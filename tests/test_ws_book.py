"""Tests for Phase 5 — Order book management."""
from decimal import Decimal

import pytest

from kraken_connector.ws.book import (
    BookChecksumEvent,
    ChecksumError,
    OrderBook,
    OrderBookManager,
)
from kraken_connector.ws.channels.book import BookData, BookLevel
from kraken_connector.ws.envelopes import WSDataMessage


def _make_levels(
    prices_qtys: list[tuple[str, str]],
) -> list[BookLevel]:
    return [BookLevel(price=Decimal(p), qty=Decimal(q)) for p, q in prices_qtys]


def _make_book_data(
    symbol: str = "BTC/USD",
    bids: list[tuple[str, str]] | None = None,
    asks: list[tuple[str, str]] | None = None,
    checksum: int | None = None,
) -> BookData:
    from kraken_connector.types import UNSET

    return BookData(
        symbol=symbol,
        bids=_make_levels(bids or []),
        asks=_make_levels(asks or []),
        checksum=checksum if checksum is not None else UNSET,
    )


# ---------------------------------------------------------------------------
# TestOrderBook
# ---------------------------------------------------------------------------


class TestOrderBook:
    def test_apply_snapshot_replaces_state(self) -> None:
        book = OrderBook(symbol="BTC/USD", depth=10)
        data = _make_book_data(
            bids=[("26000.0", "1.5"), ("25999.0", "2.0")],
            asks=[("26001.0", "1.0"), ("26002.0", "3.0")],
        )
        book.apply_snapshot(data)

        assert len(book.bids) == 2
        assert len(book.asks) == 2
        assert book.bids[0] == (Decimal("26000.0"), Decimal("1.5"))
        assert book.asks[0] == (Decimal("26001.0"), Decimal("1.0"))

    def test_apply_snapshot_replaces_previous(self) -> None:
        book = OrderBook(symbol="BTC/USD", depth=10)
        book.apply_snapshot(_make_book_data(bids=[("100", "1")], asks=[("101", "1")]))
        book.apply_snapshot(_make_book_data(bids=[("200", "2")], asks=[("201", "2")]))
        assert len(book.bids) == 1
        assert book.bids[0][0] == Decimal("200")

    def test_apply_update_inserts_new_level(self) -> None:
        book = OrderBook(symbol="BTC/USD", depth=10)
        book.apply_snapshot(
            _make_book_data(bids=[("26000.0", "1.0")], asks=[("26001.0", "1.0")])
        )
        book.apply_update(_make_book_data(bids=[("25999.0", "0.5")], asks=[]))
        assert len(book.bids) == 2

    def test_apply_update_modifies_existing_level(self) -> None:
        book = OrderBook(symbol="BTC/USD", depth=10)
        book.apply_snapshot(_make_book_data(bids=[("26000.0", "1.0")], asks=[]))
        book.apply_update(_make_book_data(bids=[("26000.0", "5.0")], asks=[]))
        assert len(book.bids) == 1
        assert book.bids[0][1] == Decimal("5.0")

    def test_apply_update_removes_level_on_zero_qty(self) -> None:
        book = OrderBook(symbol="BTC/USD", depth=10)
        book.apply_snapshot(
            _make_book_data(
                bids=[("26000.0", "1.0"), ("25999.0", "2.0")],
                asks=[],
            )
        )
        book.apply_update(_make_book_data(bids=[("26000.0", "0")], asks=[]))
        assert len(book.bids) == 1
        assert book.bids[0][0] == Decimal("25999.0")

    def test_truncate_to_depth(self) -> None:
        book = OrderBook(symbol="BTC/USD", depth=3)
        bids = [(str(26000 - i), "1.0") for i in range(5)]
        asks = [(str(26001 + i), "1.0") for i in range(5)]
        book.apply_snapshot(_make_book_data(bids=bids, asks=asks))
        assert len(book.bids) == 3
        assert len(book.asks) == 3
        # Best bid is highest price
        assert book.bids[0][0] == Decimal("26000")
        # Best ask is lowest price
        assert book.asks[0][0] == Decimal("26001")

    def test_best_bid_ask_spread(self) -> None:
        book = OrderBook(symbol="BTC/USD", depth=10)
        book.apply_snapshot(
            _make_book_data(
                bids=[("26000.0", "1.0")],
                asks=[("26005.0", "2.0")],
            )
        )
        assert book.best_bid == (Decimal("26000.0"), Decimal("1.0"))
        assert book.best_ask == (Decimal("26005.0"), Decimal("2.0"))
        assert book.spread == Decimal("5.0")

    def test_empty_book_properties(self) -> None:
        book = OrderBook(symbol="BTC/USD", depth=10)
        assert book.best_bid is None
        assert book.best_ask is None
        assert book.spread is None


