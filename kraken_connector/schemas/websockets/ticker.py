"""Data models for ticker messages on websockets."""

from typing import Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field


@_attrs_define
class OrderBookEntry:
    """An entry on an OrderBook.

    Attributes:
        price: The price associated with the entry.
        whole_lot_volume: The lot volume expressed as an integer.
        lot_volume: The lot volume as a float.
    """

    price: float = _attrs_field()
    whole_lot_volume: int = _attrs_field()
    lot_volume: float = _attrs_field()

    @classmethod
    def from_message(cls, message) -> Self:
        """Instantiate a OrderBookEntry obj from the message context."""
        return cls(*message)


@_attrs_define
class Close:
    """The close of a ticker."""

    price: float
    lot_volume: float

    @classmethod
    def from_message(cls, message) -> Self:
        """Instantiate a Close object from the message context."""
        return cls(*message)


@_attrs_define
class GenericTickerValueFloat:
    """Values that are expressed in terms of today and last24 as floats."""

    today: float
    last_24_hours: float

    @classmethod
    def from_message(cls, message: list[Any]) -> Self:
        """Instantiate a GenericTickerValue object from the message context."""
        return cls(*message)


@_attrs_define
class GenericTickerValueInt:
    """Values that are expressed in terms of today and last24 as floats."""

    today: int
    last_24_hours: int

    @classmethod
    def from_message(cls, message: list[Any]) -> Self:
        """Instantiate a GenericTickerValue object from the message context."""
        return cls(*message)


@_attrs_define
class Ticker:
    """Ticker information on currency pair.

    Attributes:
        a: Ask
        b: Bid
        c: Close
        v: Volume
        p: Volume weighted average price
        t: Number of trades
        l: Low price
        h: High price
        o: Open price
    """

    ask: OrderBookEntry = _attrs_field(alias="a")
    bid: OrderBookEntry = _attrs_field(alias="b")
    close: Close = _attrs_field(alias="c")
    volume: GenericTickerValueFloat = _attrs_field(alias="v")
    volume_weighted_average_price: GenericTickerValueFloat = _attrs_field(alias="p")
    number_trades: GenericTickerValueInt = _attrs_field(alias="t")
    low: GenericTickerValueFloat = _attrs_field(alias="l")
    high: GenericTickerValueFloat = _attrs_field(alias="h")
    open: GenericTickerValueFloat = _attrs_field(alias="o")

    @classmethod
    def from_message(cls, message: dict[str, Any]) -> Self:
        """Instantiate a GenericTickerValue object from the message context."""
        d = message.copy()
        a = OrderBookEntry.from_message(d.pop("a"))
        b = OrderBookEntry.from_message(d.pop("b"))
        c = Close.from_message(d.pop("c"))
        v = GenericTickerValueFloat.from_message(d.pop("v"))
        p = GenericTickerValueFloat.from_message(d.pop("p"))
        t = GenericTickerValueInt.from_message(d.pop("t"))
        l = GenericTickerValueFloat.from_message(d.pop("l"))
        h = GenericTickerValueFloat.from_message(d.pop("h"))
        o = GenericTickerValueFloat.from_message(d.pop("o"))
        return cls(a=a, b=b, c=c, v=v, p=p, t=t, l=l, h=h, o=o)


@_attrs_define
class TickerMessage:
    """Message received for a ticker subscription. on currency pair.

    Attributes:
        channel_id: Channel ID of subscription - deprecated,
            use channelName and pair.
        ticker: Ticker information on currency pair.
        channel_name: The name of the channel to which the message
            relates.
        currency_pair: The name of the currency pair to which the
            message relates.

    Example:
        ```json
        [
            0,
            {
                "a": [
                "5525.40000",
                1,
                "1.000"
                ],
                "b": [
                "5525.10000",
                1,
                "1.000"
                ],
                "c": [
                "5525.10000",
                "0.00398963"
                ],
                "h": [
                "5783.00000",
                "5783.00000"
                ],
                "l": [
                "5505.00000",
                "5505.00000"
                ],
                "o": [
                "5760.70000",
                "5763.40000"
                ],
                "p": [
                "5631.44067",
                "5653.78939"
                ],
                "t": [
                11493,
                16267
                ],
                "v": [
                "2634.11501494",
                "3591.17907851"
                ]
            },
            "ticker",
            "XBT/USD"
        ]
        ```
    """

    channel_id: int = _attrs_field()
    ticker: Ticker = _attrs_field()
    channel_name: str = _attrs_field()
    currency_pair: str = _attrs_field()

    @classmethod
    def from_message(cls, message: list[Any]):
        """Convert raw message from websocke to TicketMessage."""
        channel_id = message[0]
        ticker = Ticker.from_message(message[1])
        channel_name = message[2]
        currency_pair = message[3]
        return cls(
            channel_id=channel_id,
            ticker=ticker,
            channel_name=channel_name,
            currency_pair=currency_pair,
        )
