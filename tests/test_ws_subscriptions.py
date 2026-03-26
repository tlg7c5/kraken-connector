"""Tests for Phase 3 — Subscription lifecycle on KrakenWSClient."""
import asyncio
import json
from unittest.mock import AsyncMock, patch

import pytest

from kraken_connector.ws import (
    ConnectionState,
    KrakenWSClient,
    SubscriptionEntry,
    SubscriptionError,
)
from kraken_connector.ws.envelopes import WSDataMessage, WSResponse
from kraken_connector.ws.subscribe import BookParams, ExecutionsParams, TickerParams
from kraken_connector.ws.subscriptions import _make_sub_key

from .ws_helpers import (
    MockWebSocket,
    async_return,
    heartbeat_json,
    subscribe_response_json,
    ticker_json,
    unsubscribe_response_json,
)

# ---------------------------------------------------------------------------
# TestSubscriptionKey
# ---------------------------------------------------------------------------


class TestSubscriptionKey:
    def test_same_params_produce_same_key(self) -> None:
        a = TickerParams(symbol=["BTC/USD"])
        b = TickerParams(symbol=["BTC/USD"])
        assert _make_sub_key(a) == _make_sub_key(b)

    def test_different_params_produce_different_key(self) -> None:
        a = BookParams(symbol=["BTC/USD"], depth=10)
        b = BookParams(symbol=["BTC/USD"], depth=100)
        assert _make_sub_key(a) != _make_sub_key(b)

    def test_key_with_list_symbols(self) -> None:
        a = TickerParams(symbol=["BTC/USD", "ETH/USD"])
        b = TickerParams(symbol=["BTC/USD", "ETH/USD"])
        assert _make_sub_key(a) == _make_sub_key(b)

    def test_key_excludes_token(self) -> None:
        a = ExecutionsParams(token="token_a")  # noqa: S106
        b = ExecutionsParams(token="token_b")  # noqa: S106
        assert _make_sub_key(a) == _make_sub_key(b)


# ---------------------------------------------------------------------------
# TestSubscribe
# ---------------------------------------------------------------------------


