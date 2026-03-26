"""Trading method parameter and result models for Kraken WebSocket API v2."""
from typing import Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

# ---------------------------------------------------------------------------
# Nested objects
# ---------------------------------------------------------------------------


@_attrs_define
class OrderTrigger:
    """Trigger configuration for conditional orders.

    Attributes:
        reference: Trigger price reference ("index" or "last").
        price: Trigger price.
        price_type: Price interpretation ("static", "pct", "quote").
    """

    reference: str
    price: float
    price_type: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "reference": self.reference,
            "price": self.price,
        }
        if not isinstance(self.price_type, Unset):
            field_dict["price_type"] = self.price_type
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            reference=d.pop("reference"),
            price=d.pop("price"),
            price_type=d.pop("price_type", UNSET),
        )


@_attrs_define
class ConditionalClose:
    """Conditional close order template attached to a parent order.

    Attributes:
        order_type: Order type for the close order.
        limit_price: Limit price for the close order.
        trigger_price: Trigger price for the close order.
    """

    order_type: str
    limit_price: Unset | float = UNSET
    trigger_price: Unset | float = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {"order_type": self.order_type}
        if not isinstance(self.limit_price, Unset):
            field_dict["limit_price"] = self.limit_price
        if not isinstance(self.trigger_price, Unset):
            field_dict["trigger_price"] = self.trigger_price
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            order_type=d.pop("order_type"),
            limit_price=d.pop("limit_price", UNSET),
            trigger_price=d.pop("trigger_price", UNSET),
        )


# ---------------------------------------------------------------------------
# Request params
# ---------------------------------------------------------------------------


