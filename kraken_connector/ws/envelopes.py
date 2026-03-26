"""Request/response envelope types for Kraken WebSocket API v2."""
from typing import Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset


@_attrs_define
class WSRequest:
    """Client to server request envelope.

    Attributes:
        method: The method name (subscribe, unsubscribe, add_order, etc.)
        params: Method-specific parameters.
        req_id: Optional client-originated ID echoed in the response.
    """

    method: str
    params: dict[str, Any] = _attrs_field(factory=dict)
    req_id: Unset | int = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "method": self.method,
            "params": self.params,
        }
        if not isinstance(self.req_id, Unset):
            field_dict["req_id"] = self.req_id
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        method = d.pop("method")
        params = d.pop("params", {})
        req_id = d.pop("req_id", UNSET)
        return cls(method=method, params=params, req_id=req_id)


@_attrs_define
class WSResponse:
    """Server to client success response envelope.

    Attributes:
        method: Echoes the request method.
        result: Response data (structure varies by method).
        success: Always True for success responses.
        time_in: Request receipt timestamp (RFC3339).
        time_out: Response transmission timestamp (RFC3339).
        req_id: Echoed from request if provided.
    """

    method: str
    result: dict[str, Any]
    success: bool
    time_in: str
    time_out: str
    req_id: Unset | int = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "method": self.method,
            "result": self.result,
            "success": self.success,
            "time_in": self.time_in,
            "time_out": self.time_out,
        }
        if not isinstance(self.req_id, Unset):
            field_dict["req_id"] = self.req_id
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        method = d.pop("method")
        result = d.pop("result")
        success = d.pop("success")
        time_in = d.pop("time_in")
        time_out = d.pop("time_out")
        req_id = d.pop("req_id", UNSET)
        return cls(
            method=method,
            result=result,
            success=success,
            time_in=time_in,
            time_out=time_out,
            req_id=req_id,
        )


@_attrs_define
class WSErrorResponse:
    """Server to client error response envelope.

    Attributes:
        method: Echoes the request method.
        error: Error message string.
        success: Always False for error responses.
        time_in: Request receipt timestamp (RFC3339).
        time_out: Response transmission timestamp (RFC3339).
        req_id: Echoed from request if provided.
    """

    method: str
    error: str
    success: bool
    time_in: str
    time_out: str
    req_id: Unset | int = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "method": self.method,
            "error": self.error,
            "success": self.success,
            "time_in": self.time_in,
            "time_out": self.time_out,
        }
        if not isinstance(self.req_id, Unset):
            field_dict["req_id"] = self.req_id
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        method = d.pop("method")
        error = d.pop("error")
        success = d.pop("success")
        time_in = d.pop("time_in")
        time_out = d.pop("time_out")
        req_id = d.pop("req_id", UNSET)
        return cls(
            method=method,
            error=error,
            success=success,
            time_in=time_in,
            time_out=time_out,
            req_id=req_id,
        )


@_attrs_define
class WSDataMessage:
    """Server to client channel data feed.

    Attributes:
        channel: The channel name (ticker, book, trade, etc.)
        type: Message type — "snapshot" or "update".
        data: Array of channel-specific data objects.
        sequence: Monotonic sequence number (present on private channels only).
    """

    channel: str
    type: str
    data: list[Any]
    sequence: Unset | int = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "channel": self.channel,
            "type": self.type,
            "data": self.data,
        }
        if not isinstance(self.sequence, Unset):
            field_dict["sequence"] = self.sequence
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        channel = d.pop("channel")
        type_ = d.pop("type")
        data = d.pop("data")
        sequence = d.pop("sequence", UNSET)
        return cls(channel=channel, type=type_, data=data, sequence=sequence)


@_attrs_define
class PingRequest:
    """Client ping request for connection keepalive.

    Attributes:
        req_id: Optional client-originated ID echoed in pong response.
    """

    req_id: Unset | int = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {"method": "ping"}
        if not isinstance(self.req_id, Unset):
            field_dict["req_id"] = self.req_id
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        req_id = d.pop("req_id", UNSET)
        return cls(req_id=req_id)


@_attrs_define
class PongResponse:
    """Server pong response to a client ping.

    Attributes:
        req_id: Echoed from ping request if provided.
        time_in: Request receipt timestamp (RFC3339).
        time_out: Response transmission timestamp (RFC3339).
    """

    req_id: Unset | int = UNSET
    time_in: Unset | str = UNSET
    time_out: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {"method": "pong"}
        if not isinstance(self.req_id, Unset):
            field_dict["req_id"] = self.req_id
        if not isinstance(self.time_in, Unset):
            field_dict["time_in"] = self.time_in
        if not isinstance(self.time_out, Unset):
            field_dict["time_out"] = self.time_out
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        d.pop("method", None)
        req_id = d.pop("req_id", UNSET)
        time_in = d.pop("time_in", UNSET)
        time_out = d.pop("time_out", UNSET)
        return cls(req_id=req_id, time_in=time_in, time_out=time_out)
