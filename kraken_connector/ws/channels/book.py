"""Book (Level 2) channel data models for Kraken WebSocket API v2."""
from typing import Any, Self

from attrs import define as _attrs_define

from ...types import UNSET, Unset


@_attrs_define
class BookLevel:
    """A single price level in the order book.

    Attributes:
        price: Price at this level.
        qty: Quantity at this level. A value of 0 signals level removal.
    """

    price: float
    qty: float

    def to_dict(self) -> dict[str, Any]:
        return {"price": self.price, "qty": self.qty}

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(price=d.pop("price"), qty=d.pop("qty"))


@_attrs_define
class BookData:
    """Order book data from the v2 book channel.

    Attributes:
        symbol: Currency pair (e.g. "BTC/USD").
        bids: Bid price levels (descending from best bid).
        asks: Ask price levels (ascending from best ask).
        checksum: CRC32 checksum of top 10 levels (present on updates).
        timestamp: RFC3339 timestamp.
    """

    symbol: str
    bids: list[BookLevel]
    asks: list[BookLevel]
    checksum: Unset | int = UNSET
    timestamp: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "symbol": self.symbol,
            "bids": [level.to_dict() for level in self.bids],
            "asks": [level.to_dict() for level in self.asks],
        }
        if not isinstance(self.checksum, Unset):
            field_dict["checksum"] = self.checksum
        if not isinstance(self.timestamp, Unset):
            field_dict["timestamp"] = self.timestamp
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        symbol = d.pop("symbol")
        bids = [BookLevel.from_dict(b) for b in d.pop("bids", [])]
        asks = [BookLevel.from_dict(a) for a in d.pop("asks", [])]
        checksum = d.pop("checksum", UNSET)
        timestamp = d.pop("timestamp", UNSET)
        return cls(
            symbol=symbol,
            bids=bids,
            asks=asks,
            checksum=checksum,
            timestamp=timestamp,
        )
