"""Order book state management for Kraken WebSocket API v2.

Maintains local order book state from snapshot and incremental update
messages, with CRC32 checksum validation for data integrity.
"""
import zlib
from decimal import Decimal

from attrs import Factory
from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .channels.book import BookData
from .envelopes import WSDataMessage


class ChecksumError(Exception):
    """Raised when book checksum validation fails."""

    def __init__(self, symbol: str, expected: int, computed: int) -> None:
        self.symbol = symbol
        self.expected = expected
        self.computed = computed
        super().__init__(
            f"Book checksum mismatch for {symbol}: "
            f"expected {expected}, computed {computed}"
        )


@_attrs_define
class BookChecksumEvent:
    """Emitted to the message queue when a book checksum fails.

    Attributes:
        symbol: The currency pair with the checksum mismatch.
        expected: The checksum from the server message.
        computed: The locally computed checksum.
    """

    symbol: str
    expected: int
    computed: int


@_attrs_define
class OrderBook:
    """Local order book state for a single symbol.

    Maintains sorted bid (descending) and ask (ascending) price levels.
    Applies snapshots (full replace) and updates (incremental).
    Validates CRC32 checksums when present.

    Attributes:
        symbol: Currency pair (e.g. "BTC/USD").
        depth: Subscribed book depth (10, 25, 100, 500, or 1000).
    """

    symbol: str
    depth: int = 10
    _asks: dict[Decimal, Decimal] = _attrs_field(factory=dict, init=False)
    _bids: dict[Decimal, Decimal] = _attrs_field(factory=dict, init=False)

    def apply_snapshot(self, data: BookData) -> None:
        """Replace book state with snapshot data."""
        self._asks.clear()
        self._bids.clear()
        for level in data.asks:
            self._asks[level.price] = level.qty
        for level in data.bids:
            self._bids[level.price] = level.qty
        self._truncate()

    def apply_update(self, data: BookData) -> None:
        """Apply incremental update. Validates checksum if present.

        Raises:
            ChecksumError: If checksum validation fails.
        """
        for level in data.asks:
            if level.qty == 0:
                self._asks.pop(level.price, None)
            else:
                self._asks[level.price] = level.qty

        for level in data.bids:
            if level.qty == 0:
                self._bids.pop(level.price, None)
            else:
                self._bids[level.price] = level.qty

        self._truncate()

        if not isinstance(data.checksum, int):
            return
        self.validate_checksum(data.checksum)

    def validate_checksum(self, expected: int) -> None:
        """Validate CRC32 checksum against top 10 levels.

        Raises:
            ChecksumError: If the computed checksum doesn't match.
        """
        computed = self._compute_checksum(self.asks[:10], self.bids[:10])
        if computed != expected:
            raise ChecksumError(self.symbol, expected, computed)

    @property
    def asks(self) -> list[tuple[Decimal, Decimal]]:
        """Ask levels sorted ascending by price."""
        return sorted(self._asks.items(), key=lambda x: x[0])

    @property
    def bids(self) -> list[tuple[Decimal, Decimal]]:
        """Bid levels sorted descending by price."""
        return sorted(self._bids.items(), key=lambda x: x[0], reverse=True)

    @property
    def best_bid(self) -> tuple[Decimal, Decimal] | None:
        """Highest bid (price, qty) or None if empty."""
        bids = self.bids
        return bids[0] if bids else None

    @property
    def best_ask(self) -> tuple[Decimal, Decimal] | None:
        """Lowest ask (price, qty) or None if empty."""
        asks = self.asks
        return asks[0] if asks else None

    @property
    def spread(self) -> Decimal | None:
        """Difference between best ask and best bid, or None."""
        ba = self.best_ask
        bb = self.best_bid
        if ba is None or bb is None:
            return None
        return ba[0] - bb[0]

    def _truncate(self) -> None:
        """Trim to subscribed depth."""
        if len(self._asks) > self.depth:
            sorted_asks = sorted(self._asks.keys())
            for price in sorted_asks[self.depth :]:
                del self._asks[price]

        if len(self._bids) > self.depth:
            sorted_bids = sorted(self._bids.keys(), reverse=True)
            for price in sorted_bids[self.depth :]:
                del self._bids[price]

    @staticmethod
    def _compute_checksum(
        asks: list[tuple[Decimal, Decimal]],
        bids: list[tuple[Decimal, Decimal]],
    ) -> int:
        """Compute CRC32 over top ask + bid levels.

        Algorithm: for each ask (ascending) then bid (descending),
        format price and qty by removing decimal point and stripping
        leading zeros, concatenate all, compute CRC32.
        """
        parts: list[str] = []
        for price, qty in asks:
            parts.append(OrderBook._format_decimal(price))
            parts.append(OrderBook._format_decimal(qty))
        for price, qty in bids:
            parts.append(OrderBook._format_decimal(price))
            parts.append(OrderBook._format_decimal(qty))
        payload = "".join(parts)
        return zlib.crc32(payload.encode("ascii")) & 0xFFFFFFFF

    @staticmethod
    def _format_decimal(value: Decimal) -> str:
        """Format a Decimal for checksum: remove dot, strip leading zeros."""
        s = str(value)
        if "." in s:
            s = s.replace(".", "")
        return s.lstrip("0") or "0"


@_attrs_define
class OrderBookManager:
    """Collection of OrderBook instances, keyed by symbol.

    Processes book channel WSDataMessages, applying snapshots and
    updates to the appropriate OrderBook.
    """

    _books: dict[str, OrderBook] = Factory(dict)

    def get(self, symbol: str) -> OrderBook | None:
        """Get the OrderBook for a symbol, or None."""
        return self._books.get(symbol)

    def get_or_create(self, symbol: str, depth: int = 10) -> OrderBook:
        """Get or create an OrderBook for a symbol."""
        if symbol not in self._books:
            self._books[symbol] = OrderBook(symbol=symbol, depth=depth)
        return self._books[symbol]

    def process_message(self, msg: WSDataMessage) -> BookChecksumEvent | None:
        """Apply a book WSDataMessage to the appropriate OrderBook.

        Returns:
            BookChecksumEvent if checksum validation fails, None otherwise.
        """
        if msg.channel != "book" or not msg.data:
            return None

        for item in msg.data:
            if not isinstance(item, BookData):
                continue

            book = self.get_or_create(item.symbol)

            try:
                if msg.type == "snapshot":
                    book.apply_snapshot(item)
                else:
                    book.apply_update(item)
            except ChecksumError as exc:
                return BookChecksumEvent(
                    symbol=exc.symbol,
                    expected=exc.expected,
                    computed=exc.computed,
                )
        return None

    def remove(self, symbol: str) -> None:
        """Remove the OrderBook for a symbol."""
        self._books.pop(symbol, None)

    def clear(self) -> None:
        """Remove all OrderBook instances."""
        self._books.clear()
