"""Constants related to Kraken Websockets."""
from enum import IntEnum, StrEnum


class EventType(StrEnum):
    """Event values for Websocket Responses."""

    HEARTBEAT = "heartbeat"
    PING = "ping"
    PONG = "pong"
    SUBSCRIBE = "subscribe"
    SUBSCRIPTION_STATUS = "subscriptionStatus"
    SYSTEM_STATUS = "systemStatus"
    UNSUBSCRIBE = "unsubscribe"

    def __str__(self) -> str:
        return str(self.value)


class MessageStatus(StrEnum):
    """Status sent in response to request from User.

    Members:
        OK: The request was successful.
        ERROR: There was an error processing the request.
    """

    OK = "ok"
    ERROR = "error"


class SystemStatus(StrEnum):
    """Status states for SystemStatus."""

    ONLINE = "online"
    MAINTENANCE = "maintenance"
    CANCEL_ONLY = "cancel_only"
    LIMIT_ONLY = "limit_only"
    POST_ONLY = "post_only"

    def __str__(self) -> str:
        return str(self.value)


class SubscriptionStatus(StrEnum):
    """Status states for Subscription."""

    ERROR = "error"
    SUBSCRIPTED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"

    def __str__(self) -> str:
        return str(self.value)


class SubscriptionType(StrEnum):
    """Types of Kraken Websocket Subscriptions."""

    BOOK = "book"
    OHLC = "ohlc"
    OPEN_ORDERS = "openOrders"
    OWN_TRADES = "ownTrades"
    SPREAD = "spread"
    TICKER = "ticker"
    TRADE = "trade"

    def __str__(self) -> str:
        return str(self.value)


class BookDepth(IntEnum):
    """Subscribeable levels for a BOOK subscription.

    Depth is defined by kraken as the total on each side of the order book.
    """

    TEN = 10
    TWENTY_FIVE = 25
    ONE_HUNDRED = 100
    FIVE_HUNDRED = 500
    ONE_THOUSAND = 1000

    def __str__(self) -> str:
        return str(self.value)


class OhlcInterval(IntEnum):
    """Subscribeable intervals for OHLC subscriptions.

    Values are interpreted as values in minutes.
    """

    ONE_MIN = 1
    FIVE_MIN = 5
    FIFTEEN_MIN = 15
    THIRTY_MIN = 30
    SIXTY_MIN = 60
    TWO_HUNDRED_FORTY_MIN = 240
    FOURTEEN_HUNDRED_FORTY_MIN = 1440
    TEN_THOUSAND_EIGHTY_MIN = 10080
    TWENTY_ONE_THOUSAND_SIX_HUNDRED_MIN = 21600

    ONE_HOUR = SIXTY_MIN
    FOUR_HOUR = TWO_HUNDRED_FORTY_MIN
    ONE_DAY = FOURTEEN_HUNDRED_FORTY_MIN
    SEVEN_DAY = TEN_THOUSAND_EIGHTY_MIN
    ONE_WEEK = TEN_THOUSAND_EIGHTY_MIN
    FIFTEEN_DAY = TWENTY_ONE_THOUSAND_SIX_HUNDRED_MIN

    def __str__(self) -> str:
        return str(self.value)
