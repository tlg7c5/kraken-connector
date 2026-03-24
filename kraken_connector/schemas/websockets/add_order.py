"""Data models for addOrder private messasges on websockets."""

from typing import Any, Dict, List, Literal, Self, Union

from attrs import converters
from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ...constants.trading import OrderFlags, OrderType, TimeInForce, TypeOrder
from ...constants.websockets import MessageStatus
from ...types import UNSET, Unset
from ...utils.converters import boolean_to_message, order_flags_to_message


@_attrs_define
class CreateOrder:
    """An order created by the authenticated user to add to the exchange order book.

    Note:
        Either `price` or `price2` can be preceded by `+`, `-`, or `#` to specify the order price as an offset
        relative to the last traded price. `+` adds the amount to, and `-` subtracts the amount from the last traded
        price. `#` will either add or subtract the amount to the last traded price, depending on the direction and order
        type used. Relative prices can be suffixed with a `%` to signify the relative amount as a percentage.

    Attributes:
        event: Literal 'addOrder'
        token: The session token string used for authentication.
        request_id: Optional, client originated requestID sent in acknowledgement
            in the message response to a received addOrder event.
        order_type: The `OrderType` (limit/market/etc).
        type_order: The `TypeOrder` (buy/sell).
        pair: The currency pair.
        price: The price associated with the Order.  Optional depending on `OrderType`.
            Acts as the limit price for `limit` orders and the trigger price for `stop-loss`,
            `stop-loss-limit`, `take-profit` and `take-profit-limit` orders.
        price2: The secondary price of the Order.  Optional depending on `OrderType`.
            It is the limit price for `stop-loss-limit` and `take-profit-limit` orders.
        volume: The order volume in base currency.
        leverage: Optional, amount of leverage desired.  Default is None.
        reduce_only: Optional, boolean, if True, order will only reduce a currently open position,
            not increase it or open a new position.  Default is False.
        order_flags: Optional, list of `OrderFlags`.
        start_time: Optional - scheduled start time for when the Order takes effect.
            If present, should be in one of the following forms:
            * 0 = now (default)
            * +<n> = schedule start time <n> seconds from now
            * <n> = unix timestamp of start time
        expire_time: Optional - expiration time of the Order.
            If present, should be in one of the following forms:
            * 0 = now (default)
            * +<n> = expire <n> seconds from now
            * <n> = unix timestamp of expiration time
        deadline: Optional - RFC3339 timestamp (e.g. 2021-04-01T00:18:45Z). Range of valid offsets
            from now between 500 milliseconds to 60 seconds, default is 5 seconds. The engine will
            prevent this order from matching after this time, it provides protection against
            latency on time sensitive orders.
        userref: Optional, user reference ID that is an integer.
        validate: Optional, flag to only validate the inputs of the message without creating an
            actual order.  Essentially, it is for testing.
        conditional_close_order_type: Optional, conditional close order to attached to the Order
            being created.
        conditional_close_price: Optional, price of the conditional close order.
        conditional_close_price2: Optional, secondary price of the conditional close order.
        time_in_force: Optional, `TimeInForce` of the order.  Default is GOOD_TIL_CANCELLED.
    """

    token: str
    order_type: OrderType
    type_order: TypeOrder
    pair: str
    volume: float = _attrs_field(converter=float)
    request_id: Union[int, Unset] = _attrs_field(
        default=UNSET, converter=converters.optional(int)
    )
    price: Union[float, Unset] = _attrs_field(
        default=UNSET, converter=converters.optional(float)
    )
    price2: Union[float, Unset] = _attrs_field(
        default=UNSET, converter=converters.optional(float)
    )
    leverage: Union[float, Unset] = _attrs_field(
        default=UNSET, converter=converters.optional(float)
    )
    reduce_only: Union[Unset, bool] = _attrs_field(
        default=UNSET, converter=converters.optional(converters.to_bool)
    )
    order_flags: Union[Unset, List[OrderFlags]] = _attrs_field(
        default=UNSET, factory=list
    )
    start_time: Union[str, Unset] = UNSET
    expire_time: Union[str, Unset] = UNSET
    deadline: Union[str, Unset] = UNSET
    userref: Union[int, Unset] = _attrs_field(
        default=UNSET, converter=converters.optional(int)
    )
    validate: Union[bool, Unset] = _attrs_field(
        default=UNSET, converter=converters.optional(converters.to_bool)
    )
    conditional_close_order_type: Union[OrderType, Unset] = UNSET
    conditional_close_price: Union[float, Unset] = _attrs_field(
        default=UNSET, converter=converters.optional(float)
    )
    conditional_close_price2: Union[float, Unset] = _attrs_field(
        default=UNSET, converter=converters.optional(float)
    )
    time_in_force: Union[TimeInForce, Unset] = UNSET
    _event: Literal["addOrder"] = "addOrder"

    @classmethod
    def from_dict(cls, values: Dict[str, Any]) -> Self:
        """Generates object to create order from dictary of values.

        Args:
            values: Key/Value dictionary of values.

        Returns:
            A CreateOrder object.
        """
        return cls(**values)

    def to_payload(self) -> dict[str, Any]:
        """Generate message payload to create order on exchange.

        Example:
            - minimal values

            ```json
            {
                "event": "addOrder",
                "ordertype": "limit",
                "pair": "XBT/USD",
                "price": "9000",
                "token": "0000000000000000000000000000000000000000",
                "type": "buy",
                "volume": "10.123"
            }
            ```

            - conditional close

            ```json
            {
                "close[ordertype]": "limit",
                "close[price]": "9100",
                "event": "addOrder",
                "ordertype": "limit",
                "pair": "XBT/USD",
                "price": "9000",
                "token": "0000000000000000000000000000000000000000",
                "type": "buy",
                "volume": "10"
            }
            ```

        Returns:
            The createOrder object ready for transmission over websockets tp Kraken.
        """

        order_type = str(self.order_type)
        type_order = str(self.type_order)
        volume = str(self.volume)

        payload = {
            "event": self._event,
            "token": self.token,
            "ordertype": order_type,
            "type": type_order,
            "pair": self.pair,
            "volume": volume,
        }

        if not isinstance(self.request_id, Unset):
            payload |= {"reqid": str(self.request_id)}
        if not isinstance(self.price, Unset):
            payload |= {"price": str(self.price)}
        if not isinstance(self.price2, Unset):
            payload |= {"price2": str(self.price2)}
        if not isinstance(self.leverage, Unset):
            payload |= {"leverage": str(self.leverage)}
        if not isinstance(self.reduce_only, Unset):
            payload |= {"reduce_only": boolean_to_message(self.reduce_only)}
        if not isinstance(self.order_flags, Unset):
            payload |= {"oflags": order_flags_to_message(self.order_flags)}
        if not isinstance(self.order_flags, Unset):
            payload |= {"oflags": order_flags_to_message(self.order_flags)}
        if not isinstance(self.start_time, Unset):
            payload |= {"starttm": str(self.start_time)}
        if not isinstance(self.expire_time, Unset):
            payload |= {"expiretm": str(self.expire_time)}
        if not isinstance(self.deadline, Unset):
            payload |= {"deadline": str(self.deadline)}
        if not isinstance(self.userref, Unset):
            payload |= {"userref": str(int(self.userref))}
        if not isinstance(self.validate, Unset):
            payload |= {"validate": boolean_to_message(self.validate)}
        if not isinstance(self.conditional_close_order_type, Unset):
            payload |= {"close[ordertype]": str(self.conditional_close_order_type)}
        if (
            not isinstance(self.conditional_close_price, Unset)
            and self.conditional_close_order_type
        ):
            payload |= {"close[price]": str(self.conditional_close_price)}
        if (
            not isinstance(self.conditional_close_price2, Unset)
            and self.conditional_close_order_type
            and self.conditional_close_price
        ):
            payload |= {"close[price2]": str(self.conditional_close_price2)}
        if not isinstance(self.time_in_force, Unset):
            payload |= {"timeinforce": str(self.time_in_force)}

        return payload


