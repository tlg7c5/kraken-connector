"""Data models for openOrders private messasges on websockets."""

from datetime import datetime
from typing import Any, Dict, List, Self, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ...constants.trading import OrderStatus, OrderType, TypeOrder
from ...types import UNSET, Unset


@_attrs_define
class OrderDescription:
    """The description of the Order.

    Attributes:
        pair: The asset pair related to the order.
        position_id: Optional, position ID.
        type_order: The `TypeOrder` of the order (buy/sell).
        order_type: The `OrderType` of the order.
        price: The primary price of the order.
        price2: The secondary price of the order.
        leverage: The amount of leverage associated with the order.
        order: The order description.
        close: The conditional close order description, if conditional
            close is set.
    """

    pair: str
    position_id: Union[str, Unset]
    type_order: TypeOrder
    order_type: OrderType
    price: float
    price2: Union[float, Unset]
    leverage: Union[float, Unset]
    order: str
    close: Union[str, Unset]

    @classmethod
    def from_message(cls, message: Dict[str, Any]) -> Self:
        """Instantiate an OrderDescription object from the message context."""
        src_copy = message.copy()
        pair = src_copy.get("pair")
        position_id = src_copy.get("position", UNSET)
        type_order = src_copy.get("type")
        order_type = src_copy.get("ordertype")
        price = src_copy.get("price")
        price2 = src_copy.get("price2", UNSET)
        leverage = src_copy.get("leverage", UNSET)
        order = src_copy.get("order")
        close = src_copy.get("close", UNSET)

        return cls(
            pair=pair,
            position_id=position_id,
            type_order=TypeOrder(type_order),
            order_type=OrderType(order_type),
            price=float(price),
            price2=float(price2) if price2 else UNSET,
            leverage=float(leverage) if price2 else UNSET,
            order=order,
            close=close,
        )


@_attrs_define
class ConditionalCloseOrder:
    """The Order that is only placed contingent on the underlying order being filled.

    Attributes:
        order_type: The `OrderType` of the conditional close order.
        price: The primary price of the conditional close order.
        price2: The secondary price of the conditional close order.
        order_flags: Optional - comma delimited list of order flags,
            of the conditional close order:
            * viqc = volume in quote currency
            * fcib = prefer fee in base currency
            * fciq = prefer fee in quote currency
            * nompp = no market price protection
            * post = post only order (available when ordertype = limit)
    """

    order_type: OrderType
    price: float
    price2: Union[float, Unset]
    order_flags: str

    @classmethod
    def from_message(cls, message: Dict[str, Any]) -> Self:
        """Instantiate an ConditionalCloseOrder object from the message context."""
        src_copy = message.copy()
        order_type = src_copy.get("ordertype")
        price = src_copy.get("price")
        price2 = src_copy.get("price2", UNSET)
        order_flags = src_copy.get("oflags", "")

        return cls(
            order_type=OrderType(order_type),
            price=float(price),
            price2=float(price2) if price2 else UNSET,
            order_flags=order_flags,
        )


