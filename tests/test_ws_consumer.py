"""Tests for Phase 7 — consumer API (async iterator) and full-stack integration."""
import asyncio
import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

from kraken_connector.ws.book import OrderBook
from kraken_connector.ws.channels.book import BookData, BookLevel
from kraken_connector.ws.client import KrakenWSClient
from kraken_connector.ws.envelopes import WSDataMessage, WSResponse
from kraken_connector.ws.token import TokenManager
from kraken_connector.ws.trading import (
    AddOrderParams,
    CancelAllOrdersAfterParams,
    CancelOrderParams,
)

from .ws_helpers import (
    MockWebSocket,
    async_return,
    book_snapshot_json,
    book_update_json,
    executions_json,
    heartbeat_json,
    subscribe_response_json,
    ticker_json,
    trading_response_json,
    unsubscribe_response_json,
)


def _mock_token_manager(token: str = "test-token") -> TokenManager:  # noqa: S107
    tm = TokenManager(auth_client=MagicMock())
    tm._token = token
    tm._expires_at = float("inf")
    return tm


# ---------------------------------------------------------------------------
# TestAsyncIterator
# ---------------------------------------------------------------------------


class TestAsyncIterator:
    def test_async_for_receives_messages(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket(
                [
                    heartbeat_json(),
                    ticker_json(),
                    ticker_json(),
                    ticker_json(),
                ]
            )
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                messages = []
                count = 0
                async for msg in client:
                    messages.append(msg)
                    count += 1
                    if count >= 3:
                        break

                assert len(messages) == 3
                assert all(isinstance(m, WSDataMessage) for m in messages)

                await client.disconnect()

        asyncio.run(_run())

    def test_async_for_stops_on_disconnect(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json(), ticker_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # Receive the one data message.
                msg = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg, WSDataMessage)

                # Disconnect — iterator should stop.
                await client.disconnect()

                messages = []
                async for m in client:
                    messages.append(m)
                assert messages == []

        asyncio.run(_run())

    def test_async_for_empty_queue_disconnected(self) -> None:
        async def _run() -> None:
            client = KrakenWSClient(max_reconnect_attempts=0)
            # Never connected — immediately stops.
            messages = []
            async for m in client:
                messages.append(m)
            assert messages == []

        asyncio.run(_run())

    def test_async_for_drains_remaining_after_disconnect(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json(), ticker_json(), ticker_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # Let recv_loop process messages.
                await asyncio.sleep(0.1)

                # Disconnect while messages are in queue.
                await client.disconnect()

                messages = []
                async for m in client:
                    messages.append(m)

                # Should have drained the remaining data messages.
                assert len(messages) >= 1
                assert all(isinstance(m, WSDataMessage) for m in messages)

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# TestFullStack
# ---------------------------------------------------------------------------


class TestFullStack:
    def test_public_subscribe_receive_unsubscribe(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                from kraken_connector.ws.subscribe import TickerParams

                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # Subscribe.
                sub_req_id = client._sub_req_counter + 1
                mock_ws.add_message(subscribe_response_json(sub_req_id))
                await client.subscribe(TickerParams(symbol=["BTC/USD"]))

                # Receive data.
                mock_ws.add_message(ticker_json())
                msg = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg, WSDataMessage)
                assert msg.channel == "ticker"

                # Unsubscribe.
                unsub_req_id = client._sub_req_counter + 1
                mock_ws.add_message(unsubscribe_response_json(unsub_req_id))
                await client.unsubscribe(TickerParams(symbol=["BTC/USD"]))

                assert len(client.subscriptions) == 0
                await client.disconnect()

        asyncio.run(_run())

    def test_private_subscribe_with_token_manager(self) -> None:
        async def _run() -> None:
            tm = _mock_token_manager("ws-token")
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                from kraken_connector.ws.subscribe import ExecutionsParams

                client = KrakenWSClient(max_reconnect_attempts=0, token_manager=tm)
                await client.connect()

                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    subscribe_response_json(req_id, channel="executions")
                )
                await client.subscribe(ExecutionsParams())

                # Receive executions data with sequence.
                mock_ws.add_message(executions_json(sequence=1))
                msg = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg, WSDataMessage)
                assert msg.channel == "executions"
                assert msg.sequence == 1

                # Verify token was injected.
                sent = [json.loads(s) for s in mock_ws.sent]
                sub_reqs = [s for s in sent if s.get("method") == "subscribe"]
                assert sub_reqs[0]["params"]["token"] == "ws-token"  # noqa: S105

                await client.disconnect()

        asyncio.run(_run())

    def test_trading_add_and_cancel(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # Add order.
                add_req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(
                        add_req_id, "add_order", {"order_id": "OTEST-1"}
                    )
                )
                add_resp = await client.add_order(
                    AddOrderParams(
                        symbol="BTC/USD",
                        side="buy",
                        order_type="limit",
                        order_qty=0.1,
                        token="t",  # noqa: S106
                        limit_price=26000.0,
                    )
                )
                assert isinstance(add_resp, WSResponse)
                assert add_resp.result["order_id"] == "OTEST-1"

                # Cancel order.
                cancel_req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(
                        cancel_req_id, "cancel_order", {"order_id": "OTEST-1"}
                    )
                )
                cancel_resp = await client.cancel_order(
                    CancelOrderParams(token="t", order_id=["OTEST-1"])  # noqa: S106
                )
                assert isinstance(cancel_resp, WSResponse)

                await client.disconnect()

        asyncio.run(_run())

    def test_book_subscribe_snapshot_update_checksum(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                from kraken_connector.ws.subscribe import BookParams

                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # Subscribe.
                req_id = client._sub_req_counter + 1
                mock_ws.add_message(subscribe_response_json(req_id, channel="book"))
                await client.subscribe(BookParams(symbol=["BTC/USD"], depth=10))

                # Snapshot.
                mock_ws.add_message(
                    book_snapshot_json(
                        "BTC/USD",
                        bids=[{"price": 26000.0, "qty": 1.5}],
                        asks=[{"price": 26001.0, "qty": 2.0}],
                    )
                )
                msg = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg, WSDataMessage)

                book = client.book_manager.get("BTC/USD")
                assert book is not None
                assert book.best_bid == (Decimal("26000.0"), Decimal("1.5"))

                # Compute valid checksum for the expected state after update.
                temp = OrderBook(symbol="BTC/USD", depth=10)
                temp.apply_snapshot(
                    BookData(
                        symbol="BTC/USD",
                        bids=[BookLevel(Decimal("26000.0"), Decimal("1.5"))],
                        asks=[BookLevel(Decimal("26001.0"), Decimal("5.0"))],
                    )
                )
                valid_crc = OrderBook._compute_checksum(temp.asks[:10], temp.bids[:10])

                # Update with valid checksum.
                mock_ws.add_message(
                    book_update_json(
                        "BTC/USD",
                        asks=[{"price": 26001.0, "qty": 5.0}],
                        checksum=valid_crc,
                    )
                )
                msg2 = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg2, WSDataMessage)

                assert book.best_ask == (Decimal("26001.0"), Decimal("5.0"))

                await client.disconnect()

        asyncio.run(_run())

    def test_dead_man_switch_set_and_disable(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # Set timer.
                set_req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(
                        set_req_id,
                        "cancel_all_orders_after",
                        {
                            "currentTime": "2024-01-01T00:00:00Z",
                            "triggerTime": "2024-01-01T00:01:00Z",
                        },
                    )
                )
                resp1 = await client.cancel_all_orders_after(
                    CancelAllOrdersAfterParams(token="t", timeout=60)  # noqa: S106
                )
                assert isinstance(resp1, WSResponse)
                assert resp1.result["triggerTime"] == "2024-01-01T00:01:00Z"

                # Disable timer.
                disable_req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(
                        disable_req_id,
                        "cancel_all_orders_after",
                        {
                            "currentTime": "2024-01-01T00:00:30Z",
                            "triggerTime": "0",
                        },
                    )
                )
                resp2 = await client.cancel_all_orders_after(
                    CancelAllOrdersAfterParams(token="t", timeout=0)  # noqa: S106
                )
                assert isinstance(resp2, WSResponse)
                assert resp2.result["triggerTime"] == "0"

                await client.disconnect()

        asyncio.run(_run())
