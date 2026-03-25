"""OHLC channel data model for Kraken WebSocket API v2."""
from typing import Any, Dict, Self

from attrs import define as _attrs_define


@_attrs_define
class OHLCData:
    """OHLC candle data from the v2 ohlc channel.

    Attributes:
        symbol: Currency pair (e.g. "BTC/USD").
        open: Open price for the interval.
        high: High price for the interval.
        low: Low price for the interval.
        close: Close price for the interval.
        vwap: Volume weighted average price.
        trades: Count of trades in the interval.
        volume: Total volume in base currency.
        interval: Interval in minutes.
        interval_begin: Start of interval (RFC3339).
        timestamp: RFC3339 timestamp.
    """

    symbol: str
    open: float
    high: float
    low: float
    close: float
    vwap: float
    trades: int
    volume: float
    interval: int
    interval_begin: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "vwap": self.vwap,
            "trades": self.trades,
            "volume": self.volume,
            "interval": self.interval,
            "interval_begin": self.interval_begin,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, src_dict: Dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            symbol=d.pop("symbol"),
            open=d.pop("open"),
            high=d.pop("high"),
            low=d.pop("low"),
            close=d.pop("close"),
            vwap=d.pop("vwap"),
            trades=d.pop("trades"),
            volume=d.pop("volume"),
            interval=d.pop("interval"),
            interval_begin=d.pop("interval_begin"),
            timestamp=d.pop("timestamp"),
        )