class TestSubscribe:
    def test_subscribe_sends_request_with_req_id(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                params = TickerParams(symbol=["BTC/USD"])

                # Queue the subscribe response before calling subscribe.
                req_id = client._sub_req_counter + 1
                mock_ws.add_message(subscribe_response_json(req_id))

                await client.subscribe(params)

                # Verify a subscribe request was sent.
                sent = [json.loads(s) for s in mock_ws.sent]
                sub_requests = [s for s in sent if s.get("method") == "subscribe"]
                assert len(sub_requests) == 1
                assert sub_requests[0]["req_id"] == req_id
                assert sub_requests[0]["params"]["channel"] == "ticker"

                await client.disconnect()

        asyncio.run(_run())

    def test_subscribe_returns_response_on_success(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                params = TickerParams(symbol=["BTC/USD"])
                req_id = client._sub_req_counter + 1
                mock_ws.add_message(subscribe_response_json(req_id))

                response = await client.subscribe(params)
                assert isinstance(response, WSResponse)
                assert response.method == "subscribe"
                assert response.success is True

                await client.disconnect()

        asyncio.run(_run())

    def test_subscribe_raises_on_server_error(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                params = TickerParams(symbol=["INVALID/PAIR"])
                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    subscribe_response_json(
                        req_id, success=False, error="Currency pair not supported"
                    )
                )

                with pytest.raises(
                    SubscriptionError, match="Currency pair not supported"
                ):
                    await client.subscribe(params)

                await client.disconnect()

        asyncio.run(_run())

    def test_subscribe_timeout_raises(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0, request_timeout=0.1)
                await client.connect()

                params = TickerParams(symbol=["BTC/USD"])
                # Don't add a response — should time out.

                with pytest.raises(asyncio.TimeoutError):
                    await client.subscribe(params)

                # Pending request should be cleaned up.
                assert len(client._pending_requests) == 0

                await client.disconnect()

        asyncio.run(_run())

    def test_subscribe_tracks_subscription(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                params = TickerParams(symbol=["BTC/USD"])
                req_id = client._sub_req_counter + 1
                mock_ws.add_message(subscribe_response_json(req_id))

                await client.subscribe(params)

                subs = client.subscriptions
                assert len(subs) == 1
                entry = list(subs.values())[0]
                assert isinstance(entry, SubscriptionEntry)
                assert entry.confirmed is True
                assert entry.params.channel == "ticker"

                await client.disconnect()

        asyncio.run(_run())

    def test_subscribe_not_tracked_on_failure(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                params = TickerParams(symbol=["BAD/PAIR"])
                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    subscribe_response_json(req_id, success=False, error="fail")
                )

                with pytest.raises(SubscriptionError):
                    await client.subscribe(params)

                assert len(client.subscriptions) == 0

                await client.disconnect()

        asyncio.run(_run())

    def test_subscribe_when_disconnected_raises(self) -> None:
        async def _run() -> None:
            client = KrakenWSClient()
            params = TickerParams(symbol=["BTC/USD"])
            with pytest.raises(RuntimeError, match="Cannot subscribe"):
                await client.subscribe(params)

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# TestUnsubscribe
# ---------------------------------------------------------------------------


class TestUnsubscribe:
    def test_unsubscribe_sends_request(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                params = TickerParams(symbol=["BTC/USD"])

                # Subscribe first.
                sub_req_id = client._sub_req_counter + 1
                mock_ws.add_message(subscribe_response_json(sub_req_id))
                await client.subscribe(params)

                # Unsubscribe.
                unsub_req_id = client._sub_req_counter + 1
                mock_ws.add_message(unsubscribe_response_json(unsub_req_id))
                await client.unsubscribe(params)

                sent = [json.loads(s) for s in mock_ws.sent]
                unsub_requests = [s for s in sent if s.get("method") == "unsubscribe"]
                assert len(unsub_requests) == 1
                assert unsub_requests[0]["req_id"] == unsub_req_id

                await client.disconnect()

        asyncio.run(_run())

    def test_unsubscribe_removes_tracking(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                params = TickerParams(symbol=["BTC/USD"])
                sub_req_id = client._sub_req_counter + 1
                mock_ws.add_message(subscribe_response_json(sub_req_id))
                await client.subscribe(params)
                assert len(client.subscriptions) == 1

                unsub_req_id = client._sub_req_counter + 1
                mock_ws.add_message(unsubscribe_response_json(unsub_req_id))
                await client.unsubscribe(params)
                assert len(client.subscriptions) == 0

                await client.disconnect()

        asyncio.run(_run())

    def test_unsubscribe_raises_on_server_error(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                params = TickerParams(symbol=["BTC/USD"])
                sub_req_id = client._sub_req_counter + 1
                mock_ws.add_message(subscribe_response_json(sub_req_id))
                await client.subscribe(params)

                unsub_req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    unsubscribe_response_json(
                        unsub_req_id, success=False, error="Unsub failed"
                    )
                )

                with pytest.raises(SubscriptionError, match="Unsub failed"):
                    await client.unsubscribe(params)

                # Subscription should still be tracked on failure.
                assert len(client.subscriptions) == 1

                await client.disconnect()

        asyncio.run(_run())

    def test_unsubscribe_unknown_raises_key_error(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                params = TickerParams(symbol=["BTC/USD"])
                with pytest.raises(KeyError, match="No tracked subscription"):
                    await client.unsubscribe(params)

                await client.disconnect()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# TestReqIdCorrelation
# ---------------------------------------------------------------------------


class TestReqIdCorrelation:
    def test_response_not_enqueued_to_consumer(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                params = TickerParams(symbol=["BTC/USD"])
                req_id = client._sub_req_counter + 1
                # Queue: subscribe response, then a ticker message.
                mock_ws.add_message(subscribe_response_json(req_id))
                mock_ws.add_message(ticker_json())

                await client.subscribe(params)

                # Consumer should only get the ticker, not the sub response.
                msg = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg, WSDataMessage)
                assert msg.channel == "ticker"

                await client.disconnect()

        asyncio.run(_run())

    def test_unmatched_response_still_enqueued(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket(
                [
                    heartbeat_json(),
                    # Response with req_id that nobody is waiting for.
                    subscribe_response_json(999999),
                ]
            )
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # Should be enqueued since no pending future for req_id=999999.
                msg = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg, WSResponse)
                assert msg.req_id == 999999

                await client.disconnect()

        asyncio.run(_run())

    def test_concurrent_subscriptions_correlate_correctly(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])

            # Auto-respond to subscribe requests with matching req_id.
            original_send = mock_ws.send

            async def _auto_respond_send(data: str) -> None:
                await original_send(data)
                parsed = json.loads(data)
                if parsed.get("method") == "subscribe":
                    req_id = parsed["req_id"]
                    channel = parsed["params"]["channel"]
                    symbol = parsed["params"].get("symbol", [""])[0]
                    mock_ws.add_message(
                        subscribe_response_json(req_id, channel=channel, symbol=symbol)
                    )

            mock_ws.send = _auto_respond_send  # type: ignore[assignment]

            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                params_a = TickerParams(symbol=["BTC/USD"])
                params_b = BookParams(symbol=["ETH/USD"], depth=10)

                # Fire both concurrently.
                results = await asyncio.gather(
                    client.subscribe(params_a),
                    client.subscribe(params_b),
                )

                assert all(isinstance(r, WSResponse) for r in results)
                assert len(client.subscriptions) == 2

                await client.disconnect()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# TestReconnectResubscription
# ---------------------------------------------------------------------------


class TestReconnectResubscription:
    def test_resubscribe_after_reconnect(self) -> None:
        async def _run() -> None:
            # First WS: subscribe, then close.
            ws1 = MockWebSocket([heartbeat_json()])
            ws1._close_after = 3  # Close after sub response + heartbeat + 1 more

            # Second WS: will receive re-subscribe.
            ws2 = MockWebSocket([heartbeat_json()])

            connect_mock = AsyncMock(side_effect=[ws1, ws2])

            with patch(
                "kraken_connector.ws.client.websockets.connect",
                connect_mock,
            ):
                client = KrakenWSClient(
                    backoff_base=0.01,
                    max_reconnect_attempts=3,
                    heartbeat_timeout=30.0,
                    request_timeout=2.0,
                )
                await client.connect()

                # Subscribe on ws1.
                params = TickerParams(symbol=["BTC/USD"])
                req_id = client._sub_req_counter + 1
                ws1.add_message(subscribe_response_json(req_id))
                await client.subscribe(params)
                assert len(client.subscriptions) == 1

                # Close ws1 to trigger reconnect.
                ws1._close_after = ws1._index

                # Wait for reconnect.
                for _ in range(30):
                    await asyncio.sleep(0.1)
                    if connect_mock.call_count >= 2:
                        break

                # Queue response for re-subscribe on ws2.
                await asyncio.sleep(0.2)
                resub_req_id = client._sub_req_counter + 1
                ws2.add_message(subscribe_response_json(resub_req_id))

                # Wait for resubscribe to complete.
                await asyncio.sleep(1.0)

                # Should still have the subscription tracked.
                assert len(client.subscriptions) >= 1

                await client.disconnect()

        asyncio.run(_run())

    def test_pending_requests_fail_on_disconnect(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # Manually create a pending request.
                future: asyncio.Future[
                    object
                ] = asyncio.get_event_loop().create_future()
                client._pending_requests[42] = future  # type: ignore[assignment]

                await client.disconnect()

                assert future.done()
                with pytest.raises(ConnectionError):
                    future.result()

        asyncio.run(_run())

    def test_no_resubscribe_when_empty(self) -> None:
        async def _run() -> None:
            ws1 = MockWebSocket([heartbeat_json()])
            ws2 = MockWebSocket([heartbeat_json()])
            connect_mock = AsyncMock(side_effect=[ws1, ws2])

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
                # No subscriptions — just reconnect.
                await client._reconnect()

                assert client.state == ConnectionState.CONNECTED

                # ws2 should have no subscribe messages sent.
                sub_sent = [json.loads(s) for s in ws2.sent if "subscribe" in s]
                assert len(sub_sent) == 0

                await client.disconnect()

        asyncio.run(_run())