@_attrs_define
class CreateOrderResponse:
    """A response from Kraken to a request to create a new order.

    Examples:
        - successful request response

        ```json
        {
            "descr": "buy 0.01770000 XBTUSD @ limit 4000",
            "event": "addOrderStatus",
            "status": "ok",
            "txid": "ONPNXH-KMKMU-F4MR5V"
        }
        ```

        - unsuccessful request response

        ```json
        {
            "errorMessage": "EOrder:Order minimum not met",
            "event": "addOrderStatus",
            "status": "error"
        }
        ```

    Returns:
        _description_
    """

    event: Literal["addOrderStatus"]
    status: MessageStatus
    request_id: Union[Unset, int] = _attrs_field(
        default=UNSET, converter=converters.optional(int)
    )
    order_id: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    error_message: Union[Unset, str] = UNSET

    @classmethod
    def from_message(cls, message: Dict[str, Any]) -> Self:
        """Converts message received by websocket to object.

        The message will have a description, order_id and request_id,
        only if the status is 'ok'.  Otherwise, it will have an
        error_message set on the response object.

        Args:
            message: The message received from Kraken via websocket.

        Returns:
            _description_
        """
        _message = message.copy()
        _response = {
            "event": _message.get("event"),
            "status": MessageStatus(_message.get("status")),
            "order_id": _message.get("txid", UNSET),
            "description": _message.get("descr", UNSET),
            "error_message": _message.get("errorMessage", UNSET),
        }

        return cls(**_response)
