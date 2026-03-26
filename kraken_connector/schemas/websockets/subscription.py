"""Schema related to Kraken Websocket subscriptions.

Note:
    All subscription related messages received through Kraken websockets
    are dictionary objects with the value set on the 'event' key dictating
    the type of message.
"""
from typing import Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ...constants.websockets import BookDepth, EventType, OhlcInterval, SubscriptionType
from ...types import UNSET, Unset
from ...utils.validators import _check_reqid


@_attrs_define
class SubscriptionRequest:
    """Data model for the Subscription object of a SubscribeRequest.

    Attributes:
        name (SubscriptionType): Channel Name to which a subscription is made. One of
            book|ohlc|openOrders|ownTrades|spread|ticker|trade
        depth (Union[Unset, BookDepth]): Optional depth associated with book subscription
            in number of levels each side, default 10.
            Valid Options are: 10, 25, 100, 500, 1000
        interval (Union[Unset, OhlcInterval]): Optional time interval associated with
            ohlc subscription in minutes. Default 1.
            Valid Interval values: 1|5|15|30|60|240|1440|10080|21600
        rate_counter (Union[Unset, bool]): Optional - whether to send rate-limit counter in updates
            (supported only for openOrders subscriptions; default = False)
        snapshot (Union[Unset, bool]): Optional - whether to send historical feed data snapshot
            upon subscription (supported only for ownTrades subscriptions; default = true)
        token (Union[Unset, str]): Optional base64-encoded authentication token for
            private-data endpoints.
        consolidate_taker (Union[Unset, bool]): Optional - for ownTrades, whether to consolidate
            order fills by root taker trade(s), default = true. If false, all order fills
            will show separately.
    """

    name: SubscriptionType
    depth: Unset | BookDepth = UNSET
    interval: Unset | OhlcInterval = UNSET
    rate_counter: Unset | bool = _attrs_field(alias="ratecounter", default=UNSET)
    snapshot: Unset | bool = UNSET
    token: Unset | str = UNSET
    consolidate_taker: (Unset | bool) = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        field_dict["name"] = str(self.name)
        if not isinstance(self.depth, Unset):
            field_dict["depth"] = str(self.depth)
        if not isinstance(self.interval, Unset):
            field_dict["interval"] = str(self.interval)
        if not isinstance(self.rate_counter, Unset):
            field_dict["ratecounter"] = self.rate_counter
        if not isinstance(self.snapshot, Unset):
            field_dict["snapshot"] = self.snapshot
        if not isinstance(self.token, Unset):
            field_dict["token"] = self.token
        if not isinstance(self.consolidate_taker, Unset):
            field_dict["consolidate_taker"] = self.consolidate_taker

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        name = d.pop("name")
        depth = d.pop("depth", UNSET)
        interval = d.pop("interval", UNSET)
        rate_counter = d.pop("rate_counter", UNSET)
        if isinstance(rate_counter, Unset):
            rate_counter = d.pop("ratecounter", UNSET)
        snapshot = d.pop("snapshot", UNSET)
        token = d.pop("token", UNSET)
        consolidate_taker = d.pop("consolidate_taker", UNSET)

        return cls(
            name=name,
            depth=depth,
            interval=interval,
            ratecounter=rate_counter,
            snapshot=snapshot,
            token=token,
            consolidate_taker=consolidate_taker,
        )