@_attrs_define
class AddOrderParams:
    """Parameters for the add_order trading method.

    Attributes:
        symbol: Currency pair (e.g. "BTC/USD").
        side: Order side ("buy" or "sell").
        order_type: Order type (limit, market, etc.).
        order_qty: Order quantity.
        token: Authentication token.
        limit_price: Limit price (for limit orders).
        limit_price_type: Price interpretation ("static", "pct", "quote").
        triggers: Trigger configuration for conditional orders.
        time_in_force: Time-in-force ("gtc", "gtd", "ioc").
        margin: Whether this is a margin order.
        post_only: Whether to post-only.
        reduce_only: Whether to reduce-only.
        effective_time: Scheduled start time (RFC3339).
        expire_time: Expiration time for GTD orders (RFC3339).
        deadline: Response deadline (RFC3339, 500ms-60s).
        cl_ord_id: Client order identifier string.
        order_userref: Client numeric reference.
        conditional: Conditional close order template.
        display_qty: Display quantity for iceberg orders.
        fee_preference: Fee currency preference ("base" or "quote").
        stp_type: Self-trade prevention type.
        cash_order_qty: Buy market order quantity in quote currency.
        validate: Validation-only mode (no execution).
    """

    symbol: str
    side: str
    order_type: str
    order_qty: float
    token: str
    limit_price: Unset | float = UNSET
    limit_price_type: Unset | str = UNSET
    triggers: Unset | OrderTrigger = UNSET
    time_in_force: Unset | str = UNSET
    margin: Unset | bool = UNSET
    post_only: Unset | bool = UNSET
    reduce_only: Unset | bool = UNSET
    effective_time: Unset | str = UNSET
    expire_time: Unset | str = UNSET
    deadline: Unset | str = UNSET
    cl_ord_id: Unset | str = UNSET
    order_userref: Unset | int = UNSET
    conditional: Unset | ConditionalClose = UNSET
    display_qty: Unset | float = UNSET
    fee_preference: Unset | str = UNSET
    stp_type: Unset | str = UNSET
    cash_order_qty: Unset | float = UNSET
    validate: Unset | bool = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "symbol": self.symbol,
            "side": self.side,
            "order_type": self.order_type,
            "order_qty": self.order_qty,
            "token": self.token,
        }
        if not isinstance(self.limit_price, Unset):
            field_dict["limit_price"] = self.limit_price
        if not isinstance(self.limit_price_type, Unset):
            field_dict["limit_price_type"] = self.limit_price_type
        if not isinstance(self.triggers, Unset):
            field_dict["triggers"] = self.triggers.to_dict()
        if not isinstance(self.time_in_force, Unset):
            field_dict["time_in_force"] = self.time_in_force
        if not isinstance(self.margin, Unset):
            field_dict["margin"] = self.margin
        if not isinstance(self.post_only, Unset):
            field_dict["post_only"] = self.post_only
        if not isinstance(self.reduce_only, Unset):
            field_dict["reduce_only"] = self.reduce_only
        if not isinstance(self.effective_time, Unset):
            field_dict["effective_time"] = self.effective_time
        if not isinstance(self.expire_time, Unset):
            field_dict["expire_time"] = self.expire_time
        if not isinstance(self.deadline, Unset):
            field_dict["deadline"] = self.deadline
        if not isinstance(self.cl_ord_id, Unset):
            field_dict["cl_ord_id"] = self.cl_ord_id
        if not isinstance(self.order_userref, Unset):
            field_dict["order_userref"] = self.order_userref
        if not isinstance(self.conditional, Unset):
            field_dict["conditional"] = self.conditional.to_dict()
        if not isinstance(self.display_qty, Unset):
            field_dict["display_qty"] = self.display_qty
        if not isinstance(self.fee_preference, Unset):
            field_dict["fee_preference"] = self.fee_preference
        if not isinstance(self.stp_type, Unset):
            field_dict["stp_type"] = self.stp_type
        if not isinstance(self.cash_order_qty, Unset):
            field_dict["cash_order_qty"] = self.cash_order_qty
        if not isinstance(self.validate, Unset):
            field_dict["validate"] = self.validate
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        triggers_raw = d.pop("triggers", UNSET)
        triggers: Unset | OrderTrigger = UNSET
        if not isinstance(triggers_raw, Unset):
            triggers = OrderTrigger.from_dict(triggers_raw)
        conditional_raw = d.pop("conditional", UNSET)
        conditional: Unset | ConditionalClose = UNSET
        if not isinstance(conditional_raw, Unset):
            conditional = ConditionalClose.from_dict(conditional_raw)
        return cls(
            symbol=d.pop("symbol"),
            side=d.pop("side"),
            order_type=d.pop("order_type"),
            order_qty=d.pop("order_qty"),
            token=d.pop("token"),
            limit_price=d.pop("limit_price", UNSET),
            limit_price_type=d.pop("limit_price_type", UNSET),
            triggers=triggers,
            time_in_force=d.pop("time_in_force", UNSET),
            margin=d.pop("margin", UNSET),
            post_only=d.pop("post_only", UNSET),
            reduce_only=d.pop("reduce_only", UNSET),
            effective_time=d.pop("effective_time", UNSET),
            expire_time=d.pop("expire_time", UNSET),
            deadline=d.pop("deadline", UNSET),
            cl_ord_id=d.pop("cl_ord_id", UNSET),
            order_userref=d.pop("order_userref", UNSET),
            conditional=conditional,
            display_qty=d.pop("display_qty", UNSET),
            fee_preference=d.pop("fee_preference", UNSET),
            stp_type=d.pop("stp_type", UNSET),
            cash_order_qty=d.pop("cash_order_qty", UNSET),
            validate=d.pop("validate", UNSET),
        )


