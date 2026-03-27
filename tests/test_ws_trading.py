"""Tests for Phase 6 — trading methods on KrakenWSClient."""
import asyncio
import json
from unittest.mock import MagicMock, patch

import pytest

from kraken_connector.ws.client import KrakenWSClient, TradingError
from kraken_connector.ws.envelopes import WSResponse
from kraken_connector.ws.token import TokenManager
from kraken_connector.ws.trading import (
    AddOrderParams,
    AmendOrderParams,
    BatchAddParams,
    BatchCancelParams,
    CancelAllOrdersAfterParams,
    CancelAllParams,
    CancelOrderParams,
    EditOrderParams,
)

from .ws_helpers import (
    MockWebSocket,
    async_return,
    heartbeat_json,
    trading_response_json,
)


def _mock_token_manager(token: str = "test-token") -> TokenManager:  # noqa: S107
    tm = TokenManager(auth_client=MagicMock())
    tm._token = token
    tm._expires_at = float("inf")
    return tm


# ---------------------------------------------------------------------------
# TestTradingHelper
# ---------------------------------------------------------------------------


class TestTradingHelper:
    def test_send_trading_request_success(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(req_id, "add_order", {"order_id": "O1"})
                )

                params = AddOrderParams(
                    symbol="BTC/USD",
                    side="buy",
                    order_type="limit",
                    order_qty=1.0,
                    token="t",  # noqa: S106
                    limit_price=26000.0,
                )
                resp = await client.add_order(params)
                assert isinstance(resp, WSResponse)
                assert resp.result["order_id"] == "O1"

                await client.disconnect()

        asyncio.run(_run())

    def test_send_trading_request_error_raises(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(
                        req_id, "add_order", success=False, error="Insufficient funds"
                    )
                )

                params = AddOrderParams(
                    symbol="BTC/USD",
                    side="buy",
                    order_type="limit",
                    order_qty=1.0,
                    token="t",  # noqa: S106
                    limit_price=26000.0,
                )
                with pytest.raises(TradingError, match="Insufficient funds"):
                    await client.add_order(params)

                await client.disconnect()

        asyncio.run(_run())

    def test_send_trading_request_timeout(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0, request_timeout=0.1)
                await client.connect()

                # No response queued — should timeout.
                params = CancelAllParams(token="t")  # noqa: S106
                with pytest.raises(asyncio.TimeoutError):
                    await client.cancel_all(params)

                await client.disconnect()

        asyncio.run(_run())

    def test_send_trading_request_auto_injects_token(self) -> None:
        async def _run() -> None:
            tm = _mock_token_manager("injected")
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0, token_manager=tm)
                await client.connect()

                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(req_id, "cancel_all", {"count": 0})
                )

                # CancelAllParams has token="" by default, but it's in the dict.
                # Use _send_trading_request directly with no token in params.
                resp = await client._send_trading_request("cancel_all", {})
                assert isinstance(resp, WSResponse)

                # Verify the sent request includes the injected token.
                sent = [json.loads(s) for s in mock_ws.sent]
                trading_reqs = [s for s in sent if s.get("method") == "cancel_all"]
                assert len(trading_reqs) == 1
                assert trading_reqs[0]["params"]["token"] == "injected"  # noqa: S105

                await client.disconnect()

        asyncio.run(_run())

    def test_send_trading_request_no_injection_without_manager(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(req_id, "cancel_all", {"count": 0})
                )

                params = CancelAllParams(token="manual")  # noqa: S106
                resp = await client.cancel_all(params)
                assert isinstance(resp, WSResponse)

                sent = [json.loads(s) for s in mock_ws.sent]
                trading_reqs = [s for s in sent if s.get("method") == "cancel_all"]
                assert trading_reqs[0]["params"]["token"] == "manual"  # noqa: S105

                await client.disconnect()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# Method-specific tests
# ---------------------------------------------------------------------------


class TestAddOrder:
    def test_sends_correct_method(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(req_id, "add_order", {"order_id": "O1"})
                )

                params = AddOrderParams(
                    symbol="BTC/USD",
                    side="buy",
                    order_type="market",
                    order_qty=0.1,
                    token="t",  # noqa: S106
                )
                await client.add_order(params)

                sent = [json.loads(s) for s in mock_ws.sent]
                assert any(s.get("method") == "add_order" for s in sent)
                await client.disconnect()

        asyncio.run(_run())

    def test_when_disconnected_raises(self) -> None:
        async def _run() -> None:
            client = KrakenWSClient(max_reconnect_attempts=0)
            params = AddOrderParams(
                symbol="BTC/USD",
                side="buy",
                order_type="market",
                order_qty=0.1,
                token="t",  # noqa: S106
            )
            with pytest.raises(RuntimeError, match="Cannot send"):
                await client.add_order(params)

        asyncio.run(_run())