# ---------------------------------------------------------------------------
# TestChecksum
# ---------------------------------------------------------------------------


class TestChecksum:
    def test_format_decimal_strips_dot_and_leading_zeros(self) -> None:
        assert OrderBook._format_decimal(Decimal("0.00041")) == "41"
        assert OrderBook._format_decimal(Decimal("12.00000000")) == "1200000000"
        assert OrderBook._format_decimal(Decimal("26000.0")) == "260000"
        assert OrderBook._format_decimal(Decimal("0")) == "0"
        assert OrderBook._format_decimal(Decimal("100")) == "100"

    def test_compute_checksum_known_values(self) -> None:
        import zlib

        # Manual computation for verification.
        asks = [(Decimal("26001.0"), Decimal("2.0"))]
        bids = [(Decimal("26000.0"), Decimal("1.5"))]
        # asks: "260010" + "20" = "26001020"
        # bids: "260000" + "15" = "26000015"
        # Actually: "26001.0" -> remove dot -> "260010" -> lstrip 0 -> "260010"
        # "2.0" -> "20" -> "20"
        # "26000.0" -> "260000" -> "260000"
        # "1.5" -> "15" -> "15"
        # Let me just use the function directly and verify it's consistent
        computed = OrderBook._compute_checksum(asks, bids)
        # Verify against zlib directly
        payload_str = "2600102026000015"
        expected = zlib.crc32(payload_str.encode("ascii")) & 0xFFFFFFFF
        assert computed == expected

    def test_validate_checksum_passes(self) -> None:
        book = OrderBook(symbol="BTC/USD", depth=10)
        book.apply_snapshot(
            _make_book_data(
                bids=[("26000.0", "1.5")],
                asks=[("26001.0", "2.0")],
            )
        )
        # Compute the correct checksum.
        correct = OrderBook._compute_checksum(book.asks[:10], book.bids[:10])
        # Should not raise.
        book.validate_checksum(correct)

    def test_validate_checksum_fails(self) -> None:
        book = OrderBook(symbol="BTC/USD", depth=10)
        book.apply_snapshot(
            _make_book_data(
                bids=[("26000.0", "1.5")],
                asks=[("26001.0", "2.0")],
            )
        )
        with pytest.raises(ChecksumError, match="checksum mismatch"):
            book.validate_checksum(99999)

    def test_checksum_with_fewer_than_10_levels(self) -> None:
        book = OrderBook(symbol="BTC/USD", depth=10)
        book.apply_snapshot(
            _make_book_data(
                bids=[("100", "1")],
                asks=[("101", "2"), ("102", "3")],
            )
        )
        correct = OrderBook._compute_checksum(book.asks[:10], book.bids[:10])
        book.validate_checksum(correct)  # Should not raise.

    def test_checksum_precision_with_many_decimals(self) -> None:
        # Verify that 0.00041 formats to "41", etc.
        asks = [(Decimal("0.00041"), Decimal("100.00000000"))]
        bids = [(Decimal("0.00040"), Decimal("200.00000000"))]
        # asks: "41" + "10000000000"
        # bids: "40" + "20000000000"
        import zlib

        payload = "41100000000004020000000000"
        expected = zlib.crc32(payload.encode("ascii")) & 0xFFFFFFFF
        computed = OrderBook._compute_checksum(asks, bids)
        assert computed == expected

    def test_apply_update_validates_checksum(self) -> None:
        book = OrderBook(symbol="BTC/USD", depth=10)
        book.apply_snapshot(_make_book_data(bids=[("100", "1")], asks=[("101", "1")]))
        # Update with bad checksum.
        with pytest.raises(ChecksumError):
            book.apply_update(
                _make_book_data(bids=[("100", "2")], asks=[], checksum=99999)
            )


