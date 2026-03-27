"""Status channel data model for Kraken WebSocket API v2."""
from typing import Any, Self

from attrs import define as _attrs_define


@_attrs_define
class StatusData:
    """System status data sent on connect and on state changes.

    Attributes:
        system: System state ("online", "maintenance", "cancel_only", "post_only").
        api_version: API version string (e.g. "v2").
        connection_id: Unique connection identifier.
        version: Server version string.
    """

    system: str
    api_version: str
    connection_id: int
    version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "system": self.system,
            "api_version": self.api_version,
            "connection_id": self.connection_id,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            system=d.pop("system"),
            api_version=d.pop("api_version"),
            connection_id=d.pop("connection_id"),
            version=d.pop("version"),
        )
