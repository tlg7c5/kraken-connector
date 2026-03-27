"""Subscription tracking types for Kraken WebSocket API v2."""
from typing import Any, Union

from attrs import define as _attrs_define

from .subscribe import (
    BalancesParams,
    BookParams,
    ExecutionsParams,
    InstrumentParams,
    OHLCParams,
    TickerParams,
    TradeParams,
)

SubscriptionParams = Union[
    TickerParams,
    BookParams,
    TradeParams,
    OHLCParams,
    InstrumentParams,
    ExecutionsParams,
    BalancesParams,
]


class SubscriptionError(Exception):
    """Raised when a subscribe/unsubscribe request is rejected by the server."""

    def __init__(self, error: str, req_id: int | None = None) -> None:
        self.error = error
        self.req_id = req_id
        super().__init__(f"Subscription failed: {error}")


@_attrs_define
class SubscriptionEntry:
    """Tracks a single active subscription.

    Attributes:
        params: The original typed parameter object.
        req_id: The req_id used for the subscribe request.
        confirmed: Whether the server has confirmed this subscription.
    """

    params: SubscriptionParams
    req_id: int
    confirmed: bool = False


def _make_sub_key(params: SubscriptionParams) -> tuple[tuple[str, Any], ...]:
    """Create a hashable key from subscription params.

    Uses the serialized dict to ensure two param objects with the same
    field values produce the same key, regardless of object identity.
    The ``token`` field is excluded because it changes on refresh and
    must not affect subscription identity.
    """
    d = params.to_dict()
    d.pop("token", None)
    return tuple(
        sorted((k, tuple(v) if isinstance(v, list) else v) for k, v in d.items())
    )