@_attrs_define
class Order:
    """An Order belonging to the authenticated user.

    The Order would be considered an OpenOrder, even if later closed or
    cancelled, as long as it was an open order at the time at which the
    openOrder feed was subscribed.

    Attributes:
        referral_id: Referral order transaction id that created this order.
        userref: The user reference ID.
        status: The `OrderStatus` of the order.
        open_time: Unix timestamp of when the order was placed.
        start_time: Unix timestamp of the order start time, if set.
        display_volume: Optional, dependent on whether order type is
            iceberg - the visible quantity for iceberg order types.
        display_volume_remain: Optional dependent on whether order
            type is iceberg - the visible quantity remaing in the
            order for iceberg order types.
        expire_time: Unix timestamp of order end time (if set).
        contingent: The conditional close order info object
            (if conditional close set).
        description: The order description info object.
        last_updated: The unix timestamp of last change (for updates).
        volume: The volume of order in base currency unless viqc
            (volume in quote currency) set in `order_flags`.
        volume_executed: The total volume executed so far in base currency
            unless viqc set in `order_flags`.
        cost: The total cost inquote currency, unless unless
            viqc set in `order_flags`.
        fee: The total fee in quote currency.
        average_price: The cumulative, average price in quote currency
            unless viqc flag set in `order_flags`.
        stop_price: The stop price in quote currency, for trailing stops.
        limit_price: The triggered limit price in quote currency,
            when limit based order type is triggered.
        misc: A comma delimited list of miscellaneous info:
            * stopped = triggered by stop price
            * touched = triggered by touch price
            * liquidation = liquidation
            * partial = partial fill
        order_flags: Optional - comma delimited list of order flags:
            * viqc = volume in quote currency
            * fcib = prefer fee in base currency
            * fciq = prefer fee in quote currency
            * nompp = no market price protection
            * post = post only order (available when ordertype = limit)
        time_in_force: Optional, the time-in-force of the order.
        cancel_reason: Optional, cancel reason,
            present for all cancellation updates (status="canceled")
            and for some close updates (status="closed")
        rate_count: Optional, rate-limit counter, present if requested in
            subscription request.  See [trading rate limits](https://support.kraken.com/hc/en-us/articles/360045239571)
    """

    referral_id: Union[str, Unset]
    userref: Union[int, Unset]
    status: OrderStatus
    open_time: Union[datetime, Unset]
    start_time: Union[datetime, Unset]
    display_volume: Union[float, Unset]
    display_volume_remain: Union[float, Unset]
    expire_time: Union[datetime, Unset]
    contingent: Union[ConditionalCloseOrder, Unset]
    description: Union[OrderDescription, Unset]
    last_updated: Union[datetime, Unset]
    volume: Union[float, Unset]
    volume_executed: Union[float, Unset]
    cost: Union[float, Unset]
    fee: Union[float, Unset]
    average_price: Union[float, Unset]
    stop_price: Union[float, Unset]
    limit_price: Union[float, Unset]
    misc: Union[str, Unset]
    order_flags: Union[str, Unset]
    time_in_force: Union[str, Unset]
    cancel_reason: Union[str, Unset]
    rate_count: Union[int, Unset]

    @classmethod
    def from_message(cls, message: Dict[str, Any]) -> Self:
        """Instantiate an Order object from the message context."""
        src_copy = message.copy()
        referral_id = src_copy.get("refid", UNSET)
        userref = src_copy.get("userref", UNSET)
        status = src_copy.get("status")
        open_time = src_copy.get("opentm", UNSET)
        start_time = src_copy.get("startm", UNSET)
        display_volume = src_copy.get("display_volume", UNSET)
        display_volume_remain = src_copy.get("display_volume_remain", UNSET)
        expire_time = src_copy.get("expiretm", UNSET)
        contingent = src_copy.get("contingent", UNSET)
        description = src_copy.get("descr", UNSET)
        last_updated = src_copy.get("lastupdated", UNSET)
        volume = src_copy.get("vol", UNSET)
        volume_executed = src_copy.get("vol_exec", UNSET)
        cost = src_copy.get("cost", UNSET)
        fee = src_copy.get("fee", UNSET)
        average_price = src_copy.get("avg_price", UNSET)
        stop_price = src_copy.get("stopprice", UNSET)
        limit_price = src_copy.get("limitprice", UNSET)
        misc = src_copy.get("misc", UNSET)
        order_flags = src_copy.get("oflags", UNSET)
        time_in_force = src_copy.get("timeinforce", UNSET)
        cancel_reason = src_copy.get("cancel_reason", UNSET)
        rate_count = src_copy.get("ratecount", UNSET)

        return cls(
            referral_id=referral_id,
            userref=int(userref) if userref else UNSET,
            status=OrderStatus(status),
            open_time=datetime.fromtimestamp(float(open_time)) if open_time else UNSET,
            start_time=datetime.fromtimestamp(float(start_time))
            if start_time
            else UNSET,
            display_volume=float(display_volume) if display_volume else UNSET,
            display_volume_remain=float(display_volume_remain)
            if display_volume_remain
            else UNSET,
            expire_time=datetime.fromtimestamp(float(expire_time))
            if expire_time
            else UNSET,
            contingent=ConditionalCloseOrder.from_message(contingent)
            if contingent
            else UNSET,
            description=OrderDescription.from_message(description)
            if description
            else UNSET,
            last_updated=datetime.fromtimestamp(float(last_updated))
            if last_updated
            else UNSET,
            volume=float(volume) if volume else UNSET,
            volume_executed=float(volume_executed) if volume_executed else UNSET,
            cost=float(cost) if cost else UNSET,
            fee=float(fee) if fee else UNSET,
            average_price=float(average_price) if average_price else UNSET,
            stop_price=float(stop_price) if stop_price else UNSET,
            limit_price=float(limit_price) if limit_price else UNSET,
            misc=misc,
            order_flags=order_flags,
            time_in_force=time_in_force,
            cancel_reason=cancel_reason,
            rate_count=int(rate_count) if rate_count else UNSET,
        )


