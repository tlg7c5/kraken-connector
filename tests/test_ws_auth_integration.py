"""Tests for Phase 4 — auth integration in KrakenWSClient."""
import asyncio
import json
from unittest.mock import MagicMock, patch

from kraken_connector.ws import KrakenWSClient
from kraken_connector.ws.envelopes import WSDataMessage
from kraken_connector.ws.sequence import SequenceGapEvent
from kraken_connector.ws.subscribe import BalancesParams, ExecutionsParams, TickerParams
from kraken_connector.ws.token import TokenManager

from .ws_helpers import (
    MockWebSocket,
    async_return,
    balances_snapshot_json,
    executions_json,
    heartbeat_json,
    subscribe_response_json,
    ticker_json,
)


def _mock_token_manager(token: str = "test-token") -> TokenManager:  # noqa: S107
    """Create a TokenManager with a mocked auth client."""
    tm = TokenManager(auth_client=MagicMock())
    tm._token = token
    tm._expires_at = float("inf")  # Never expires.
    return tm


# ---------------------------------------------------------------------------
# TestPrivateSubscription
# ---------------------------------------------------------------------------


class TestPrivateSubscription:
    def test_subscribe_injects_token_for_executions(self) -> None:
        async def _run() -> None:
            tm = _mock_token_manager("injected-token")
            mock_ws = MockWebSocket([heartbeat_json()])

            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0, token_manager=tm)
                await client.connect()

                params = ExecutionsParams()
                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    subscribe_response_json(req_id, channel="executions")
                )

                await client.subscribe(params)

                # Check that the sent request includes the injected token.
                sent = [json.loads(s) for s in mock_ws.sent]
                sub_requests = [s for s in sent if s.get("method") == "subscribe"]
                assert len(sub_requests) == 1
                assert (
                    sub_requests[0]["params"]["token"] == "injected-token"  # noqa: S105
                )

                await client.disconnect()

        asyncio.run(_run())

    def test_subscribe_injects_token_for_balances(self) -> None:
        async def _run() -> None:
            tm = _mock_token_manager("bal-token")
            mock_ws = MockWebSocket([heartbeat_json()])

            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0, token_manager=tm)
                await client.connect()

                params = BalancesParams()
                req_id = client._sub_req_counter + 1
                mock_ws.add_message(subscribe_response_json(req_id, channel="balances"))

                await client.subscribe(params)

                sent = [json.loads(s) for s in mock_ws.sent]
                sub_requests = [s for s in sent if s.get("method") == "subscribe"]
                assert sub_requests[0]["params"]["token"] == "bal-token"  # noqa: S105

                await client.disconnect()

        asyncio.run(_run())

    def test_subscribe_no_injection_without_token_manager(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])

            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                # No token_manager provided.
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                params = ExecutionsParams(token="manual-token")  # noqa: S106
                req_id = client._sub_req_counter + 1
                mock_ws.add_message(
                    subscribe_response_json(req_id, channel="executions")
                )

                await client.subscribe(params)

                # Should use the manually provided token.
                sent = [json.loads(s) for s in mock_ws.sent]
                sub_requests = [s for s in sent if s.get("method") == "subscribe"]
                assert (
                    sub_requests[0]["params"]["token"] == "manual-token"  # noqa: S105
                )

                await client.disconnect()

        asyncio.run(_run())

    def test_subscribe_no_injection_for_public_channel(self) -> None:
        async def _run() -> None:
            tm = _mock_token_manager("should-not-appear")
            mock_ws = MockWebSocket([heartbeat_json()])

            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0, token_manager=tm)
                await client.connect()

                params = TickerParams(symbol=["BTC/USD"])
                req_id = client._sub_req_counter + 1
                mock_ws.add_message(subscribe_response_json(req_id))

                await client.subscribe(params)

                # Public channel params should NOT have token field.
                sent = [json.loads(s) for s in mock_ws.sent]
                sub_requests = [s for s in sent if s.get("method") == "subscribe"]
                assert "token" not in sub_requests[0]["params"]

                await client.disconnect()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# TestReconnectTokenRefresh
# ---------------------------------------------------------------------------


class TestReconnectTokenRefresh:
    def test_resubscribe_invalidates_token_before_refetch(self) -> None:
        async def _run() -> None:
            tm = _mock_token_manager("old-token")
            assert tm.is_valid  # Token is valid before resubscribe.

            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0, token_manager=tm)
                await client.connect()

                await client._resubscribe_all()
                # After resubscribe, token should be invalidated.
                assert not tm.is_valid

                await client.disconnect()

        asyncio.run(_run())

    def test_reconnect_resets_sequence_tracker(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # Set some sequence state.
                client._sequence_tracker.check(10, "executions")
                assert client._sequence_tracker._last_sequence == 10

                await client._resubscribe_all()
                assert client._sequence_tracker._last_sequence is None

                await client.disconnect()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# TestSequenceInRecvLoop
# ---------------------------------------------------------------------------


class TestSequenceInRecvLoop:
    def test_sequence_gap_enqueued_to_consumer(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket(
                [
                    heartbeat_json(),
                    executions_json(sequence=1),
                    executions_json(sequence=5),  # Gap: expected 2, got 5.
                ]
            )
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # First: executions data (seq=1, baseline).
                msg1 = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg1, WSDataMessage)
                assert msg1.channel == "executions"

                # Second: SequenceGapEvent (expected=2, received=5).
                msg2 = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg2, SequenceGapEvent)
                assert msg2.expected == 2
                assert msg2.received == 5

                # Third: the actual executions data (seq=5) still enqueued.
                msg3 = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg3, WSDataMessage)

                await client.disconnect()

        asyncio.run(_run())

    def test_no_gap_event_for_public_channels(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket(
                [
                    heartbeat_json(),
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

                msg1 = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg1, WSDataMessage)
                assert msg1.channel == "ticker"

                msg2 = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg2, WSDataMessage)
                assert msg2.channel == "ticker"

                await client.disconnect()

        asyncio.run(_run())

    def test_first_private_message_no_gap(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket(
                [
                    heartbeat_json(),
                    balances_snapshot_json(sequence=42),
                ]
            )
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # First private message sets baseline — no gap event.
                msg = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg, WSDataMessage)
                assert msg.channel == "balances"
                assert msg.sequence == 42

                await client.disconnect()

        asyncio.run(_run())
