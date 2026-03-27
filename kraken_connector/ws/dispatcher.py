"""Message dispatcher for Kraken WebSocket API v2.

Routes raw JSON strings to typed model instances.
"""
import json
from typing import Any, Union

from ..types import UNSET
from .book import BookChecksumEvent
from .channels.balances import BalanceLedgerUpdate, BalanceSnapshot
from .channels.book import BookData
from .channels.executions import ExecutionData
from .channels.heartbeat import HeartbeatMessage
from .channels.instrument import InstrumentData
from .channels.ohlc import OHLCData
from .channels.status import StatusData
from .channels.ticker import TickerData
from .channels.trade import TradeData
from .envelopes import PongResponse, WSDataMessage, WSErrorResponse, WSResponse
from .sequence import SequenceGapEvent

# Union of all possible return types from parse_message.
WSMessage = Union[
    HeartbeatMessage,
    WSDataMessage,
    PongResponse,
    WSResponse,
    WSErrorResponse,
    SequenceGapEvent,
    BookChecksumEvent,
]

# Channel name → data item deserializer.
_CHANNEL_PARSERS: dict[str, Any] = {
    "ticker": TickerData.from_dict,
    "book": BookData.from_dict,
    "trade": TradeData.from_dict,
    "ohlc": OHLCData.from_dict,
    "status": StatusData.from_dict,
}

# Channels where snapshot and update use different models.
_BALANCE_SNAPSHOT_TYPES = ("snapshot",)


def _parse_data_items(channel: str, msg_type: str, raw_items: list[Any]) -> list[Any]:
    """Deserialize data array items into typed models."""
    # Instrument channel: single object with assets + pairs, not a list of items.
    if channel == "instrument":
        return [InstrumentData.from_dict(item) for item in raw_items]

    # Executions channel: always ExecutionData.
    if channel == "executions":
        return [ExecutionData.from_dict(item) for item in raw_items]

    # Balances channel: snapshot vs ledger update use different models.
    if channel == "balances":
        if msg_type in _BALANCE_SNAPSHOT_TYPES:
            return [BalanceSnapshot.from_dict(item) for item in raw_items]
        return [BalanceLedgerUpdate.from_dict(item) for item in raw_items]

    # Standard channels with a single model per item.
    parser = _CHANNEL_PARSERS.get(channel)
    if parser is not None:
        return [parser(item) for item in raw_items]

    # Unknown channel — return raw dicts.
    return raw_items


def parse_message(raw: str) -> WSMessage:
    """Route a raw JSON string from Kraken WS v2 to a typed model.

    Routing logic:
        1. ``"channel" == "heartbeat"`` → :class:`HeartbeatMessage`
        2. ``"channel"`` present with ``"data"`` → :class:`WSDataMessage`
           with typed data items
        3. ``"method" == "pong"`` → :class:`PongResponse`
        4. ``"success" == True`` → :class:`WSResponse`
        5. ``"success" == False`` → :class:`WSErrorResponse`

    For data messages, the ``data`` list items are deserialized into
    the appropriate channel model.  Response envelopes keep their
    ``result`` dict untyped — callers correlate ``req_id`` to determine
    the expected result type.

    Args:
        raw: Raw JSON string received from the WebSocket connection.

    Returns:
        A typed message model instance.

    Raises:
        ValueError: If the message cannot be classified.
        json.JSONDecodeError: If the input is not valid JSON.
    """
    msg: dict[str, Any] = json.loads(raw)

    # 1. Heartbeat — minimal message with just "channel": "heartbeat".
    channel = msg.get("channel")
    if channel == "heartbeat":
        return HeartbeatMessage.from_dict(msg)

    # 2. Data feed — has "channel" and "data".
    if channel is not None and "data" in msg:
        msg_type = msg.get("type", "update")
        typed_data = _parse_data_items(channel, msg_type, msg["data"])
        sequence = msg.get("sequence", UNSET)
        return WSDataMessage(
            channel=channel,
            type=msg_type,
            data=typed_data,
            sequence=sequence,
        )

    # 3. Pong response.
    if msg.get("method") == "pong":
        return PongResponse.from_dict(msg)

    # 4/5. Success or error response.
    if "success" in msg:
        if msg["success"]:
            return WSResponse.from_dict(msg)
        return WSErrorResponse.from_dict(msg)

    raise ValueError(f"Unrecognized WebSocket v2 message: {raw[:200]}")