# ---------------------------------------------------------------------------
# TestDecimalBookLevel
# ---------------------------------------------------------------------------


class TestDecimalBookLevel:
    def test_book_level_decimal_roundtrip(self) -> None:
        raw = {"price": 26000.5, "qty": 1.25}
        level = BookLevel.from_dict(raw)
        assert level.price == Decimal("26000.5")
        assert level.qty == Decimal("1.25")
        d = level.to_dict()
        assert d["price"] == 26000.5
        assert d["qty"] == 1.25

    def test_book_level_precision_preserved(self) -> None:
        raw = {"price": 0.00041, "qty": 12.0}
        level = BookLevel.from_dict(raw)
        assert level.price == Decimal("0.00041")
        assert level.qty == Decimal("12.0")


# ---------------------------------------------------------------------------
# TestOrderBookManager
# ---------------------------------------------------------------------------


class TestOrderBookManager:
    def test_process_snapshot_creates_book(self) -> None:
        mgr = OrderBookManager()
        data = BookData(
            symbol="BTC/USD",
            bids=_make_levels([("26000", "1")]),
            asks=_make_levels([("26001", "2")]),
        )
        msg = WSDataMessage(channel="book", type="snapshot", data=[data])
        result = mgr.process_message(msg)
        assert result is None
        book = mgr.get("BTC/USD")
        assert book is not None
        assert len(book.bids) == 1

    def test_process_update_applies_to_existing(self) -> None:
        mgr = OrderBookManager()
        snapshot = BookData(
            symbol="BTC/USD",
            bids=_make_levels([("26000", "1")]),
            asks=_make_levels([("26001", "2")]),
        )
        mgr.process_message(
            WSDataMessage(channel="book", type="snapshot", data=[snapshot])
        )

        update = BookData(
            symbol="BTC/USD",
            bids=_make_levels([("26000", "5")]),
            asks=[],
        )
        mgr.process_message(WSDataMessage(channel="book", type="update", data=[update]))

        book = mgr.get("BTC/USD")
        assert book is not None
        assert book.bids[0][1] == Decimal("5")

    def test_checksum_failure_returns_event(self) -> None:
        mgr = OrderBookManager()
        snapshot = BookData(
            symbol="BTC/USD",
            bids=_make_levels([("26000", "1")]),
            asks=_make_levels([("26001", "2")]),
        )
        mgr.process_message(
            WSDataMessage(channel="book", type="snapshot", data=[snapshot])
        )

        bad_update = BookData(
            symbol="BTC/USD",
            bids=_make_levels([("26000", "5")]),
            asks=[],
            checksum=99999,
        )
        result = mgr.process_message(
            WSDataMessage(channel="book", type="update", data=[bad_update])
        )
        assert isinstance(result, BookChecksumEvent)
        assert result.symbol == "BTC/USD"

    def test_clear_removes_all_books(self) -> None:
        mgr = OrderBookManager()
        mgr.get_or_create("BTC/USD")
        mgr.get_or_create("ETH/USD")
        assert mgr.get("BTC/USD") is not None
        mgr.clear()
        assert mgr.get("BTC/USD") is None
        assert mgr.get("ETH/USD") is None
