"""Shared test helpers for WebSocket client tests."""
import asyncio
import json
from typing import Any

from websockets.exceptions import ConnectionClosedOK
from websockets.frames import Close

# ---------------------------------------------------------------------------
# JSON message factories
# ---------------------------------------------------------------------------


def status_json(
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


def heartbeat_json() -> str:
    return json.dumps({"channel": "heartbeat"})


def pong_json(req_id: int = 1) -> str:
    return json.dumps(
        {
            "method": "pong",
            "req_id": req_id,
            "time_in": "2024-01-01T00:00:00Z",
            "time_out": "2024-01-01T00:00:00Z",
        }
    )


def ticker_json() -> str:
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


def subscribe_response_json(
    req_id: int,
    channel: str = "ticker",
    symbol: str = "BTC/USD",
    success: bool = True,
    error: str | None = None,
) -> str:
    if success:
        return json.dumps(
            {
                "method": "subscribe",
                "result": {"channel": channel, "symbol": symbol},
                "success": True,
                "time_in": "2024-01-01T00:00:00Z",
                "time_out": "2024-01-01T00:00:00Z",
                "req_id": req_id,
            }
        )
    return json.dumps(
        {
            "method": "subscribe",
            "error": error or "Subscription failed",
            "success": False,
            "time_in": "2024-01-01T00:00:00Z",
            "time_out": "2024-01-01T00:00:00Z",
            "req_id": req_id,
        }
    )


def unsubscribe_response_json(
    req_id: int,
    channel: str = "ticker",
    symbol: str = "BTC/USD",
    success: bool = True,
    error: str | None = None,
) -> str:
    if success:
        return json.dumps(
            {
                "method": "unsubscribe",
                "result": {"channel": channel, "symbol": symbol},
                "success": True,
                "time_in": "2024-01-01T00:00:00Z",
                "time_out": "2024-01-01T00:00:00Z",
                "req_id": req_id,
            }
        )
    return json.dumps(
        {
            "method": "unsubscribe",
            "error": error or "Unsubscribe failed",
            "success": False,
            "time_in": "2024-01-01T00:00:00Z",
            "time_out": "2024-01-01T00:00:00Z",
            "req_id": req_id,
        }
    )


# ---------------------------------------------------------------------------
# Mock WebSocket
# ---------------------------------------------------------------------------


class MockWebSocket:
    """Mock WebSocket connection for testing."""

    def __init__(self, messages: list[str] | None = None) -> None:
        self._messages: list[str] = messages or []
        self._index = 0
        self.sent: list[str] = []
        self.closed = False
        self._close_after: int | None = None
        self._new_message_event = asyncio.Event()

    def add_message(self, msg: str) -> None:
        """Add a message to the queue (can be called after construction)."""
        self._messages.append(msg)
        self._new_message_event.set()

    async def recv(self) -> str:
        while True:
            if self.closed:
                raise ConnectionClosedOK(Close(1000, "closed"), None)
            if self._close_after is not None and self._index >= self._close_after:
                self.closed = True
                raise ConnectionClosedOK(Close(1000, "closed"), None)
            if self._index < len(self._messages):
                msg = self._messages[self._index]
                self._index += 1
                return msg
            # Wait until a new message is added.
            self._new_message_event.clear()
            await self._new_message_event.wait()

    async def send(self, data: str) -> None:
        if self.closed:
            raise ConnectionClosedOK(Close(1000, "closed"), None)
        self.sent.append(data)

    async def close(self) -> None:
        self.closed = True
        self._new_message_event.set()  # Unblock recv if waiting.


# ---------------------------------------------------------------------------
# Async helper
# ---------------------------------------------------------------------------


def async_return(value: Any) -> Any:
    """Create an awaitable that returns value (for patching async functions)."""
    future: asyncio.Future[Any] = asyncio.get_event_loop().create_future()
    future.set_result(value)
    return future