@_attrs_define
class EditOrderParams:
    """Parameters for the edit_order trading method.

    Edit is cancel-and-replace — a new order_id is returned.

    Attributes:
        order_id: Order to edit.
        symbol: Currency pair.
        token: Authentication token.
        order_qty: New order quantity.
        limit_price: New limit price.
        display_qty: New display quantity (iceberg).
        post_only: New post-only flag.
        reduce_only: New reduce-only flag.
        deadline: Response deadline (RFC3339).
        fee_preference: Fee currency preference.
        order_userref: Client numeric reference.
        validate: Validation-only mode.
        triggers: New trigger configuration.
    """

    order_id: str
    symbol: str
    token: str
    order_qty: Unset | float = UNSET
    limit_price: Unset | float = UNSET
    display_qty: Unset | float = UNSET
    post_only: Unset | bool = UNSET
    reduce_only: Unset | bool = UNSET
    deadline: Unset | str = UNSET
    fee_preference: Unset | str = UNSET
    order_userref: Unset | int = UNSET
    validate: Unset | bool = UNSET
    triggers: Unset | OrderTrigger = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "token": self.token,
        }
        if not isinstance(self.order_qty, Unset):
            field_dict["order_qty"] = self.order_qty
        if not isinstance(self.limit_price, Unset):
            field_dict["limit_price"] = self.limit_price
        if not isinstance(self.display_qty, Unset):
            field_dict["display_qty"] = self.display_qty
        if not isinstance(self.post_only, Unset):
            field_dict["post_only"] = self.post_only
        if not isinstance(self.reduce_only, Unset):
            field_dict["reduce_only"] = self.reduce_only
        if not isinstance(self.deadline, Unset):
            field_dict["deadline"] = self.deadline
        if not isinstance(self.fee_preference, Unset):
            field_dict["fee_preference"] = self.fee_preference
        if not isinstance(self.order_userref, Unset):
            field_dict["order_userref"] = self.order_userref
        if not isinstance(self.validate, Unset):
            field_dict["validate"] = self.validate
        if not isinstance(self.triggers, Unset):
            field_dict["triggers"] = self.triggers.to_dict()
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        triggers_raw = d.pop("triggers", UNSET)
        triggers: Unset | OrderTrigger = UNSET
        if not isinstance(triggers_raw, Unset):
            triggers = OrderTrigger.from_dict(triggers_raw)
        return cls(
            order_id=d.pop("order_id"),
            symbol=d.pop("symbol"),
            token=d.pop("token"),
            order_qty=d.pop("order_qty", UNSET),
            limit_price=d.pop("limit_price", UNSET),
            display_qty=d.pop("display_qty", UNSET),
            post_only=d.pop("post_only", UNSET),
            reduce_only=d.pop("reduce_only", UNSET),
            deadline=d.pop("deadline", UNSET),
            fee_preference=d.pop("fee_preference", UNSET),
            order_userref=d.pop("order_userref", UNSET),
            validate=d.pop("validate", UNSET),
            triggers=triggers,
        )


@_attrs_define
class CancelOrderParams:
    """Parameters for the cancel_order trading method.

    At least one of order_id or cl_ord_id must be provided.

    Attributes:
        token: Authentication token.
        order_id: List of order IDs to cancel.
        cl_ord_id: List of client order IDs to cancel.
    """

    token: str
    order_id: Unset | list[str] = UNSET
    cl_ord_id: Unset | list[str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {"token": self.token}
        if not isinstance(self.order_id, Unset):
            field_dict["order_id"] = self.order_id
        if not isinstance(self.cl_ord_id, Unset):
            field_dict["cl_ord_id"] = self.cl_ord_id
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            token=d.pop("token"),
            order_id=d.pop("order_id", UNSET),
            cl_ord_id=d.pop("cl_ord_id", UNSET),
        )


@_attrs_define
class CancelAllParams:
    """Parameters for the cancel_all trading method.

    Attributes:
        token: Authentication token.
    """

    token: str

    def to_dict(self) -> dict[str, Any]:
        return {"token": self.token}

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(token=d.pop("token"))


@_attrs_define
class BatchAddParams:
    """Parameters for the batch_add trading method.

    Attributes:
        symbol: Single currency pair for the entire batch.
        token: Authentication token.
        orders: List of 2-15 order parameter objects.
        deadline: Response deadline (RFC3339).
        validate: Validation-only mode.
    """

    symbol: str
    token: str
    orders: list[AddOrderParams] = _attrs_field(factory=list)
    deadline: Unset | str = UNSET
    validate: Unset | bool = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "symbol": self.symbol,
            "token": self.token,
            "orders": [o.to_dict() for o in self.orders],
        }
        if not isinstance(self.deadline, Unset):
            field_dict["deadline"] = self.deadline
        if not isinstance(self.validate, Unset):
            field_dict["validate"] = self.validate
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        orders = [AddOrderParams.from_dict(o) for o in d.pop("orders", [])]
        return cls(
            symbol=d.pop("symbol"),
            token=d.pop("token"),
            orders=orders,
            deadline=d.pop("deadline", UNSET),
            validate=d.pop("validate", UNSET),
        )