@_attrs_define
class SubscriptionStatusSubscriptionResponse:
    """Data model for Subscription object sent in response by the SubscriptionStatus endpoint.

    Attributes:
        name (SubscriptionType): Channel Name to which a subscription is made.
        depth (Union[Unset, BookDepth]): Optional depth associated with book subscription
            in number of levels each side, default 10.
            Valid Options are: 10, 25, 100, 500, 1000
        interval (Union[Unset, OhlcInterval]): Optional time interval associated with
            ohlc subscription in minutes. Default 1.
            Valid Interval values: 1|5|15|30|60|240|1440|10080|21600
        max_rate_count (Union[Unset, int]): Optional max rate-limit budget.
            Compare to the ratecounter field in the openOrders updates to check whether
            you are approaching the rate limit.
        token (Union[Unset, str]): Optional base64-encoded authentication token for
            private-data endpoints.
    """

    name: SubscriptionType
    depth: Unset | BookDepth = UNSET
    interval: Unset | OhlcInterval = UNSET
    max_rate_count: Unset | int = _attrs_field(alias="maxratecount", default=UNSET)
    token: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        field_dict["name"] = str(self.name)

        if not isinstance(self.depth, Unset):
            field_dict["depth"] = str(self.depth)
        if not isinstance(self.interval, Unset):
            field_dict["interval"] = str(self.interval)
        if not isinstance(self.max_rate_count, Unset):
            field_dict["maxratecount"] = self.max_rate_count
        if not isinstance(self.token, Unset):
            field_dict["token"] = self.token

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        name = d.pop("name")
        depth = d.pop("depth", UNSET)
        interval = d.pop("interval", UNSET)
        max_rate_count = d.pop("max_rate_count", UNSET)
        if isinstance(max_rate_count, Unset):
            max_rate_count = d.pop("maxratecount", UNSET)
        token = d.pop("token", UNSET)

        return cls(
            name=name,
            depth=depth,
            interval=interval,
            maxratecount=max_rate_count,
            token=token,
        )


@_attrs_define
class SubcribeRequest:
    """Subscribe to a topic on single or multiple currency pairs.

    Attributes:
        subscription (SubscriptionRequest):
        pair (Union[Unset, List[str]]): Optional array of currency pairs. Format of each pair
            is "A/B", where A and B are ISO 4217-A3 for standardized assets and popular unique
            symbol if not standardized.
        reqid (Union[Unset,int]): Optional client originated ID reflected in response message.

    Examples from the Kraken API Docs:

        ```json
        {
            "event": "subscribe",
            "pair": [
                "XBT/USD",
                "XBT/EUR"
            ],
            "subscription": {
                "name": "ticker"
            }
        }
        ```

        ```json
        {
            "event": "subscribe",
            "pair": [
                "XBT/EUR"
            ],
            "subscription": {
                "interval": 5,
                "name": "ohlc"
            }
        }
        ```

        ```json
        {
            "event": "subscribe",
            "subscription": {
                "name": "ownTrades",
                "token": "WW91ciBhdXRoZW50aWNhdGlvbiB0b2tlbiBnb2VzIGhlcmUu"
            }
        }
        ```
    """

    subscription: SubscriptionRequest
    reqid: Unset | int = _attrs_field(default=UNSET, converter=_check_reqid)
    pair: Unset | list[str] = UNSET
    _event: EventType = EventType.SUBSCRIBE

    def to_dict(self) -> dict[str, Any]:
        reqid: Unset | int = UNSET
        if not isinstance(self.reqid, Unset):
            reqid = self.reqid
        pair: Unset | list[str] = UNSET
        if not isinstance(self.pair, Unset):
            pair = self.pair

        field_dict: dict[str, Any] = {}
        field_dict["event"] = str(self._event)
        if reqid is not UNSET:
            field_dict["reqid"] = reqid
        if pair is not UNSET:
            field_dict["pair"] = pair
        field_dict["subscription"] = self.subscription.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        d.pop("name")
        reqid = d.pop("reqid", UNSET)
        pair = d.pop("pair", UNSET)
        _subscription = d.pop("subscription", UNSET)

        subscription = SubscriptionRequest.from_dict(_subscription)

        return cls(
            reqid=reqid,
            pair=pair,
            subscription=subscription,
        )


