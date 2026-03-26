"""Async WebSocket connection manager for Kraken WS v2."""
import asyncio
import contextlib
import json
import logging
import time
from typing import Any

import websockets
from websockets.exceptions import ConnectionClosed

from ..types import Unset
from .book import OrderBookManager
from .channels.heartbeat import HeartbeatMessage
from .channels.status import StatusData
from .constants import ConnectionState
from .dispatcher import WSMessage, parse_message
from .envelopes import (
    PingRequest,
    PongResponse,
    WSDataMessage,
    WSErrorResponse,
    WSRequest,
    WSResponse,
)
from .sequence import SequenceTracker
from .subscribe import BalancesParams, ExecutionsParams
from .subscriptions import (
    SubscriptionEntry,
    SubscriptionError,
    SubscriptionParams,
    _make_sub_key,
)
from .token import TokenManager

_logger = logging.getLogger("kraken_connector.ws")


class KrakenWSClient:
    """Async WebSocket client for Kraken WS v2.

    Manages a single WebSocket connection with heartbeat monitoring,
    client-initiated pings, automatic reconnection, and system status
    tracking.

    Usage::

        async with KrakenWSClient() as client:
            msg = await client.receive()

    Args:
        url: WebSocket endpoint URL.
        ping_interval: Seconds between client pings.
        ping_timeout: Max seconds to wait for pong response.
        heartbeat_timeout: Max silence before triggering reconnect.
        backoff_base: Base delay for exponential backoff.
        backoff_max: Maximum backoff delay.
        max_reconnect_attempts: Max reconnect retries (0 = disabled).
    """

    def __init__(
        self,
        url: str = "wss://ws.kraken.com/v2",
        ping_interval: float = 10.0,
        ping_timeout: float = 10.0,
        heartbeat_timeout: float = 30.0,
        backoff_base: float = 0.5,
        backoff_max: float = 30.0,
        max_reconnect_attempts: int = 10,
        request_timeout: float = 10.0,
        token_manager: TokenManager | None = None,
    ) -> None:
        self.url = url
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.heartbeat_timeout = heartbeat_timeout
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.max_reconnect_attempts = max_reconnect_attempts
        self.request_timeout = request_timeout
        self._token_manager = token_manager

        self._state = ConnectionState.DISCONNECTED
        self._ws: Any | None = None
        self._system_status: str | None = None
        self._connection_id: int | None = None
        self._last_message_time: float = 0.0
        self._reconnect_attempt: int = 0
        self._ping_counter: int = 0
        self._pong_event: asyncio.Event = asyncio.Event()
        self._stop_event: asyncio.Event = asyncio.Event()
        self._message_queue: asyncio.Queue[WSMessage] = asyncio.Queue()
        self._tasks: list[asyncio.Task[None]] = []

        # Subscription tracking
        self._sub_req_counter: int = 1_000_000
        self._subscriptions: dict[tuple[tuple[str, Any], ...], SubscriptionEntry] = {}
        self._pending_requests: dict[
            int, asyncio.Future[WSResponse | WSErrorResponse]
        ] = {}

        # Sequence tracking for private channels
        self._sequence_tracker: SequenceTracker = SequenceTracker()

        # Book state management
        self._book_manager: OrderBookManager = OrderBookManager()

    @property
    def state(self) -> ConnectionState:
        """Current connection state (read-only)."""
        return self._state

    @property
    def system_status(self) -> str | None:
        """Latest system status from the status channel."""
        return self._system_status

    @property
    def connection_id(self) -> int | None:
        """Connection ID from the status channel."""
        return self._connection_id

    @property
    def book_manager(self) -> OrderBookManager:
        """Access the order book manager for reading book state."""
        return self._book_manager

    @property
    def subscriptions(
        self,
    ) -> dict[tuple[tuple[str, Any], ...], SubscriptionEntry]:
        """Currently tracked subscriptions (read-only copy)."""
        return dict(self._subscriptions)

    async def connect(self) -> None:
        """Open the WebSocket connection and start background tasks.

        Raises:
            RuntimeError: If already connected or connecting.
        """
        if self._state not in (
            ConnectionState.DISCONNECTED,
            ConnectionState.RECONNECTING,
        ):
            raise RuntimeError(f"Cannot connect: state is {self._state.value}")

        self._stop_event.clear()
        self._state = ConnectionState.CONNECTING
        _logger.info("Connecting to %s", self.url)

        self._ws = await websockets.connect(self.url)
        self._state = ConnectionState.CONNECTED
        self._last_message_time = time.monotonic()
        self._reconnect_attempt = 0
        _logger.info("Connected to %s", self.url)

        self._start_tasks()

    async def disconnect(self) -> None:
        """Cleanly shut down the connection and background tasks."""
        self._stop_event.set()
        self._cancel_tasks()
        self._fail_pending_requests("disconnected")

        if self._ws is not None:
            with contextlib.suppress(Exception):
                await self._ws.close()
            self._ws = None

        self._state = ConnectionState.DISCONNECTED
        _logger.info("Disconnected")

    async def send(self, msg: WSRequest) -> None:
        """Serialize and send a request message.

        Args:
            msg: The request envelope to send.

        Raises:
            RuntimeError: If not connected.
        """
        if self._state != ConnectionState.CONNECTED or self._ws is None:
            raise RuntimeError(f"Cannot send: state is {self._state.value}")
        payload = json.dumps(msg.to_dict())
        await self._ws.send(payload)

    async def receive(self) -> WSMessage:
        """Get the next typed message from the queue.

        Blocks until a message is available.
        """
        return await self._message_queue.get()

    async def subscribe(self, params: SubscriptionParams) -> WSResponse:
        """Subscribe to a channel.

        Args:
            params: Typed subscription parameters.

        Returns:
            The server's success response.

        Raises:
            SubscriptionError: If the server rejects the subscription.
            asyncio.TimeoutError: If no response within request_timeout.
            RuntimeError: If not connected.
        """
        if self._state != ConnectionState.CONNECTED or self._ws is None:
            raise RuntimeError(f"Cannot subscribe: state is {self._state.value}")

        # Inject token for private channels.
        if self._token_manager is not None and isinstance(
            params, (ExecutionsParams, BalancesParams)
        ):
            import attrs

            token = await self._token_manager.get_token()
            params = attrs.evolve(params, token=token)

        self._sub_req_counter += 1
        req_id = self._sub_req_counter

        future: asyncio.Future[
            WSResponse | WSErrorResponse
        ] = asyncio.get_event_loop().create_future()
        self._pending_requests[req_id] = future

        request = WSRequest(
            method="subscribe",
            params=params.to_dict(),
            req_id=req_id,
        )
        await self._ws.send(json.dumps(request.to_dict()))

        try:
            response = await asyncio.wait_for(future, timeout=self.request_timeout)
        except asyncio.TimeoutError:
            self._pending_requests.pop(req_id, None)
            raise

        if isinstance(response, WSErrorResponse):
            raise SubscriptionError(response.error, req_id=req_id)

        # Track the subscription.
        key = _make_sub_key(params)
        self._subscriptions[key] = SubscriptionEntry(
            params=params, req_id=req_id, confirmed=True
        )
        return response

    async def unsubscribe(self, params: SubscriptionParams) -> WSResponse:
        """Unsubscribe from a channel.

        Args:
            params: Typed subscription parameters (must match a tracked sub).

        Returns:
            The server's success response.

        Raises:
            KeyError: If no matching subscription is tracked.
            SubscriptionError: If the server rejects the unsubscribe.
            asyncio.TimeoutError: If no response within request_timeout.
            RuntimeError: If not connected.
        """
        if self._state != ConnectionState.CONNECTED or self._ws is None:
            raise RuntimeError(f"Cannot unsubscribe: state is {self._state.value}")

        key = _make_sub_key(params)
        if key not in self._subscriptions:
            raise KeyError(f"No tracked subscription for {params.channel}")

        self._sub_req_counter += 1
        req_id = self._sub_req_counter

        future: asyncio.Future[
            WSResponse | WSErrorResponse
        ] = asyncio.get_event_loop().create_future()
        self._pending_requests[req_id] = future

        request = WSRequest(
            method="unsubscribe",
            params=params.to_dict(),
            req_id=req_id,
        )
        await self._ws.send(json.dumps(request.to_dict()))

        try:
            response = await asyncio.wait_for(future, timeout=self.request_timeout)
        except asyncio.TimeoutError:
            self._pending_requests.pop(req_id, None)
            raise

        if isinstance(response, WSErrorResponse):
            raise SubscriptionError(response.error, req_id=req_id)

        self._subscriptions.pop(key, None)
        return response

    async def __aenter__(self) -> "KrakenWSClient":
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        await self.disconnect()

    # ------------------------------------------------------------------
    # Internal tasks
    # ------------------------------------------------------------------

    def _start_tasks(self) -> None:
        """Spawn the background recv, ping, and heartbeat monitor tasks."""
        self._tasks = [
            asyncio.create_task(self._recv_loop()),
            asyncio.create_task(self._ping_loop()),
            asyncio.create_task(self._heartbeat_monitor()),
        ]

    def _cancel_tasks(self) -> None:
        """Cancel all background tasks and clear the list."""
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()

    async def _recv_loop(self) -> None:
        """Receive messages, parse them, and route to queue or internal handlers."""
        try:
            while not self._stop_event.is_set():
                if self._ws is None:
                    return
                raw = await self._ws.recv()
                self._last_message_time = time.monotonic()

                msg = parse_message(str(raw))

                # Sequence tracking for private channels.
                if isinstance(msg, WSDataMessage) and not isinstance(
                    msg.sequence, Unset
                ):
                    gap = self._sequence_tracker.check(msg.sequence, msg.channel)
                    if gap is not None:
                        _logger.warning(
                            "Sequence gap on %s: expected %d, got %d",
                            gap.channel,
                            gap.expected,
                            gap.received,
                        )
                        await self._message_queue.put(gap)

                # Apply book data to the book manager.
                if isinstance(msg, WSDataMessage) and msg.channel == "book":
                    checksum_event = self._book_manager.process_message(msg)
                    if checksum_event is not None:
                        _logger.warning(
                            "Book checksum mismatch for %s: expected %d, computed %d",
                            checksum_event.symbol,
                            checksum_event.expected,
                            checksum_event.computed,
                        )
                        await self._message_queue.put(checksum_event)

                # Intercept status messages to update internal state.
                if isinstance(msg, WSDataMessage) and msg.channel == "status":
                    self._handle_status(msg)

                # Intercept pong responses — signal the ping task, don't enqueue.
                if isinstance(msg, PongResponse):
                    self._pong_event.set()
                    continue

                # Don't enqueue heartbeats — they're transport-level.
                if isinstance(msg, HeartbeatMessage):
                    continue

                # Correlate subscribe/unsubscribe responses by req_id.
                if isinstance(msg, (WSResponse, WSErrorResponse)):
                    req_id = msg.req_id
                    if (
                        not isinstance(req_id, Unset)
                        and req_id in self._pending_requests
                    ):
                        future = self._pending_requests.pop(req_id)
                        if not future.done():
                            future.set_result(msg)
                        continue

                await self._message_queue.put(msg)

        except ConnectionClosed:
            if not self._stop_event.is_set():
                _logger.warning("Connection closed unexpectedly")
                self._trigger_reconnect("connection closed")
        except asyncio.CancelledError:
            return

    async def _ping_loop(self) -> None:
        """Send periodic pings and wait for pong responses."""
        try:
            while not self._stop_event.is_set():
                await asyncio.sleep(self.ping_interval)

                if self._stop_event.is_set() or self._ws is None:
                    return

                self._ping_counter += 1
                ping = PingRequest(req_id=self._ping_counter)
                self._pong_event.clear()

                try:
                    await self._ws.send(json.dumps(ping.to_dict()))
                except ConnectionClosed:
                    if not self._stop_event.is_set():
                        self._trigger_reconnect("ping send failed")
                    return

                try:
                    await asyncio.wait_for(
                        self._pong_event.wait(),
                        timeout=self.ping_timeout,
                    )
                except asyncio.TimeoutError:
                    if not self._stop_event.is_set():
                        _logger.warning("Pong timeout after %.1fs", self.ping_timeout)
                        self._trigger_reconnect("pong timeout")
                    return

        except asyncio.CancelledError:
            return

    async def _heartbeat_monitor(self) -> None:
        """Monitor for server silence beyond heartbeat_timeout."""
        try:
            while not self._stop_event.is_set():
                await asyncio.sleep(1.0)

                if self._stop_event.is_set():
                    return

                elapsed = time.monotonic() - self._last_message_time
                if elapsed > self.heartbeat_timeout:
                    _logger.warning(
                        "Heartbeat timeout: %.1fs since last message",
                        elapsed,
                    )
                    self._trigger_reconnect("heartbeat timeout")
                    return

        except asyncio.CancelledError:
            return

    # ------------------------------------------------------------------
    # Reconnection
    # ------------------------------------------------------------------

    def _trigger_reconnect(self, reason: str) -> None:
        """Initiate reconnection if auto-reconnect is enabled.

        Spawns reconnect as an independent task so the calling task
        (recv_loop, ping_loop, etc.) can be safely cancelled.
        """
        if self._stop_event.is_set():
            return

        if self.max_reconnect_attempts <= 0:
            _logger.error("Connection lost (%s), auto-reconnect disabled", reason)
            self._state = ConnectionState.DISCONNECTED
            return

        _logger.warning("Triggering reconnect: %s", reason)
        self._cancel_tasks()
        asyncio.create_task(self._reconnect())

    async def _reconnect(self) -> None:
        """Attempt to reconnect with exponential backoff."""
        self._state = ConnectionState.RECONNECTING
        self._fail_pending_requests("reconnecting")

        if self._ws is not None:
            with contextlib.suppress(Exception):
                await self._ws.close()
            self._ws = None

        for attempt in range(self.max_reconnect_attempts):
            self._reconnect_attempt = attempt
            delay = min(
                self.backoff_base * (2**attempt),
                self.backoff_max,
            )
            _logger.warning(
                "Reconnect %d/%d after %.2fs",
                attempt + 1,
                self.max_reconnect_attempts,
                delay,
            )
            await asyncio.sleep(delay)

            if self._stop_event.is_set():
                break

            try:
                self._state = ConnectionState.CONNECTING
                self._ws = await websockets.connect(self.url)
                self._state = ConnectionState.CONNECTED
                self._last_message_time = time.monotonic()
                self._reconnect_attempt = 0
                self._start_tasks()
                _logger.info("Reconnected successfully")
                asyncio.create_task(self._resubscribe_all())
                return
            except Exception as exc:
                _logger.warning(
                    "Reconnect attempt %d failed: %s",
                    attempt + 1,
                    exc,
                )

        # Exhausted retries.
        self._state = ConnectionState.DISCONNECTED
        _logger.error(
            "Max reconnect attempts (%d) reached", self.max_reconnect_attempts
        )

    # ------------------------------------------------------------------
    # Pending request management
    # ------------------------------------------------------------------

    def _fail_pending_requests(self, reason: str) -> None:
        """Reject all in-flight request futures with ConnectionError."""
        for future in self._pending_requests.values():
            if not future.done():
                future.set_exception(ConnectionError(reason))
        self._pending_requests.clear()

    # ------------------------------------------------------------------
    # Re-subscription
    # ------------------------------------------------------------------

    async def _resubscribe_all(self) -> None:
        """Re-subscribe to all tracked subscriptions after reconnect."""
        if self._token_manager is not None:
            self._token_manager.invalidate()
        self._sequence_tracker.reset()
        self._book_manager.clear()

        if not self._subscriptions:
            return
        _logger.info("Re-subscribing to %d channels", len(self._subscriptions))
        entries = list(self._subscriptions.values())
        for entry in entries:
            entry.confirmed = False
        for entry in entries:
            try:
                await self.subscribe(entry.params)
            except (SubscriptionError, asyncio.TimeoutError) as exc:
                _logger.error(
                    "Re-subscribe failed for %s: %s", entry.params.channel, exc
                )
                key = _make_sub_key(entry.params)
                self._subscriptions.pop(key, None)

    # ------------------------------------------------------------------
    # Status tracking
    # ------------------------------------------------------------------

    def _handle_status(self, msg: WSDataMessage) -> None:
        """Extract system status and connection ID from status channel data."""
        if msg.data and isinstance(msg.data[0], StatusData):
            status: StatusData = msg.data[0]
            self._system_status = status.system
            self._connection_id = status.connection_id
            _logger.info(
                "System status: %s (connection %d)",
                status.system,
                status.connection_id,
            )

    def _next_ping_id(self) -> int:
        """Return the next ping req_id."""
        self._ping_counter += 1
        return self._ping_counter
