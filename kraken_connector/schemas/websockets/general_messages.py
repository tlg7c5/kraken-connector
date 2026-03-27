"""General Messages as defined by Kraken Websockets API 1.9.1.

Note:
    All general messages received through Kraken websockets are dictionary
    objects with the value set on the 'event' key dictating the type of message.
"""
import logging
from typing import Any, LiteralString, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ...constants.websockets import EventType, SubscriptionStatus, SystemStatus
from ...types import UNSET, Unset
from ...utils.validators import _check_reqid
from .subscription import SubscriptionStatusSubscriptionResponse

logger = logging.getLogger(__name__)


@_attrs_define
class HeartbeatResponse:
    """Server heartbeat sent if no subscription traffic within 1 second (approximately).
    """

    event: LiteralString = EventType.HEARTBEAT.value


@_attrs_define
class PingRequest:
    """Client request to determine whether connection is alive.

    Server responds with `Pong`.

    This is an application level ping as opposed to default ping in
    websockets standard which is server initiated.

    Attributes:
        reqid (Union[Unset,int]): Optional - client originated ID reflected in response message.
    """

    reqid: Unset | int = _attrs_field(default=UNSET, converter=_check_reqid)
    _event: LiteralString = EventType.PING.value

    def to_dict(self) -> dict[str, Any]:
        reqid: Unset | int = UNSET
        if not isinstance(self.reqid, Unset):
            reqid = self.reqid

        field_dict: dict[str, Any] = {}
        field_dict["event"] = self._event
        if reqid is not UNSET:
            field_dict["reqid"] = reqid

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        reqid = d.pop("reqid", UNSET)

        return cls(
            reqid=reqid,
        )


@_attrs_define
class PongResponse:
    """Server pong response to a ping to determine whether connection is alive.

    This is an application level pong as opposed to default pong in
    websockets standard which is sent by client in response to a ping.
    """

    _event: LiteralString = EventType.PONG.value
    reqid: Unset | int = _attrs_field(default=UNSET, converter=_check_reqid)

    def to_dict(self) -> dict[str, Any]:
        reqid: Unset | int = UNSET
        if not isinstance(self.reqid, Unset):
            reqid = self.reqid

        field_dict: dict[str, Any] = {}
        field_dict["event"] = self._event
        if reqid is not UNSET:
            field_dict["reqid"] = reqid

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        event = d.pop("event")

        reqid = d.pop("reqid", UNSET)

        return cls(
            event=event,
            reqid=reqid,
        )


@_attrs_define
class SystemStatusResponse:
    """Status sent on connection or system status changes."""

    status: SystemStatus
    version: str
    connectionID: Unset | int = UNSET
    _event: LiteralString = EventType.SYSTEM_STATUS.value

    def to_dict(self) -> dict[str, Any]:
        connectionID: Unset | int = UNSET
        if not isinstance(self.connectionID, Unset):
            connectionID = self.connectionID

        field_dict: dict[str, Any] = {}
        field_dict["event"] = str(self._event)
        field_dict["status"] = str(self.status)
        field_dict["version"] = self.version
        if not isinstance(connectionID, Unset):
            field_dict["connectionID"] = connectionID

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        event = d.pop("event")
        status = d.pop("status")
        version = d.pop("version")
        connectionID = d.pop("connectionID", UNSET)

        return cls(
            event=event,
            status=status,
            version=version,
            connectionID=connectionID,
        )


@_attrs_define
class SubscriptionStatusResponse:
    """Response to subscribe, unsubscribe or exchange initiated unsubscribe.

    Attributes:
        channel_name: Channel Name on successful subscription.
            For payloads 'ohlc' and 'book', respective interval or depth will
            be added as suffix.
        event (EventType): The EventType associated with SubscriptionStatus
        status (SubscriptionStatus): A `SubscriptionStatus` object
        subscription (SubscriptionStatusSubscriptionResponse):
        reqid (Union[Unset,int]): Optional - client originated ID reflected in response message.
        pair (Union[Unset, str]): Optional - Currency pair, applicable to public messages only
        error_message (Union[Unset, str]): Error message, if any
        channel_id (Union[Unset, int]): Channel ID on successful subscription,
            applicable to public messages only - deprecated, use channelName and pair

    Examples from Kraken Websocket docs:

        ```json
        {
            "channelID": 10001,
            "channelName": "ticker",
            "event": "subscriptionStatus",
            "pair": "XBT/EUR",
            "status": "subscribed",
            "subscription": {
                "name": "ticker"
            }
        }
        ```

        ```json
        {
            "channelID": 10001,
            "channelName": "ohlc-5",
            "event": "subscriptionStatus",
            "pair": "XBT/EUR",
            "reqid": 42,
            "status": "unsubscribed",
            "subscription": {
                "interval": 5,
                "name": "ohlc"
            }
        }
        ```

        ```json
        {
            "channelName": "ownTrades",
            "event": "subscriptionStatus",
            "status": "subscribed",
            "subscription": {
                "name": "ownTrades"
            }
        }
        ```

        ```json
        {
            "errorMessage": "Subscription depth not supported",
            "event": "subscriptionStatus",
            "pair": "XBT/USD",
            "status": "error",
            "subscription": {
                "depth": 42,
                "name": "book"
            }
        }
        ```
    """

    channel_name: str = _attrs_field(alias="channelName")
    status: SubscriptionStatus
    subscription: SubscriptionStatusSubscriptionResponse
    reqid: Unset | int = _attrs_field(default=UNSET, converter=_check_reqid)
    pair: Unset | str = UNSET
    error_message: Unset | str = _attrs_field(alias="errorMessage", default=UNSET)
    channel_id: Unset | int = _attrs_field(alias="channelID", default=UNSET)
    _event: LiteralString = EventType.SYSTEM_STATUS.value

    def to_dict(self) -> dict[str, Any]:
        reqid: Unset | int = UNSET
        if not isinstance(self.reqid, Unset):
            reqid = self.reqid
        pair: Unset | str = UNSET
        if not isinstance(self.pair, Unset):
            pair = self.pair
        error_message: Unset | str = UNSET
        if not isinstance(self.error_message, Unset):
            error_message = self.error_message
        channel_id: Unset | int = UNSET
        if not isinstance(self.channel_id, Unset):
            channel_id = self.channel_id

        field_dict: dict[str, Any] = {}
        field_dict["channel_name"] = self.channel_name
        field_dict["event"] = str(self._event)
        field_dict["status"] = str(self.status)
        field_dict["subscription"] = self.subscription.to_dict()
        if reqid is not UNSET:
            field_dict["reqid"] = reqid
        if pair is not UNSET:
            field_dict["pair"] = pair
        if error_message is not UNSET:
            field_dict["error_message"] = error_message
        if channel_id is not UNSET:
            field_dict["channel_id"] = channel_id

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        event = d.pop("event")
        status = d.pop("status")
        channel_name = d.pop("channelName")
        _subscription = d.pop("subscription")
        reqid = d.pop("reqid", UNSET)
        pair = d.pop("pair", UNSET)
        error_message = d.pop("error_message", UNSET)
        channel_id = d.pop("channel_id", UNSET)

        subscription = SubscriptionStatusSubscriptionResponse.from_dict(_subscription)

        return cls(
            event=event,
            status=status,
            channelName=channel_name,
            subscription=subscription,
            reqid=reqid,
            pair=pair,
            errorMessage=error_message,
            channelID=channel_id,
        )
