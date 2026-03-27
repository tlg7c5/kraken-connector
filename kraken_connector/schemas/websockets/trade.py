"""Data models for trade messages on websockets."""

from typing import Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ...constants.trading import OrderType, TypeOrder


@_attrs_define
class Trade:
    """A trade on the exchange.

    Attributes:
        price: Price
        volume: Volume
        time: Time, seconds since epoch
        side: Triggering order side, buy/sell
        order_type: Triggering order type market/limit
        misc: Miscellaneous
    """

    price: float
    volume: float
    time: float
    side: TypeOrder
    order_type: OrderType
    misc: str

    @classmethod
    def from_message(cls, message: list) -> Self:
        """Instantiate a OHLC object from the message context."""

        return cls(*message)


@_attrs_define
class TradeMessage:
    """Message received for a trade subscription on currency pair.

    Attributes:
        channel_id: Channel ID of subscription - deprecated,
            use channelName and pair.
        trade: Trade data for currency pair.
        channel_name: The name of the channel to which the message
            relates.
        currency_pair: The name of the currency pair to which the
            message relates.

    Example:
        ```json
        [
            0,
            [
                [
                "5541.20000",
                "0.15850568",
                "1534614057.321597",
                "s",
                "l",
                ""
                ],
                [
                "6060.00000",
                "0.02455000",
                "1534614057.324998",
                "b",
                "l",
                ""
                ]
            ],
            "trade",
            "XBT/USD"
        ]
        ```
    """

    channel_id: int = _attrs_field()
    trade: Trade = _attrs_field()
    channel_name: str = _attrs_field()
    currency_pair: str = _attrs_field()

    @classmethod
    def from_message(cls, message: list[Any]) -> Self:
        """Convert raw message from websocke to OHLCMessage."""
        channel_id = message[0]
        trade = Trade.from_message(message[1])
        channel_name = message[2]
        currency_pair = message[3]
        return cls(
            channel_id=channel_id,
            trade=trade,
            channel_name=channel_name,
            currency_pair=currency_pair,
        )
