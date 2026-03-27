"""Subscription parameter models for Kraken WebSocket API v2."""
from typing import Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset


@_attrs_define
class TickerParams:
    """Subscription parameters for the ticker channel.

    Attributes:
        symbol: List of currency pairs to subscribe to.
        event_trigger: Optional trigger filter — "bbo" or "trades".
    """

    symbol: list[str] = _attrs_field(factory=list)
    event_trigger: Unset | str = UNSET
    channel: str = "ticker"

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "channel": self.channel,
            "symbol": self.symbol,
        }
        if not isinstance(self.event_trigger, Unset):
            field_dict["event_trigger"] = self.event_trigger
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            channel=d.pop("channel", "ticker"),
            symbol=d.pop("symbol", []),
            event_trigger=d.pop("event_trigger", UNSET),
        )


@_attrs_define
class BookParams:
    """Subscription parameters for the book (Level 2) channel.

    Attributes:
        symbol: List of currency pairs to subscribe to.
        depth: Book depth — 10, 25, 100, 500, or 1000.
    """

    symbol: list[str] = _attrs_field(factory=list)
    depth: int = 10
    channel: str = "book"

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel": self.channel,
            "symbol": self.symbol,
            "depth": self.depth,
        }

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            channel=d.pop("channel", "book"),
            symbol=d.pop("symbol", []),
            depth=d.pop("depth", 10),
        )


@_attrs_define
class TradeParams:
    """Subscription parameters for the trade channel.

    Attributes:
        symbol: List of currency pairs to subscribe to.
        snapshot: Whether to receive a snapshot of recent trades on subscribe.
    """

    symbol: list[str] = _attrs_field(factory=list)
    snapshot: Unset | bool = UNSET
    channel: str = "trade"

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "channel": self.channel,
            "symbol": self.symbol,
        }
        if not isinstance(self.snapshot, Unset):
            field_dict["snapshot"] = self.snapshot
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            channel=d.pop("channel", "trade"),
            symbol=d.pop("symbol", []),
            snapshot=d.pop("snapshot", UNSET),
        )


@_attrs_define
class OHLCParams:
    """Subscription parameters for the OHLC channel.

    Attributes:
        symbol: List of currency pairs to subscribe to.
        interval: Candle interval in minutes (1, 5, 15, 30, 60, 240, 1440, 10080, 21600).
    """

    symbol: list[str] = _attrs_field(factory=list)
    interval: int = 1
    channel: str = "ohlc"

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel": self.channel,
            "symbol": self.symbol,
            "interval": self.interval,
        }

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            channel=d.pop("channel", "ohlc"),
            symbol=d.pop("symbol", []),
            interval=d.pop("interval", 1),
        )


@_attrs_define
class InstrumentParams:
    """Subscription parameters for the instrument channel.

    Attributes:
        include_tokenized_assets: Whether to include tokenized assets.
    """

    include_tokenized_assets: Unset | bool = UNSET
    channel: str = "instrument"

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {"channel": self.channel}
        if not isinstance(self.include_tokenized_assets, Unset):
            field_dict["include_tokenized_assets"] = self.include_tokenized_assets
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            channel=d.pop("channel", "instrument"),
            include_tokenized_assets=d.pop("include_tokenized_assets", UNSET),
        )


@_attrs_define
class ExecutionsParams:
    """Subscription parameters for the executions (private) channel.

    Attributes:
        token: Authentication token from GetWebSocketsToken.
        snap_orders: Whether to receive an order snapshot on subscribe.
        snap_trades: Whether to receive a trade snapshot on subscribe.
        order_status: Optional filter by order status.
        ratecounter: Whether to include rate counter data.
    """

    token: str = ""
    snap_orders: Unset | bool = UNSET
    snap_trades: Unset | bool = UNSET
    order_status: Unset | str = UNSET
    ratecounter: Unset | bool = UNSET
    channel: str = "executions"

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "channel": self.channel,
            "token": self.token,
        }
        if not isinstance(self.snap_orders, Unset):
            field_dict["snap_orders"] = self.snap_orders
        if not isinstance(self.snap_trades, Unset):
            field_dict["snap_trades"] = self.snap_trades
        if not isinstance(self.order_status, Unset):
            field_dict["order_status"] = self.order_status
        if not isinstance(self.ratecounter, Unset):
            field_dict["ratecounter"] = self.ratecounter
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            channel=d.pop("channel", "executions"),
            token=d.pop("token", ""),
            snap_orders=d.pop("snap_orders", UNSET),
            snap_trades=d.pop("snap_trades", UNSET),
            order_status=d.pop("order_status", UNSET),
            ratecounter=d.pop("ratecounter", UNSET),
        )


@_attrs_define
class BalancesParams:
    """Subscription parameters for the balances (private) channel.

    Attributes:
        token: Authentication token from GetWebSocketsToken.
        snapshot: Whether to receive a balance snapshot on subscribe.
    """

    token: str = ""
    snapshot: Unset | bool = UNSET
    channel: str = "balances"

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "channel": self.channel,
            "token": self.token,
        }
        if not isinstance(self.snapshot, Unset):
            field_dict["snapshot"] = self.snapshot
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            channel=d.pop("channel", "balances"),
            token=d.pop("token", ""),
            snapshot=d.pop("snapshot", UNSET),
        )
