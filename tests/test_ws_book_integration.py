"""Tests for Phase 5 — book management integration with KrakenWSClient."""
import asyncio
from decimal import Decimal
from unittest.mock import patch

from kraken_connector.ws.book import BookChecksumEvent, OrderBook
from kraken_connector.ws.client import KrakenWSClient
from kraken_connector.ws.envelopes import WSDataMessage

from .ws_helpers import (
    MockWebSocket,
    async_return,
    book_snapshot_json,
    book_update_json,
    heartbeat_json,
)


class TestBookInRecvLoop:
    def test_book_snapshot_populates_manager(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket(
                [
                    heartbeat_json(),
                    book_snapshot_json(
                        "BTC/USD",
                        bids=[{"price": 26000.0, "qty": 1.5}],
                        asks=[{"price": 26001.0, "qty": 2.0}],
                    ),
                ]
            )
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                msg = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg, WSDataMessage)
                assert msg.channel == "book"

                book = client.book_manager.get("BTC/USD")
                assert book is not None
                assert book.best_bid == (Decimal("26000.0"), Decimal("1.5"))
                assert book.best_ask == (Decimal("26001.0"), Decimal("2.0"))

                await client.disconnect()

        asyncio.run(_run())

    def test_book_update_modifies_state(self) -> None:
        async def _run() -> None:
            # Compute checksum for the expected final state.
            temp_book = OrderBook(symbol="BTC/USD", depth=10)
            from kraken_connector.ws.channels.book import BookData, BookLevel

            temp_book.apply_snapshot(
                BookData(
                    symbol="BTC/USD",
                    bids=[BookLevel(Decimal("26000.0"), Decimal("1.5"))],
                    asks=[BookLevel(Decimal("26001.0"), Decimal("5.0"))],
                )
            )
            valid_checksum = OrderBook._compute_checksum(
                temp_book.asks[:10], temp_book.bids[:10]
            )

            mock_ws = MockWebSocket(
                [
                    heartbeat_json(),
                    book_snapshot_json(
                        "BTC/USD",
                        bids=[{"price": 26000.0, "qty": 1.5}],
                        asks=[{"price": 26001.0, "qty": 2.0}],
                    ),
                    book_update_json(
                        "BTC/USD",
                        asks=[{"price": 26001.0, "qty": 5.0}],
                        checksum=valid_checksum,
                    ),
                ]
            )
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # Snapshot.
                msg1 = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg1, WSDataMessage)

                # Update.
                msg2 = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg2, WSDataMessage)

                book = client.book_manager.get("BTC/USD")
                assert book is not None
                assert book.best_ask == (Decimal("26001.0"), Decimal("5.0"))

                await client.disconnect()

        asyncio.run(_run())

    def test_checksum_failure_enqueued(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket(
                [
                    heartbeat_json(),
                    book_snapshot_json(
                        "BTC/USD",
                        bids=[{"price": 26000.0, "qty": 1.5}],
                        asks=[{"price": 26001.0, "qty": 2.0}],
                    ),
                    book_update_json(
                        "BTC/USD",
                        asks=[{"price": 26001.0, "qty": 5.0}],
                        checksum=99999,  # Bad checksum.
                    ),
                ]
            )
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # Snapshot message.
                msg1 = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg1, WSDataMessage)

                # Checksum failure event should come before the data message.
                msg2 = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg2, BookChecksumEvent)
                assert msg2.symbol == "BTC/USD"

                # The data message is still enqueued.
                msg3 = await asyncio.wait_for(client.receive(), timeout=2.0)
                assert isinstance(msg3, WSDataMessage)

                await client.disconnect()

        asyncio.run(_run())

    def test_reconnect_clears_books(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                # Manually populate a book.
                client.book_manager.get_or_create("BTC/USD")
                assert client.book_manager.get("BTC/USD") is not None

                await client._resubscribe_all()
                assert client.book_manager.get("BTC/USD") is None

                await client.disconnect()

        asyncio.run(_run())

    def test_book_manager_accessible_from_client(self) -> None:
        async def _run() -> None:
            mock_ws = MockWebSocket([heartbeat_json()])
            with patch(
                "kraken_connector.ws.client.websockets.connect",
                return_value=async_return(mock_ws),
            ):
                client = KrakenWSClient(max_reconnect_attempts=0)
                await client.connect()

                mgr = client.book_manager
                assert mgr is not None
                assert mgr.get("BTC/USD") is None  # No books yet.

                await client.disconnect()

        asyncio.run(_run())