@_attrs_define
class UnsubscribeSubscriptionRequest:
    """Data model for the Subscription object of a UnsubscribeRequest.

    Attributes:
        name (SubscriptionType): Channel Name to which a subscription is made. One of
            book|ohlc|openOrders|ownTrades|spread|ticker|trade
        depth (Union[Unset, BookDepth]): Optional depth associated with book subscription
            in number of levels each side, default 10.
            Valid Options are: 10, 25, 100, 500, 1000
        interval (Union[Unset, OhlcInterval]): Optional time interval associated with
            ohlc subscription in minutes. Default 1.
            Valid Interval values: 1|5|15|30|60|240|1440|10080|21600
        token (Union[Unset, str]): Optional base64-encoded authentication token for
            private-data endpoints.
    """

    name: SubscriptionType
    depth: Unset | BookDepth = UNSET
    interval: Unset | OhlcInterval = UNSET
    token: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        field_dict["name"] = str(self.name)
        if not isinstance(self.depth, Unset):
            field_dict["depth"] = str(self.depth)
        if not isinstance(self.interval, Unset):
            field_dict["interval"] = str(self.interval)
        if not isinstance(self.token, Unset):
            field_dict["token"] = self.token

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        name = d.pop("name")
        depth = d.pop("depth", UNSET)
        interval = d.pop("interval", UNSET)
        token = d.pop("token", UNSET)

        return cls(
            name=name,
            depth=depth,
            interval=interval,
            token=token,
        )


@_attrs_define
class UnsubcribeRequest:
    """Unsubscribe from a SubscriptionType to which a SubscriptionRequest was made.

    Valid UnsubscribeRequest can specify a channelID or multiple currency pairs.

    Attributes:
        subscription (UnsubscribeSubscriptionRequest): An `UnsubscribeSubscriptionRequest` object
        pair (Union[Unset, List[str]]): Optional array of currency pairs. Format of each pair
            is "A/B", where A and B are ISO 4217-A3 for standardized assets and popular unique
            symbol if not standardized.
        reqid (Union[Unset,int]): Optional client originated ID reflected in response message.
        channel_id (Union[Unset, int]): Optional Channel ID on successful subscription,
            applicable to public messages only - deprecated, use SubscriptionType and pair instead.

    Examples from the Kraken API Docs:

        ```json
        {
            "event": "unsubscribe",
            "pair": [
                "XBT/EUR",
                "XBT/USD"
            ],
            "subscription": {
                "name": "ticker"
            }
        }
        ```

        ```json
        {
            "channelID": 10001,
            "event": "unsubscribe"
        }
        ```

        ```json
        {
            "event": "unsubscribe",
            "subscription": {
                "name": "ownTrades",
                "token": "WW91ciBhdXRoZW50aWNhdGlvbiB0b2tlbiBnb2VzIGhlcmUu"
            }
        }
        ```
    """

    subscription: UnsubscribeSubscriptionRequest
    reqid: Unset | int = _attrs_field(default=UNSET, converter=_check_reqid)
    channel_id: Unset | int = _attrs_field(
        alias="channelID", default=UNSET, converter=_check_reqid
    )
    pair: Unset | list[str] = UNSET
    _event: EventType = EventType.UNSUBSCRIBE

    def to_dict(self) -> dict[str, Any]:
        reqid: Unset | int = UNSET
        if not isinstance(self.reqid, Unset):
            reqid = self.reqid
        pair: Unset | list[str] = UNSET
        if not isinstance(self.pair, Unset):
            pair = self.pair
        channel_id: Unset | int = UNSET
        if not isinstance(self.channel_id, Unset):
            channel_id = self.channel_id

        field_dict: dict[str, Any] = {}
        field_dict["event"] = str(self._event)
        if reqid is not UNSET:
            field_dict["reqid"] = reqid
        if pair is not UNSET:
            field_dict["pair"] = pair
        if channel_id is not UNSET:
            field_dict["channelID"] = channel_id
        field_dict["subscription"] = self.subscription.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        reqid = d.pop("reqid", UNSET)
        pair = d.pop("pair", UNSET)
        channel_id = d.pop("channel_id", UNSET)
        if isinstance(channel_id, Unset):
            channel_id = d.pop("channelID", UNSET)
        _subscription = d.pop("subscription", UNSET)

        subscription = UnsubscribeSubscriptionRequest.from_dict(_subscription)

        return cls(
            reqid=reqid,
            pair=pair,
            subscription=subscription,
            channelID=channel_id,
        )
