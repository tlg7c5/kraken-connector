"""Data models for spread feed messasges on websockets."""

from typing import Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field


@_attrs_define
class Spread:
    """The spread for a currency pair.

    Attributes:
        bid:
        ask:
        timestamp:
        bid_volume:
        ask_volume:
    """

    bid: float
    ask: float
    timestamp: float
    bid_volume: float
    ask_volume: float

    @classmethod
    def from_message(cls, message: list) -> Self:
        """Instantiate a Spread object from the message context."""

        return cls(*message)


@_attrs_define
class SpreadMessage:
    """Message received for a spread subscription on currency pair.

    Attributes:
        channel_id: Channel ID of subscription - deprecated,
            use channelName and pair.
        spread: Spread for a currency pair.
        channel_name: The name of the channel to which the message
            relates.
        currency_pair: The name of the currency pair to which the
            message relates.

    Example:
        ```json
        [
            0,
            [
                "5698.40000",
                "5700.00000",
                "1542057299.545897",
                "1.01234567",
                "0.98765432"
            ],
            "spread",
            "XBT/USD"
        ]
        ```
    """

    channel_id: int = _attrs_field()
    spread: Spread = _attrs_field()
    channel_name: str = _attrs_field()
    currency_pair: str = _attrs_field()

    @classmethod
    def from_message(cls, message: list[Any]) -> Self:
        """Convert raw message from websocke to OHLCMessage."""
        channel_id = message[0]
        spread = Spread.from_message(message[1])
        channel_name = message[2]
        currency_pair = message[3]
        return cls(
            channel_id=channel_id,
            spread=spread,
            channel_name=channel_name,
            currency_pair=currency_pair,
        )
