"""Executions channel data models for Kraken WebSocket API v2."""
from typing import Any, Self

from attrs import define as _attrs_define

from ...types import UNSET, Unset


@_attrs_define
class ExecutionFee:
    """Fee entry within an execution event.

    Attributes:
        asset: Fee currency asset.
        qty: Fee amount.
    """

    asset: str
    qty: float

    def to_dict(self) -> dict[str, Any]:
        return {"asset": self.asset, "qty": self.qty}

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(asset=d.pop("asset"), qty=d.pop("qty"))


@_attrs_define
class ExecutionData:
    """Execution data from the v2 executions channel.

    Combines order lifecycle and trade fill information. Fields present
    depend on the exec_type — order events have order fields, trade
    events additionally include execution-specific fields.

    Attributes:
        exec_type: Execution type (pending_new, new, trade, filled, etc.).
        order_id: Order identifier.
        symbol: Currency pair.
        order_status: Order status.
        side: Order side (buy/sell).
        order_type: Order type (limit, market, etc.).
        order_qty: Order quantity.
        limit_price: Limit price for limit orders.
        time_in_force: Time-in-force (gtc, gtd, ioc).
        order_userref: Client numeric reference.
        cl_ord_id: Client string identifier.
        timestamp: RFC3339 timestamp.
        cum_qty: Cumulative executed quantity.
        cum_cost: Cumulative execution value.
        avg_price: Average fill price.
        exec_id: Execution identifier (trade events).
        trade_id: Trade identifier (trade events).
        last_qty: Quantity in this execution (trade events).
        last_price: Price in this execution (trade events).
        cost: Value of this execution (trade events).
        liquidity_ind: Liquidity indicator — "t" (taker) or "m" (maker).
        fees: List of fee entries (trade events).
        fee_usd_equiv: USD equivalent of fees.
        margin: Whether this is a margin order.
    """

    exec_type: str
    order_id: str
    symbol: Unset | str = UNSET
    order_status: Unset | str = UNSET
    side: Unset | str = UNSET
    order_type: Unset | str = UNSET
    order_qty: Unset | float = UNSET
    limit_price: Unset | float = UNSET
    time_in_force: Unset | str = UNSET
    order_userref: Unset | int = UNSET
    cl_ord_id: Unset | str = UNSET
    timestamp: Unset | str = UNSET
    cum_qty: Unset | float = UNSET
    cum_cost: Unset | float = UNSET
    avg_price: Unset | float = UNSET
    exec_id: Unset | str = UNSET
    trade_id: Unset | int = UNSET
    last_qty: Unset | float = UNSET
    last_price: Unset | float = UNSET
    cost: Unset | float = UNSET
    liquidity_ind: Unset | str = UNSET
    fees: Unset | list[ExecutionFee] = UNSET
    fee_usd_equiv: Unset | float = UNSET
    margin: Unset | bool = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "exec_type": self.exec_type,
            "order_id": self.order_id,
        }
        if not isinstance(self.symbol, Unset):
            field_dict["symbol"] = self.symbol
        if not isinstance(self.order_status, Unset):
            field_dict["order_status"] = self.order_status
        if not isinstance(self.side, Unset):
            field_dict["side"] = self.side
        if not isinstance(self.order_type, Unset):
            field_dict["order_type"] = self.order_type
        if not isinstance(self.order_qty, Unset):
            field_dict["order_qty"] = self.order_qty
        if not isinstance(self.limit_price, Unset):
            field_dict["limit_price"] = self.limit_price
        if not isinstance(self.time_in_force, Unset):
            field_dict["time_in_force"] = self.time_in_force
        if not isinstance(self.order_userref, Unset):
            field_dict["order_userref"] = self.order_userref
        if not isinstance(self.cl_ord_id, Unset):
            field_dict["cl_ord_id"] = self.cl_ord_id
        if not isinstance(self.timestamp, Unset):
            field_dict["timestamp"] = self.timestamp
        if not isinstance(self.cum_qty, Unset):
            field_dict["cum_qty"] = self.cum_qty
        if not isinstance(self.cum_cost, Unset):
            field_dict["cum_cost"] = self.cum_cost
        if not isinstance(self.avg_price, Unset):
            field_dict["avg_price"] = self.avg_price
        if not isinstance(self.exec_id, Unset):
            field_dict["exec_id"] = self.exec_id
        if not isinstance(self.trade_id, Unset):
            field_dict["trade_id"] = self.trade_id
        if not isinstance(self.last_qty, Unset):
            field_dict["last_qty"] = self.last_qty
        if not isinstance(self.last_price, Unset):
            field_dict["last_price"] = self.last_price
        if not isinstance(self.cost, Unset):
            field_dict["cost"] = self.cost
        if not isinstance(self.liquidity_ind, Unset):
            field_dict["liquidity_ind"] = self.liquidity_ind
        if not isinstance(self.fees, Unset):
            field_dict["fees"] = [f.to_dict() for f in self.fees]
        if not isinstance(self.fee_usd_equiv, Unset):
            field_dict["fee_usd_equiv"] = self.fee_usd_equiv
        if not isinstance(self.margin, Unset):
            field_dict["margin"] = self.margin
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        exec_type = d.pop("exec_type")
        order_id = d.pop("order_id")
        fees_raw = d.pop("fees", UNSET)
        fees: Unset | list[ExecutionFee] = UNSET
        if not isinstance(fees_raw, Unset):
            fees = [ExecutionFee.from_dict(f) for f in fees_raw]
        return cls(
            exec_type=exec_type,
            order_id=order_id,
            symbol=d.pop("symbol", UNSET),
            order_status=d.pop("order_status", UNSET),
            side=d.pop("side", UNSET),
            order_type=d.pop("order_type", UNSET),
            order_qty=d.pop("order_qty", UNSET),
            limit_price=d.pop("limit_price", UNSET),
            time_in_force=d.pop("time_in_force", UNSET),
            order_userref=d.pop("order_userref", UNSET),
            cl_ord_id=d.pop("cl_ord_id", UNSET),
            timestamp=d.pop("timestamp", UNSET),
            cum_qty=d.pop("cum_qty", UNSET),
            cum_cost=d.pop("cum_cost", UNSET),
            avg_price=d.pop("avg_price", UNSET),
            exec_id=d.pop("exec_id", UNSET),
            trade_id=d.pop("trade_id", UNSET),
            last_qty=d.pop("last_qty", UNSET),
            last_price=d.pop("last_price", UNSET),
            cost=d.pop("cost", UNSET),
            liquidity_ind=d.pop("liquidity_ind", UNSET),
            fees=fees,
            fee_usd_equiv=d.pop("fee_usd_equiv", UNSET),
            margin=d.pop("margin", UNSET),
        )
