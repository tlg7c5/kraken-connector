"""Heartbeat channel model for Kraken WebSocket API v2."""
from typing import Any, Self

from attrs import define as _attrs_define


@_attrs_define
class HeartbeatMessage:
    """Automatic heartbeat sent when no other data is flowing (~1/sec).

    The heartbeat message has no type or data fields — just a channel name.

    Attributes:
        channel: Always "heartbeat".
    """

    channel: str = "heartbeat"

    def to_dict(self) -> dict[str, Any]:
        return {"channel": self.channel}

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        return cls(channel=src_dict.get("channel", "heartbeat"))