@_attrs_define
class OpenOrderMessage:
    """Message received for openOrders subscription.

    Feed to show all the open orders belonging to the authenticated user.
    Initial snapshot will provide list of all open orders and then any
    updates to the open orders list will be sent. For status change updates,
    such as 'closed', the fields orderid and status will be present in the
    payload.

    The following order cancel reasons may appear in the openOrders feed:
    * Cannot trade with self
    * Order replaced
    * Post only order
    * User requested

    Attributes:
        open_orders: Dictionary of OpenOrders keyed to orderid, if any.
        channel_name: The name of the channel to which the message
            relates.
        sequence: The sequency number for the ownTrade subscription.

    Example:
        - full payload example
        ```json
        [
            [
                {
                "OGTT3Y-C6I3P-XRI6HX": {
                    "avg_price": "34.50000",
                    "cost": "0.00000",
                    "descr": {
                    "close": "",
                    "leverage": "0:1",
                    "order": "sell 10.00345345 XBT/EUR @ limit 34.50000 with 0:1 leverage",
                    "ordertype": "limit",
                    "pair": "XBT/EUR",
                    "price": "34.50000",
                    "price2": "0.00000",
                    "type": "sell"
                    },
                    "expiretm": "0.000000",
                    "fee": "0.00000",
                    "limitprice": "34.50000",
                    "misc": "",
                    "oflags": "fcib",
                    "opentm": "0.000000",
                    "refid": "OKIVMP-5GVZN-Z2D2UA",
                    "starttm": "0.000000",
                    "status": "open",
                    "stopprice": "0.000000",
                    "userref": 0,
                    "vol": "10.00345345",
                    "vol_exec": "0.00000000"
                }
                },
                {
                "OGTT3Y-C6I3P-XRI6HX": {
                    "avg_price": "5334.60000",
                    "cost": "0.00000",
                    "descr": {
                    "close": "",
                    "leverage": "0:1",
                    "order": "sell 0.00000010 XBT/EUR @ limit 5334.60000 with 0:1 leverage",
                    "ordertype": "limit",
                    "pair": "XBT/EUR",
                    "price": "5334.60000",
                    "price2": "0.00000",
                    "type": "sell"
                    },
                    "expiretm": "0.000000",
                    "fee": "0.00000",
                    "limitprice": "5334.60000",
                    "misc": "",
                    "oflags": "fcib",
                    "opentm": "0.000000",
                    "refid": "OKIVMP-5GVZN-Z2D2UA",
                    "starttm": "0.000000",
                    "status": "open",
                    "stopprice": "0.000000",
                    "userref": 0,
                    "vol": "0.00000010",
                    "vol_exec": "0.00000000"
                }
                },
                {
                "OGTT3Y-C6I3P-XRI6HX": {
                    "avg_price": "90.40000",
                    "cost": "0.00000",
                    "descr": {
                    "close": "",
                    "leverage": "0:1",
                    "order": "sell 0.00001000 XBT/EUR @ limit 90.40000 with 0:1 leverage",
                    "ordertype": "limit",
                    "pair": "XBT/EUR",
                    "price": "90.40000",
                    "price2": "0.00000",
                    "type": "sell"
                    },
                    "expiretm": "0.000000",
                    "fee": "0.00000",
                    "limitprice": "90.40000",
                    "misc": "",
                    "oflags": "fcib",
                    "opentm": "0.000000",
                    "refid": "OKIVMP-5GVZN-Z2D2UA",
                    "starttm": "0.000000",
                    "status": "open",
                    "stopprice": "0.000000",
                    "userref": 0,
                    "vol": "0.00001000",
                    "vol_exec": "0.00000000"
                }
                },
                {
                "OGTT3Y-C6I3P-XRI6HX": {
                    "avg_price": "9.00000",
                    "cost": "0.00000",
                    "descr": {
                    "close": "",
                    "leverage": "0:1",
                    "order": "sell 0.00001000 XBT/EUR @ limit 9.00000 with 0:1 leverage",
                    "ordertype": "limit",
                    "pair": "XBT/EUR",
                    "price": "9.00000",
                    "price2": "0.00000",
                    "type": "sell"
                    },
                    "expiretm": "0.000000",
                    "fee": "0.00000",
                    "limitprice": "9.00000",
                    "misc": "",
                    "oflags": "fcib",
                    "opentm": "0.000000",
                    "refid": "OKIVMP-5GVZN-Z2D2UA",
                    "starttm": "0.000000",
                    "status": "open",
                    "stopprice": "0.000000",
                    "userref": 0,
                    "vol": "0.00001000",
                    "vol_exec": "0.00000000"
                }
                }
            ],
            "openOrders",
            {
                "sequence": 234
            }
        ]
        ```
        - limited status-change payload
        ```json
        [
            [
                {
                "OGTT3Y-C6I3P-XRI6HX": {
                    "status": "closed"
                }
                },
                {
                "OGTT3Y-C6I3P-XRI6HX": {
                    "status": "closed"
                }
                }
            ],
            "openOrders",
            {
                "sequence": 59342
            }
        ]
        ```
    """

    open_orders: Dict[str, Order] = _attrs_field()
    channel_name: str = _attrs_field()
    sequence: int = _attrs_field()

    @classmethod
    def from_message(cls, message: List[Any]):
        """Convert raw message from websocket to OpenOrderMessage."""
        open_orders = {}
        for i in message[0]:
            open_orders |= {j: Order.from_message(i[j]) for j in i}
        channel_name = message[1]
        sequence = message[2]
        return cls(
            open_orders=open_orders,
            channel_name=channel_name,
            sequence=sequence,
        )
