"""Data models for OHLC candles feeds on websockets."""

from typing import Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field


@_attrs_define
class OHLC:
    """Open High Low Close (Candle) feed for a currency pair and interval period.

    When subscribed for OHLC, a snapshot of the last valid candle
    (irrespective of the endtime) will be sent, followed by updates
    to the running candle. For example, if a subscription is made to
    1 min candle and there have been no trades for 5 mins, a snapshot
    of the last 1 min candle from 5 mins ago will be published. The
    endtime can be used to determine that it is an old candle.

    Attributes:
        time: Candle last update time, in seconds since epoch.
        etime: End time of interval, in seconds since epoch.
        open: Open price of interval.
        high: High price within interval.
        low: Low price within interval.
        close: Close price of interval.
        vwap: Volume weighted average price within interval.
        volume: Accumulated volume within interval.
        count: Number of trades within interval.
    """

    time: float
    etime: float
    open: float
    high: float
    low: float
    close: float
    vwap: float
    volume: float
    count: int

    @classmethod
    def from_message(cls, message: list) -> Self:
        """Instantiate a OHLC object from the message context."""

        return cls(*message)


@_attrs_define
class OHLCMessage:
    """Message received for a OHLC subscription on currency pair.

    Attributes:
        channel_id: Channel ID of subscription - deprecated,
            use channelName and pair.
        ohlc: OHLC data for currency pair and interval period.
        channel_name: The name of the channel to which the message
            relates.
        currency_pair: The name of the currency pair to which the
            message relates.

    Example:
        ```json
        [
            42,
            [
                "1542057314.748456",
                "1542057360.435743",
                "3586.70000",
                "3586.70000",
                "3586.60000",
                "3586.60000",
                "3586.68894",
                "0.03373000",
                2
            ],
            "ohlc-5",
            "XBT/USD"
        ]
        ```
    """

    channel_id: int = _attrs_field()
    ohlc: OHLC = _attrs_field()
    channel_name: str = _attrs_field()
    currency_pair: str = _attrs_field()

    @classmethod
    def from_message(cls, message: list[Any]) -> Self:
        """Convert raw message from websocke to OHLCMessage."""
        channel_id = message[0]
        ohlc = OHLC.from_message(message[1])
        channel_name = message[2]
        currency_pair = message[3]
        return cls(
            channel_id=channel_id,
            ohlc=ohlc,
            channel_name=channel_name,
            currency_pair=currency_pair,
        )
