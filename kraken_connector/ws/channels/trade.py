"""Trade channel data model for Kraken WebSocket API v2."""
from typing import Any, Dict, Self

from attrs import define as _attrs_define


@_attrs_define
class TradeData:
    """Trade data from the v2 trade channel.

    Attributes:
        symbol: Currency pair (e.g. "BTC/USD").
        side: Trade side — "buy" or "sell".
        qty: Trade quantity.
        price: Trade price.
        ord_type: Order type that generated the trade (e.g. "limit", "market").
        trade_id: Sequence number per book.
        timestamp: RFC3339 timestamp.
    """

    symbol: str
    side: str
    qty: float
    price: float
    ord_type: str
    trade_id: int
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "qty": self.qty,
            "price": self.price,
            "ord_type": self.ord_type,
            "trade_id": self.trade_id,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, src_dict: Dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            symbol=d.pop("symbol"),
            side=d.pop("side"),
            qty=d.pop("qty"),
            price=d.pop("price"),
            ord_type=d.pop("ord_type"),
            trade_id=d.pop("trade_id"),
            timestamp=d.pop("timestamp"),
        )
