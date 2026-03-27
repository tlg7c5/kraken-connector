"""Data models for ownTrades private messasges on websockets."""

from typing import Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ...constants.trading import OrderType, TypeOrder


@_attrs_define
class OwnTrade:
    """Trades on an account.

    Attributes:
        order_id: The Order responsible for execution of trade.
        position_id: Position trade id.
        pair: The currency pair of the trade.
        time: Unix timestamp of trade.
        type_order: The type of order, e.g. buy/sell.
        order_type: The order type, e.g. limit/market.
        price: The average price that the order was executed at in
            terms of the quote currency.
        cost: The total cost of the order in quote currency.
        fee: The total fee associated with the trade in terms of
            quote currency.
        volume: The volume in base currency.
        margin: The initial margin in quote currency.
        userref: The reference id assigned by the user associated
            with the order associated with the trade.
    """

    order_id: str | None
    position_id: str | None
    pair: str | None
    time: float | None
    type_order: TypeOrder
    order_type: OrderType
    price: float | None
    cost: float | None
    fee: float | None
    volume: float | None
    margin: float | None
    userref: int | None

    @classmethod
    def from_message(cls, message: dict[str, Any]) -> Self:
        """Instantiate a Spread object from the message context."""
        src_copy = message.copy()
        order_id = src_copy.get("ordertxid")
        position_id = src_copy.get("postxid")
        pair = src_copy.get("pair")
        time = src_copy.get("time")
        type_order = TypeOrder(src_copy.get("type"))
        order_type = OrderType(src_copy.get("orderType"))
        price = src_copy.get("price")
        cost = src_copy.get("cost")
        fee = src_copy.get("fee")
        volume = src_copy.get("vol")
        margin = src_copy.get("margin")
        userref = src_copy.get("userref")
        return cls(
            order_id=order_id,
            position_id=position_id,
            pair=pair,
            time=time,
            type_order=type_order,
            order_type=order_type,
            price=price,
            cost=cost,
            fee=fee,
            volume=volume,
            margin=margin,
            userref=userref,
        )


@_attrs_define
class OwnTradeMessage:
    """Message received for ownTrade subscription.

    On subscription last 50 trades for the user will be sent,
    followed by new trades.

    Attributes:
        trades: List of OwnTrades.
        channel_name: The name of the channel to which the message
            relates.
        sequence: The sequency number for the ownTrade subscription.

    Example:
        ```json
        [
            [
                {
                    "TDLH43-DVQXD-2KHVYY": {
                        "cost": "1000000.00000",
                        "fee": "1600.00000",
                        "margin": "0.00000",
                        "ordertxid": "TDLH43-DVQXD-2KHVYY",
                        "ordertype": "limit",
                        "pair": "XBT/EUR",
                        "postxid": "OGTT3Y-C6I3P-XRI6HX",
                        "price": "100000.00000",
                        "time": "1560516023.070651",
                        "type": "sell",
                        "vol": "1000000000.00000000"
                    }
                },
                {
                    "TDLH43-DVQXD-2KHVYY": {
                        "cost": "1000000.00000",
                        "fee": "600.00000",
                        "margin": "0.00000",
                        "ordertxid": "TDLH43-DVQXD-2KHVYY",
                        "ordertype": "limit",
                        "pair": "XBT/EUR",
                        "postxid": "OGTT3Y-C6I3P-XRI6HX",
                        "price": "100000.00000",
                        "time": "1560516023.070658",
                        "type": "buy",
                        "vol": "1000000000.00000000"
                    }
                },
                {
                "TDLH43-DVQXD-2KHVYY": {
                    "cost": "1000000.00000",
                    "fee": "1600.00000",
                    "margin": "0.00000",
                    "ordertxid": "TDLH43-DVQXD-2KHVYY",
                    "ordertype": "limit",
                    "pair": "XBT/EUR",
                    "postxid": "OGTT3Y-C6I3P-XRI6HX",
                    "price": "100000.00000",
                    "time": "1560520332.914657",
                    "type": "sell",
                    "vol": "1000000000.00000000"
                }
                },
                {
                "TDLH43-DVQXD-2KHVYY": {
                    "cost": "1000000.00000",
                    "fee": "600.00000",
                    "margin": "0.00000",
                    "ordertxid": "TDLH43-DVQXD-2KHVYY",
                    "ordertype": "limit",
                    "pair": "XBT/EUR",
                    "postxid": "OGTT3Y-C6I3P-XRI6HX",
                    "price": "100000.00000",
                    "time": "1560520332.914664",
                    "type": "buy",
                    "vol": "1000000000.00000000"
                }
                }
            ],
            "ownTrades",
            {
                "sequence": 2948
            }
        ]
        ```
    """

    trades: dict[str, OwnTrade] = _attrs_field()
    channel_name: str = _attrs_field()
    sequence: int = _attrs_field()

    @classmethod
    def from_message(cls, message: list[Any]) -> Self:
        """Convert raw message from websocket to OwnTradeMessage."""
        trades: dict[str, OwnTrade] = {}
        for i in message[0]:
            trades |= {j: OwnTrade.from_message(i[j]) for j in i}
        channel_name = message[1]
        sequence = message[2]
        return cls(
            trades=trades,
            channel_name=channel_name,
            sequence=sequence,
        )
