"""Constants and enums for Kraken WebSocket API v2."""
from enum import StrEnum


class ChannelName(StrEnum):
    """WebSocket v2 channel names."""

    TICKER = "ticker"
    BOOK = "book"
    TRADE = "trade"
    OHLC = "ohlc"
    INSTRUMENT = "instrument"
    LEVEL3 = "level3"
    EXECUTIONS = "executions"
    BALANCES = "balances"
    HEARTBEAT = "heartbeat"
    STATUS = "status"

    def __str__(self) -> str:
        return str(self.value)


class MessageType(StrEnum):
    """Data message types (snapshot vs incremental update)."""

    SNAPSHOT = "snapshot"
    UPDATE = "update"

    def __str__(self) -> str:
        return str(self.value)


class MethodName(StrEnum):
    """WebSocket v2 method names for requests and responses."""

    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PING = "ping"
    PONG = "pong"
    ADD_ORDER = "add_order"
    AMEND_ORDER = "amend_order"
    EDIT_ORDER = "edit_order"
    CANCEL_ORDER = "cancel_order"
    CANCEL_ALL = "cancel_all"
    CANCEL_ALL_ORDERS_AFTER = "cancel_all_orders_after"
    BATCH_ADD = "batch_add"
    BATCH_CANCEL = "batch_cancel"

    def __str__(self) -> str:
        return str(self.value)


class SystemState(StrEnum):
    """Kraken system status values (v2 names)."""

    ONLINE = "online"
    MAINTENANCE = "maintenance"
    CANCEL_ONLY = "cancel_only"
    POST_ONLY = "post_only"

    def __str__(self) -> str:
        return str(self.value)


class OrderSide(StrEnum):
    """Order side for trading methods."""

    BUY = "buy"
    SELL = "sell"

    def __str__(self) -> str:
        return str(self.value)


class WSOrderType(StrEnum):
    """Order types for WS v2 trading methods."""

    LIMIT = "limit"
    MARKET = "market"
    ICEBERG = "iceberg"
    STOP_LOSS = "stop-loss"
    STOP_LOSS_LIMIT = "stop-loss-limit"
    TAKE_PROFIT = "take-profit"
    TAKE_PROFIT_LIMIT = "take-profit-limit"
    TRAILING_STOP = "trailing-stop"
    TRAILING_STOP_LIMIT = "trailing-stop-limit"
    SETTLE_POSITION = "settle-position"

    def __str__(self) -> str:
        return str(self.value)


class TimeInForce(StrEnum):
    """Time-in-force values for orders."""

    GTC = "gtc"
    GTD = "gtd"
    IOC = "ioc"

    def __str__(self) -> str:
        return str(self.value)


class ExecType(StrEnum):
    """Execution type values from the executions channel."""

    PENDING_NEW = "pending_new"
    NEW = "new"
    TRADE = "trade"
    FILLED = "filled"
    CANCELED = "canceled"
    EXPIRED = "expired"
    AMENDED = "amended"
    RESTATED = "restated"
    STATUS = "status"

    def __str__(self) -> str:
        return str(self.value)


class OrderStatus(StrEnum):
    """Order status values from the executions channel."""

    PENDING_NEW = "pending_new"
    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    EXPIRED = "expired"

    def __str__(self) -> str:
        return str(self.value)


class TriggerReference(StrEnum):
    """Trigger price reference for conditional orders."""

    INDEX = "index"
    LAST = "last"

    def __str__(self) -> str:
        return str(self.value)


class PriceType(StrEnum):
    """Price type for limit_price_type field."""

    STATIC = "static"
    PCT = "pct"
    QUOTE = "quote"

    def __str__(self) -> str:
        return str(self.value)


class FeePreference(StrEnum):
    """Fee currency preference for orders."""

    BASE = "base"
    QUOTE = "quote"

    def __str__(self) -> str:
        return str(self.value)


class STPType(StrEnum):
    """Self-trade prevention type."""

    CANCEL_NEWEST = "cancel_newest"
    CANCEL_OLDEST = "cancel_oldest"
    CANCEL_BOTH = "cancel_both"

    def __str__(self) -> str:
        return str(self.value)


class LiquidityIndicator(StrEnum):
    """Liquidity indicator for trade executions."""

    TAKER = "t"
    MAKER = "m"

    def __str__(self) -> str:
        return str(self.value)


class ConnectionState(StrEnum):
    """WebSocket connection state machine states."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"

    def __str__(self) -> str:
        return str(self.value)