class TestAmendOrder:
    def test_sends_correct_method(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(
                        req_id, "amend_order", {"order_id": "O1", "amend_id": "A1"}
                    )
                )

                params = AmendOrderParams(
                    order_id="O1",
                    token="t",  # noqa: S106
                    limit_price=27000.0,
                )
                await client.amend_order(params)

                sent = [json.loads(s) for s in mock_ws.sent]
                assert any(s.get("method") == "amend_order" for s in sent)
                await client.disconnect()

        asyncio.run(_run())


class TestEditOrder:
    def test_sends_correct_method(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(
                        req_id,
                        "edit_order",
                        {"order_id": "O2", "original_order_id": "O1"},
                    )
                )

                params = EditOrderParams(
                    order_id="O1",
                    symbol="BTC/USD",
                    token="t",  # noqa: S106
                    order_qty=2.0,
                )
                await client.edit_order(params)

                sent = [json.loads(s) for s in mock_ws.sent]
                assert any(s.get("method") == "edit_order" for s in sent)
                await client.disconnect()

        asyncio.run(_run())


class TestCancelOrder:
    def test_sends_correct_method(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(req_id, "cancel_order", {"order_id": "O1"})
                )

                params = CancelOrderParams(token="t", order_id=["O1"])  # noqa: S106
                await client.cancel_order(params)

                sent = [json.loads(s) for s in mock_ws.sent]
                assert any(s.get("method") == "cancel_order" for s in sent)
                await client.disconnect()

        asyncio.run(_run())


class TestCancelAll:
    def test_sends_correct_method(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(req_id, "cancel_all", {"count": 3})
                )

                params = CancelAllParams(token="t")  # noqa: S106
                await client.cancel_all(params)

                sent = [json.loads(s) for s in mock_ws.sent]
                assert any(s.get("method") == "cancel_all" for s in sent)
                await client.disconnect()

        asyncio.run(_run())


class TestCancelAllOrdersAfter:
    def test_sends_correct_method(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(
                        req_id,
                        "cancel_all_orders_after",
                        {
                            "currentTime": "2024-01-01T00:00:00Z",
                            "triggerTime": "2024-01-01T00:01:00Z",
                        },
                    )
                )

                params = CancelAllOrdersAfterParams(token="t", timeout=60)  # noqa: S106
                await client.cancel_all_orders_after(params)

                sent = [json.loads(s) for s in mock_ws.sent]
                assert any(s.get("method") == "cancel_all_orders_after" for s in sent)
                await client.disconnect()

        asyncio.run(_run())

    def test_disable(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(
                        req_id,
                        "cancel_all_orders_after",
                        {
                            "currentTime": "2024-01-01T00:00:00Z",
                            "triggerTime": "2024-01-01T00:00:00Z",
                        },
                    )
                )

                params = CancelAllOrdersAfterParams(token="t", timeout=0)  # noqa: S106
                await client.cancel_all_orders_after(params)

                sent = [json.loads(s) for s in mock_ws.sent]
                reqs = [s for s in sent if s.get("method") == "cancel_all_orders_after"]
                assert reqs[0]["params"]["timeout"] == 0
                await client.disconnect()

        asyncio.run(_run())


class TestBatchAdd:
    def test_sends_correct_method(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(req_id, "batch_add", {"orders": []})
                )

                params = BatchAddParams(
                    symbol="BTC/USD",
                    token="t",  # noqa: S106
                    orders=[
                        AddOrderParams(
                            symbol="BTC/USD",
                            side="buy",
                            order_type="limit",
                            order_qty=0.1,
                            token="t",  # noqa: S106
                            limit_price=26000.0,
                        ),
                    ],
                )
                await client.batch_add(params)

                sent = [json.loads(s) for s in mock_ws.sent]
                assert any(s.get("method") == "batch_add" for s in sent)
                await client.disconnect()

        asyncio.run(_run())


class TestBatchCancel:
    def test_sends_correct_method(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    trading_response_json(req_id, "batch_cancel", {"count": 2})
                )

                params = BatchCancelParams(
                    token="t",  # noqa: S106
                    orders=["O1", "O2"],
                )
                await client.batch_cancel(params)

                sent = [json.loads(s) for s in mock_ws.sent]
                assert any(s.get("method") == "batch_cancel" for s in sent)
                await client.disconnect()

        asyncio.run(_run())
