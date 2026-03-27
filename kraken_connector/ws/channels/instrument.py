"""Instrument channel data models for Kraken WebSocket API v2."""
from typing import Any, Self

from attrs import define as _attrs_define

from ...types import UNSET, Unset


@_attrs_define
class InstrumentAsset:
    """Asset reference data from the instrument channel.

    Attributes:
        id: Asset identifier (e.g. "BTC").
        status: Asset status ("enabled", "depositonly", "disabled").
        precision: Ledger/balance precision.
        precision_display: Display precision.
        borrowable: Whether the asset can be borrowed.
        collateral_value: Collateral value multiplier.
        margin_rate: Borrow interest rate.
    """

    id: str
    status: str
    precision: int
    precision_display: int
    borrowable: bool
    collateral_value: Unset | float = UNSET
    margin_rate: Unset | float = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "id": self.id,
            "status": self.status,
            "precision": self.precision,
            "precision_display": self.precision_display,
            "borrowable": self.borrowable,
        }
        if not isinstance(self.collateral_value, Unset):
            field_dict["collateral_value"] = self.collateral_value
        if not isinstance(self.margin_rate, Unset):
            field_dict["margin_rate"] = self.margin_rate
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            id=d.pop("id"),
            status=d.pop("status"),
            precision=d.pop("precision"),
            precision_display=d.pop("precision_display"),
            borrowable=d.pop("borrowable"),
            collateral_value=d.pop("collateral_value", UNSET),
            margin_rate=d.pop("margin_rate", UNSET),
        )


@_attrs_define
class InstrumentPair:
    """Trading pair reference data from the instrument channel.

    Attributes:
        symbol: Pair symbol (e.g. "BTC/USD").
        base: Base currency id.
        quote: Quote currency id.
        status: Pair status ("online", "maintenance", etc.).
        qty_precision: Quantity precision.
        qty_increment: Minimum quantity increment.
        qty_min: Minimum order quantity.
        price_precision: Price precision.
        price_increment: Minimum price increment.
        cost_precision: Cost precision.
        cost_min: Minimum order cost.
        marginable: Whether margin trading is available.
        margin_initial: Initial margin requirement.
        position_limit_long: Maximum long position size.
        position_limit_short: Maximum short position size.
        has_index: Whether the pair has an index price.
    """

    symbol: str
    base: str
    quote: str
    status: str
    qty_precision: int
    qty_increment: float
    qty_min: float
    price_precision: int
    price_increment: float
    cost_precision: int
    cost_min: float
    marginable: bool
    margin_initial: Unset | float = UNSET
    position_limit_long: Unset | float = UNSET
    position_limit_short: Unset | float = UNSET
    has_index: Unset | bool = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "symbol": self.symbol,
            "base": self.base,
            "quote": self.quote,
            "status": self.status,
            "qty_precision": self.qty_precision,
            "qty_increment": self.qty_increment,
            "qty_min": self.qty_min,
            "price_precision": self.price_precision,
            "price_increment": self.price_increment,
            "cost_precision": self.cost_precision,
            "cost_min": self.cost_min,
            "marginable": self.marginable,
        }
        if not isinstance(self.margin_initial, Unset):
            field_dict["margin_initial"] = self.margin_initial
        if not isinstance(self.position_limit_long, Unset):
            field_dict["position_limit_long"] = self.position_limit_long
        if not isinstance(self.position_limit_short, Unset):
            field_dict["position_limit_short"] = self.position_limit_short
        if not isinstance(self.has_index, Unset):
            field_dict["has_index"] = self.has_index
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            symbol=d.pop("symbol"),
            base=d.pop("base"),
            quote=d.pop("quote"),
            status=d.pop("status"),
            qty_precision=d.pop("qty_precision"),
            qty_increment=d.pop("qty_increment"),
            qty_min=d.pop("qty_min"),
            price_precision=d.pop("price_precision"),
            price_increment=d.pop("price_increment"),
            cost_precision=d.pop("cost_precision"),
            cost_min=d.pop("cost_min"),
            marginable=d.pop("marginable"),
            margin_initial=d.pop("margin_initial", UNSET),
            position_limit_long=d.pop("position_limit_long", UNSET),
            position_limit_short=d.pop("position_limit_short", UNSET),
            has_index=d.pop("has_index", UNSET),
        )


@_attrs_define
class InstrumentData:
    """Instrument channel data containing assets and pairs.

    Attributes:
        assets: List of asset reference data.
        pairs: List of trading pair reference data.
    """

    assets: list[InstrumentAsset]
    pairs: list[InstrumentPair]

    def to_dict(self) -> dict[str, Any]:
        return {
            "assets": [a.to_dict() for a in self.assets],
            "pairs": [p.to_dict() for p in self.pairs],
        }

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        assets = [InstrumentAsset.from_dict(a) for a in d.pop("assets", [])]
        pairs = [InstrumentPair.from_dict(p) for p in d.pop("pairs", [])]
        return cls(assets=assets, pairs=pairs)
