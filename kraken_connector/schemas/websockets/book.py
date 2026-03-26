"""Data models for Order book subscription messasges on websockets."""

from typing import Any, Literal, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ...types import UNSET, Unset


@_attrs_define
class PriceLevel:
    """A price level on the order book of a currency pair.

    Note:
        The values are strings although they always hold a float value.
        This is needed to perform the checksum calculation for the
        orderbook.

    Attributes:
        price: Price level
        volume: Volume at price level.  For updates, a
            volume = 0 signals level removal and deletion from
            the order book.
        timestamp: The time price level was last updated, in
            seconds since epoch.
        update_type: Optional value that is passed in as a literal
            'r' to signal the update is a republished update.
    """

    price: str
    volume: str
    timestamp: str
    update_type: Literal["r"] | None = None

    @classmethod
    def from_message(cls, message: list) -> Self:
        """Instantiate a PriceLevel object from the message context."""
        return cls(*message)


@_attrs_define
class OrderBookSnapshot:
    """An initial snapshot of an Order Book for a currency pair.

    Attributes:
        ask_side: List of price levels, ascending from best ask.
        bid_side: List of price levels, descending from best bid.
    """

    ask_side: list[PriceLevel] = _attrs_field(alias="as", factory=list)
    bid_side: list[PriceLevel] = _attrs_field(alias="bs", factory=list)

    @classmethod
    def from_message(cls, message: dict) -> Self:
        """Instantiate a OrderBookUpdate object from the message context."""
        message_copy = message.copy()
        ask_side = [PriceLevel.from_message(i) for i in message_copy.get("as", [])]
        bid_side = [PriceLevel.from_message(i) for i in message_copy.get("bs", [])]
        return cls(**{"as": ask_side, "bs": bid_side})


@_attrs_define
class OrderBookUpdate:
    """An update to the Order Book for a currency pair.

    Attributes:
        ask_updates: List of price levels, ascending from best ask.
        bid_updates: List of price levels, descending from best bid.
        checksum: Optional, book checksum as a quoted unsigned
            32-bit integer, present only within the last update
            container in the message. See [calculation details](https://docs.kraken.com/websockets/#book-checksum).
    """

    ask_updates: list[PriceLevel] = _attrs_field(alias="a", factory=list)
    bid_updates: list[PriceLevel] = _attrs_field(alias="b", factory=list)
    checksum: int | Unset = _attrs_field(alias="c", default=UNSET)

    @classmethod
    def from_message(cls, message: dict) -> Self:
        """Instantiate a OrderBookUpdate object from the message context."""
        message_copy = message.copy()
        ask_container = {}
        bid_container = {}
        if len(message_copy) == 5:
            ask_container = message_copy[1]
            bid_container = message_copy[2]
            checksum = bid_container.pop("c", UNSET)
        elif "a" in message_copy[1]:
            ask_container = message_copy[1]
            checksum = ask_container.pop("c", UNSET)
        else:
            bid_container = message_copy[1]
            checksum = bid_container.pop("c", UNSET)

        ask_updates = [PriceLevel.from_message(i) for i in ask_container.get("a", [])]
        bid_updates = [PriceLevel.from_message(i) for i in bid_container.get("b", [])]
        return cls(a=ask_updates, b=bid_updates, c=checksum)


@_attrs_define
class OrderBookMessage:
    """Message received for an order book subscription on currency pair.

    On subscription, a snapshot will be published at the specified depth,
    following the snapshot, level updates will be published

    Attributes:
        channel_id: Channel ID of subscription - deprecated,
            use channelName and pair.
        order_book_update: The updates to an order book for a currency pair.
        channel_name: The name of the channel to which the message
            relates.
        currency_pair: The name of the currency pair to which the
            message relates.

    Example:
        - Snapshot

        ```json
        [
            0,
            {
                "as": [
                [
                    "5541.30000",
                    "2.50700000",
                    "1534614248.123678"
                ],
                [
                    "5541.80000",
                    "0.33000000",
                    "1534614098.345543"
                ],
                [
                    "5542.70000",
                    "0.64700000",
                    "1534614244.654432"
                ]
                ],
                "bs": [
                [
                    "5541.20000",
                    "1.52900000",
                    "1534614248.765567"
                ],
                [
                    "5539.90000",
                    "0.30000000",
                    "1534614241.769870"
                ],
                [
                    "5539.50000",
                    "5.00000000",
                    "1534613831.243486"
                ]
                ]
            },
            "book-100",
            "XBT/USD"
        ]
        ```

        - Update

        ```json
        [
            1234,
            {
                "a": [
                [
                    "5541.30000",
                    "2.50700000",
                    "1534614248.456738"
                ],
                [
                    "5542.50000",
                    "0.40100000",
                    "1534614248.456738"
                ]
                ]
            },
            {
                "b": [
                [
                    "5541.30000",
                    "0.00000000",
                    "1534614335.345903"
                ]
                ],
                "c": "974942666"
            },
            "book-10",
            "XBT/USD"
        ]
        ```

        - Republished Update

        ```json
        [
            1234,
            {
                "a": [
                [
                    "5541.30000",
                    "2.50700000",
                    "1534614248.456738",
                    "r"
                ],
                [
                    "5542.50000",
                    "0.40100000",
                    "1534614248.456738",
                    "r"
                ]
                ],
                "c": "974942666"
            },
            "book-25",
            "XBT/USD"
        ]
        ```
    """

    channel_id: int = _attrs_field()
    order_book_update: OrderBookSnapshot | OrderBookUpdate = _attrs_field()
    channel_name: str = _attrs_field()
    currency_pair: str = _attrs_field()

    @classmethod
    def from_message(cls, message: list[Any]):
        """Convert raw message from websocke to OHLCMessage."""
        chanel_id = message[0]
        if "as" in message[1]:
            order_book_update = OrderBookSnapshot.from_message(message[1])
        else:
            order_book_update = OrderBookUpdate.from_message(message[1])
        channel_name = message[2]
        currency_pair = message[3]
        return cls(
            channel_id=chanel_id,
            order_book_update=order_book_update,
            channel_name=channel_name,
            currency_pair=currency_pair,
        )