@_attrs_define
class BatchCancelParams:
    """Parameters for the batch_cancel trading method.

    Attributes:
        token: Authentication token.
        orders: List of order IDs to cancel.
        cl_ord_id: List of client order IDs to cancel.
    """

    token: str
    orders: list[str] = _attrs_field(factory=list)
    cl_ord_id: Unset | list[str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "token": self.token,
            "orders": self.orders,
        }
        if not isinstance(self.cl_ord_id, Unset):
            field_dict["cl_ord_id"] = self.cl_ord_id
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            token=d.pop("token"),
            orders=d.pop("orders", []),
            cl_ord_id=d.pop("cl_ord_id", UNSET),
        )


# ---------------------------------------------------------------------------
# Response results
# ---------------------------------------------------------------------------


@_attrs_define
class AddOrderResult:
    """Result from a successful add_order response.

    Attributes:
        order_id: Assigned order identifier.
        cl_ord_id: Client order ID if provided in request.
        order_userref: Client numeric reference if provided in request.
        warnings: List of warning messages.
    """

    order_id: str
    cl_ord_id: Unset | str = UNSET
    order_userref: Unset | int = UNSET
    warnings: Unset | list[str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {"order_id": self.order_id}
        if not isinstance(self.cl_ord_id, Unset):
            field_dict["cl_ord_id"] = self.cl_ord_id
        if not isinstance(self.order_userref, Unset):
            field_dict["order_userref"] = self.order_userref
        if not isinstance(self.warnings, Unset):
            field_dict["warnings"] = self.warnings
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            order_id=d.pop("order_id"),
            cl_ord_id=d.pop("cl_ord_id", UNSET),
            order_userref=d.pop("order_userref", UNSET),
            warnings=d.pop("warnings", UNSET),
        )


@_attrs_define
class EditOrderResult:
    """Result from a successful edit_order response.

    Edit is cancel-and-replace — a new order_id is assigned.

    Attributes:
        order_id: New order identifier.
        original_order_id: Identifier of the replaced order.
        warnings: List of warning messages.
    """

    order_id: str
    original_order_id: str
    warnings: Unset | list[str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "order_id": self.order_id,
            "original_order_id": self.original_order_id,
        }
        if not isinstance(self.warnings, Unset):
            field_dict["warnings"] = self.warnings
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            order_id=d.pop("order_id"),
            original_order_id=d.pop("original_order_id"),
            warnings=d.pop("warnings", UNSET),
        )


@_attrs_define
class CancelOrderResult:
    """Result from a successful cancel_order response.

    Attributes:
        order_id: Cancelled order identifier.
        cl_ord_id: Client order ID if applicable.
        warnings: List of warning messages.
    """

    order_id: str
    cl_ord_id: Unset | str = UNSET
    warnings: Unset | list[str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {"order_id": self.order_id}
        if not isinstance(self.cl_ord_id, Unset):
            field_dict["cl_ord_id"] = self.cl_ord_id
        if not isinstance(self.warnings, Unset):
            field_dict["warnings"] = self.warnings
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            order_id=d.pop("order_id"),
            cl_ord_id=d.pop("cl_ord_id", UNSET),
            warnings=d.pop("warnings", UNSET),
        )


@_attrs_define
class CancelAllResult:
    """Result from a successful cancel_all response.

    Attributes:
        count: Number of orders cancelled.
        warnings: List of warning messages.
    """

    count: int
    warnings: Unset | list[str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {"count": self.count}
        if not isinstance(self.warnings, Unset):
            field_dict["warnings"] = self.warnings
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            count=d.pop("count"),
            warnings=d.pop("warnings", UNSET),
        )


@_attrs_define
class BatchAddResult:
    """Result from a successful batch_add response.

    Attributes:
        orders: List of individual order results.
    """

    orders: list[AddOrderResult] = _attrs_field(factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"orders": [o.to_dict() for o in self.orders]}

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        orders = [AddOrderResult.from_dict(o) for o in d.pop("orders", [])]
        return cls(orders=orders)


@_attrs_define
class BatchCancelResult:
    """Result from a successful batch_cancel response.

    Attributes:
        count: Number of orders cancelled.
        warnings: List of warning messages.
    """

    count: int
    warnings: Unset | list[str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {"count": self.count}
        if not isinstance(self.warnings, Unset):
            field_dict["warnings"] = self.warnings
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            count=d.pop("count"),
            warnings=d.pop("warnings", UNSET),
        )
