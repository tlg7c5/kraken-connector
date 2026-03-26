"""Ticker channel data model for Kraken WebSocket API v2."""
from typing import Any, Self

from attrs import define as _attrs_define


@_attrs_define
class TickerData:
    """Ticker data from the v2 ticker channel.

    Attributes:
        symbol: Currency pair (e.g. "BTC/USD").
        bid: Best bid price.
        bid_qty: Best bid quantity.
        ask: Best ask price.
        ask_qty: Best ask quantity.
        last: Last traded price.
        volume: 24-hour volume in base currency.
        vwap: 24-hour volume weighted average price.
        low: 24-hour lowest trade price.
        high: 24-hour highest trade price.
        change: 24-hour price change in quote currency.
        change_pct: 24-hour price change in percentage points.
        timestamp: RFC3339 timestamp.
    """

    symbol: str
    bid: float
    bid_qty: float
    ask: float
    ask_qty: float
    last: float
    volume: float
    vwap: float
    low: float
    high: float
    change: float
    change_pct: float
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "bid": self.bid,
            "bid_qty": self.bid_qty,
            "ask": self.ask,
            "ask_qty": self.ask_qty,
            "last": self.last,
            "volume": self.volume,
            "vwap": self.vwap,
            "low": self.low,
            "high": self.high,
            "change": self.change,
            "change_pct": self.change_pct,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            symbol=d.pop("symbol"),
            bid=d.pop("bid"),
            bid_qty=d.pop("bid_qty"),
            ask=d.pop("ask"),
            ask_qty=d.pop("ask_qty"),
            last=d.pop("last"),
            volume=d.pop("volume"),
            vwap=d.pop("vwap"),
            low=d.pop("low"),
            high=d.pop("high"),
            change=d.pop("change"),
            change_pct=d.pop("change_pct"),
            timestamp=d.pop("timestamp"),
        )
