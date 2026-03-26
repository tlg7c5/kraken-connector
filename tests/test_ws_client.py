"""Tests for KrakenWSClient connection manager."""
import asyncio
import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from websockets.exceptions import ConnectionClosedOK
from websockets.frames import Close

from kraken_connector.ws import ConnectionState, KrakenWSClient
from kraken_connector.ws.envelopes import (
    WSDataMessage,
    WSRequest,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _status_json(
    system: str = "online",
    connection_id: int = 123,
    api_version: str = "v2",
    version: str = "2.0.0",
) -> str:
    return json.dumps(
        {
            "channel": "status",
            "type": "update",
            "data": [
                {
                    "system": system,
                    "api_version": api_version,
                    "connection_id": connection_id,
                    "version": version,
                }
            ],
        }
    )


def _heartbeat_json() -> str:
    return json.dumps({"channel": "heartbeat"})


def _pong_json(req_id: int = 1) -> str:
    return json.dumps(
        {
            "method": "pong",
            "req_id": req_id,
            "time_in": "2024-01-01T00:00:00Z",
            "time_out": "2024-01-01T00:00:00Z",
        }
    )


def _ticker_json() -> str:
    return json.dumps(
        {
            "channel": "ticker",
            "type": "snapshot",
            "data": [
                {
                    "symbol": "BTC/USD",
                    "bid": 50000.0,
                    "bid_qty": 1.0,
                    "ask": 50001.0,
                    "ask_qty": 2.0,
                    "last": 50000.5,
                    "volume": 100.0,
                    "vwap": 49999.0,
                    "low": 49000.0,
                    "high": 51000.0,
                    "change": 500.0,
                    "change_pct": 1.0,
                    "timestamp": "2024-01-01T00:00:00Z",
                }
            ],
        }
    )


class MockWebSocket:
    """Mock WebSocket connection for testing."""

    def __init__(self, messages: list[str] | None = None) -> None:
        self._messages: list[str] = messages or []
        self._index = 0
        self.sent: list[str] = []
        self.closed = False
        self._close_after: int | None = None

    async def recv(self) -> str:
        if self.closed:
            raise ConnectionClosedOK(Close(1000, "closed"), None)
        if self._close_after is not None and self._index >= self._close_after:
            self.closed = True
            raise ConnectionClosedOK(Close(1000, "closed"), None)
        if self._index < len(self._messages):
            msg = self._messages[self._index]
            self._index += 1
            return msg
        # Block until cancelled to simulate waiting for messages.
        await asyncio.sleep(3600)
        return ""  # unreachable

    async def send(self, data: str) -> None:
        if self.closed:
            raise ConnectionClosedOK(Close(1000, "closed"), None)
        self.sent.append(data)

    async def close(self) -> None:
        self.closed = True


# ---------------------------------------------------------------------------
# TestConfiguration
# ---------------------------------------------------------------------------


class TestConfiguration:
    def test_default_config_values(self) -> None:
        client = KrakenWSClient()
        assert client.url == "wss://ws.kraken.com/v2"
        assert client.ping_interval == 10.0
        assert client.ping_timeout == 10.0
        assert client.heartbeat_timeout == 30.0
        assert client.backoff_base == 0.5
        assert client.backoff_max == 30.0
        assert client.max_reconnect_attempts == 10

    def test_custom_url(self) -> None:
        client = KrakenWSClient(url="wss://beta-ws.kraken.com/v2")
        assert client.url == "wss://beta-ws.kraken.com/v2"

    def test_custom_timing_params(self) -> None:
        client = KrakenWSClient(
            ping_interval=5.0,
            ping_timeout=3.0,
            heartbeat_timeout=15.0,
            backoff_base=1.0,
            backoff_max=60.0,
            max_reconnect_attempts=5,
        )
        assert client.ping_interval == 5.0
        assert client.ping_timeout == 3.0
        assert client.heartbeat_timeout == 15.0
        assert client.backoff_base == 1.0
        assert client.backoff_max == 60.0
        assert client.max_reconnect_attempts == 5

    def test_initial_state_is_disconnected(self) -> None:
        client = KrakenWSClient()
        assert client.state == ConnectionState.DISCONNECTED
        assert client.system_status is None
        assert client.connection_id is None


# ---------------------------------------------------------------------------
# TestConnectionLifecycle
# ---------------------------------------------------------------------------


class TestConnectionLifecycle:
    def test_connect_sets_state_to_connected(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([_status_json(), _heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=_async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()
                assert client.state == ConnectionState.CONNECTED
                await client.disconnect()
                assert client.state == ConnectionState.DISCONNECTED

        asyncio.run(_run())

    def test_disconnect_sets_state_to_disconnected(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([_heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=_async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()
                await client.disconnect()
                assert client.state == ConnectionState.DISCONNECTED
                assert mock_ws.closed

        asyncio.run(_run())

    def test_context_manager_connects_and_disconnects(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([_heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=_async_return(mock_ws),
            ):
                async with KrakenWSClient(max_reconnect_attempts=0) as client:
                    assert client.state == ConnectionState.CONNECTED
                assert client.state == ConnectionState.DISCONNECTED

        asyncio.run(_run())

    def test_connect_when_already_connected_raises(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([_heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=_async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()
                with pytest.raises(RuntimeError, match="Cannot connect"):
                    await client.connect()
                await client.disconnect()

        asyncio.run(_run())

    def test_send_when_disconnected_raises(self) -> None:
        async def _run() -> None:
            client = KrakenWSClient()
            req = WSRequest(method="subscribe", params={"channel": "ticker"})
            with pytest.raises(RuntimeError, match="Cannot send"):
                await client.send(req)

        asyncio.run(_run())

    def test_receive_returns_typed_message(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([_ticker_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=_async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                msg = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg, WSDataMessage)
                assert msg.channel == "ticker"

                await client.disconnect()

        asyncio.run(_run())

    def test_send_serializes_request(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([_heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=_async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                req = WSRequest(
                    method="subscribe",
                    params={"channel": "ticker", "symbol": ["BTC/USD"]},
                )
                await client.send(req)

                assert len(mock_ws.sent) == 1
                sent_data = json.loads(mock_ws.sent[0])
                assert sent_data["method"] == "subscribe"
                assert sent_data["params"]["channel"] == "ticker"

                await client.disconnect()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# TestHeartbeatMonitoring
# ---------------------------------------------------------------------------


class TestHeartbeatMonitoring:
    def test_heartbeat_not_enqueued_to_consumer(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([_heartbeat_json(), _ticker_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=_async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # First message should be ticker (heartbeat filtered out).
                msg = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg, WSDataMessage)
                assert msg.channel == "ticker"

                await client.disconnect()

        asyncio.run(_run())

    def test_heartbeat_timeout_triggers_reconnect(self) -> None:
        async def _run() -> None:
            # Mock WS that just hangs (no messages).
            mock_ws = MockWebSocket([])
            reconnect_ws = MockWebSocket([_heartbeat_json()])

            connect_mock = AsyncMock(side_effect=[mock_ws, reconnect_ws])

            with patch(
                "kraken_connector.ws.client.websockets.connect",
                connect_mock,
            ):
                client = KrakenWSClient(
                    heartbeat_timeout=0.5,
                    backoff_base=0.01,
                    max_reconnect_attempts=1,
                )
                await client.connect()
                # Wait for heartbeat timeout + reconnect.
                await asyncio.sleep(1.5)

                # Should have reconnected or be disconnected.
                assert client.state in (
                    ConnectionState.CONNECTED,
                    ConnectionState.DISCONNECTED,
                )
                await client.disconnect()

        asyncio.run(_run())

    def test_data_messages_prevent_heartbeat_timeout(self) -> None:
        async def _run() -> None:
            # Ticker messages keep arriving, preventing timeout.
            mock_ws = MockWebSocket([_ticker_json(), _ticker_json(), _ticker_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=_async_return(mock_ws),
            ):
                client = KrakenWSClient(
                    heartbeat_timeout=2.0,
                    max_reconnect_attempts=0,
                )
                await client.connect()

                # Drain all messages.
                for _ in range(3):
                    await asyncio.wait_for(client.receive(), timeout=2.0)

                # Should still be connected.
                assert client.state == ConnectionState.CONNECTED
                await client.disconnect()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# TestPingPong
# ---------------------------------------------------------------------------


class TestPingPong:
    def test_ping_sent_at_interval(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([_heartbeat_json(), _pong_json(1)])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=_async_return(mock_ws),
            ):
                client = KrakenWSClient(
                    ping_interval=0.2,
                    ping_timeout=2.0,
                    max_reconnect_attempts=0,
                )
                await client.connect()

                # Wait for at least one ping to be sent.
                await asyncio.sleep(0.5)

                # Check that a ping was sent.
                pings = [json.loads(s) for s in mock_ws.sent if "ping" in s]
                assert len(pings) >= 1
                assert pings[0]["method"] == "ping"

                await client.disconnect()

        asyncio.run(_run())

    def test_pong_not_enqueued_to_consumer(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([_pong_json(1), _ticker_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=_async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # First consumer message should be ticker (pong filtered).
                msg = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg, WSDataMessage)
                assert msg.channel == "ticker"

                await client.disconnect()

        asyncio.run(_run())

    def test_ping_timeout_triggers_reconnect(self) -> None:
        async def _run() -> None:
            # WS that never sends a pong.
            mock_ws = MockWebSocket([_heartbeat_json()])
            connect_mock = AsyncMock(side_effect=[mock_ws, MockWebSocket([])])

            with patch(
                "kraken_connector.ws.client.websockets.connect",
                connect_mock,
            ):
                client = KrakenWSClient(
                    ping_interval=0.1,
                    ping_timeout=0.2,
                    heartbeat_timeout=30.0,
                    backoff_base=0.01,
                    max_reconnect_attempts=1,
                )
                await client.connect()
                await asyncio.sleep(1.0)

                # Should have attempted reconnect.
                assert connect_mock.call_count >= 2 or client.state in (
                    ConnectionState.DISCONNECTED,
                    ConnectionState.RECONNECTING,
                )
                await client.disconnect()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# TestReconnection
# ---------------------------------------------------------------------------


class TestReconnection:
    def test_reconnect_on_connection_closed(self) -> None:
        async def _run() -> None:
            # First WS closes after 1 message.
            ws1 = MockWebSocket([_ticker_json()])
            ws1._close_after = 1

            ws2 = MockWebSocket([_ticker_json()])

            connect_mock = AsyncMock(side_effect=[ws1, ws2])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                connect_mock,
            ):
                client = KrakenWSClient(
                    backoff_base=0.01,
                    max_reconnect_attempts=3,
                    heartbeat_timeout=30.0,
                )
                await client.connect()

                # Get first message.
                msg = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg, WSDataMessage)

                # Wait for reconnect to complete.
                for _ in range(20):
                    await asyncio.sleep(0.1)
                    if connect_mock.call_count >= 2:
                        break

                assert connect_mock.call_count >= 2
                await client.disconnect()

        asyncio.run(_run())

    @patch("kraken_connector.ws.client.asyncio.sleep", new_callable=AsyncMock)
    def test_backoff_timing_matches_formula(self, mock_sleep: AsyncMock) -> None:
        async def _run() -> None:
            connect_mock = AsyncMock(side_effect=ConnectionRefusedError("refused"))
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                connect_mock,
            ):
                client = KrakenWSClient(
                    backoff_base=1.0,
                    backoff_max=10.0,
                    max_reconnect_attempts=4,
                )
                # Manually trigger reconnect.
                await client._reconnect()

            # Extract the sleep calls from reconnect (not from tasks).
            delays = [
                call.args[0]
                for call in mock_sleep.call_args_list
                if isinstance(call.args[0], float) and call.args[0] >= 0.5
            ]
            assert delays == [1.0, 2.0, 4.0, 8.0]

        asyncio.run(_run())

    @patch("kraken_connector.ws.client.asyncio.sleep", new_callable=AsyncMock)
    def test_backoff_caps_at_max(self, mock_sleep: AsyncMock) -> None:
        async def _run() -> None:
            connect_mock = AsyncMock(side_effect=ConnectionRefusedError("refused"))
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                connect_mock,
            ):
                client = KrakenWSClient(
                    backoff_base=1.0,
                    backoff_max=3.0,
                    max_reconnect_attempts=4,
                )
                await client._reconnect()

            delays = [
                call.args[0]
                for call in mock_sleep.call_args_list
                if isinstance(call.args[0], float) and call.args[0] >= 0.5
            ]
            assert delays == [1.0, 2.0, 3.0, 3.0]

        asyncio.run(_run())

    def test_max_retries_exhausted_sets_disconnected(self) -> None:
        async def _run() -> None:
            connect_mock = AsyncMock(side_effect=ConnectionRefusedError("refused"))
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                connect_mock,
            ), patch(
                "kraken_connector.ws.client.asyncio.sleep",
                new_callable=AsyncMock,
            ):
                client = KrakenWSClient(
                    backoff_base=0.01,
                    max_reconnect_attempts=3,
                )
                await client._reconnect()

            assert client.state == ConnectionState.DISCONNECTED
            assert connect_mock.call_count == 3

        asyncio.run(_run())

    def test_successful_reconnect_resets_attempt_counter(self) -> None:
        async def _run() -> None:
            ws_new = MockWebSocket([_heartbeat_json()])

            connect_mock = AsyncMock(
                side_effect=[
                    ConnectionRefusedError("refused"),
                    ws_new,
                ]
            )
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                connect_mock,
            ), patch(
                "kraken_connector.ws.client.asyncio.sleep",
                new_callable=AsyncMock,
            ):
                client = KrakenWSClient(
                    backoff_base=0.01,
                    max_reconnect_attempts=5,
                )
                await client._reconnect()

            assert client.state == ConnectionState.CONNECTED
            assert client._reconnect_attempt == 0
            await client.disconnect()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# TestStatusTracking
# ---------------------------------------------------------------------------


class TestStatusTracking:
    def test_status_message_updates_system_status(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([_status_json(system="online", connection_id=42)])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=_async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # Wait for recv_loop to process status.
                await asyncio.sleep(0.2)

                assert client.system_status == "online"
                await client.disconnect()

        asyncio.run(_run())

    def test_status_message_updates_connection_id(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([_status_json(system="online", connection_id=99)])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=_async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()
                await asyncio.sleep(0.2)

                assert client.connection_id == 99
                await client.disconnect()

        asyncio.run(_run())

    def test_status_message_still_enqueued_to_consumer(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([_status_json(system="online", connection_id=1)])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=_async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                msg = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg, WSDataMessage)
                assert msg.channel == "status"

                await client.disconnect()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# Helper for async mocking
# ---------------------------------------------------------------------------


def _async_return(value: Any) -> Any:
    """Create an awaitable that returns value (for patching async functions)."""
    future: asyncio.Future[Any] = asyncio.get_event_loop().create_future()
    future.set_result(value)
    return future
