"""Token lifecycle management for Kraken WebSocket API v2."""
import asyncio
import time

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..api.websockets_authentication import get_websockets_token
from ..http import HTTPAuthenticatedClient
from ..types import Unset


class TokenAcquisitionError(Exception):
    """Raised when a WebSocket auth token cannot be obtained."""


@_attrs_define
class TokenManager:
    """Manages WebSocket authentication token lifecycle.

    Acquires tokens via the REST API, caches them, and refreshes
    before expiry.

    Attributes:
        auth_client: Authenticated HTTP client for token requests.
        refresh_margin: Seconds before expiry to trigger refresh (default 60).
    """

    _auth_client: HTTPAuthenticatedClient
    _token: str | None = _attrs_field(default=None, init=False, repr=False)
    _expires_at: float = _attrs_field(default=0.0, init=False)
    _refresh_margin: float = _attrs_field(default=60.0, kw_only=True)
    _lock: asyncio.Lock = _attrs_field(factory=asyncio.Lock, init=False)

    async def get_token(self) -> str:
        """Return a valid token, refreshing if expired or near-expiry.

        Raises:
            TokenAcquisitionError: If the REST call fails or returns no token.
        """
        async with self._lock:
            if self.is_valid:
                assert self._token is not None  # guarded by is_valid  # noqa: S101
                return self._token
            token, expires = await self._fetch_token()
            self._token = token
            self._expires_at = time.monotonic() + expires
            return token

    async def _fetch_token(self) -> tuple[str, int]:
        """Call the REST endpoint and return (token, expires_seconds).

        Raises:
            TokenAcquisitionError: On API error or missing token/expires.
        """
        try:
            response = await get_websockets_token.asyncio(
                client=self._auth_client,
            )
        except Exception as exc:
            raise TokenAcquisitionError(f"REST call failed: {exc}") from exc

        if response is None:
            raise TokenAcquisitionError("REST call returned None")

        result = response.result
        if isinstance(result, Unset) or result is None:
            raise TokenAcquisitionError("Response has no result")

        if isinstance(result.token, Unset) or not result.token:
            raise TokenAcquisitionError("Response has no token")

        if isinstance(result.expires, Unset):
            raise TokenAcquisitionError("Response has no expiry")

        return result.token, result.expires

    def invalidate(self) -> None:
        """Force next get_token() call to re-fetch from the REST API."""
        self._token = None
        self._expires_at = 0.0

    @property
    def is_valid(self) -> bool:
        """Whether the cached token is still valid (not expired or near-expiry)."""
        return (
            self._token is not None
            and time.monotonic() < self._expires_at - self._refresh_margin
        )
