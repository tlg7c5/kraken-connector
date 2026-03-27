import ssl
from typing import TYPE_CHECKING, Any, Optional, Self

import httpx
from attrs import define, evolve, field

if TYPE_CHECKING:
    from .resilience import ResilienceConfig


@define
class HTTPClient:
    """A class for keeping track of data related to the API

    The following are accepted as keyword arguments and will be used to construct httpx HTTPClients internally:

        ``base_url``: The base URL for the API, all requests are made to a relative path to this URL

        ``cookies``: A dictionary of cookies to be sent with every request

        ``headers``: A dictionary of headers to be sent with every request

        ``timeout``: The maximum amount of a time a request can take. API functions will raise
        httpx.TimeoutException if this is exceeded.

        ``verify_ssl``: Whether or not to verify the SSL certificate of the API server. This should be True in production,
        but can be set to False for testing purposes.

        ``follow_redirects``: Whether or not to follow redirects. Default value is False.

        ``httpx_args``: A dictionary of additional arguments to be passed to the ``httpx.Client`` and ``httpx.AsyncClient`` constructor.


    Attributes:
        raise_on_unexpected_status: Whether or not to raise an errors.UnexpectedStatus if the API returns a
            status code that was not documented in the source OpenAPI document. Can also be provided as a keyword
            argument to the constructor.
    """

    raise_on_unexpected_status: bool = field(default=False, kw_only=True)
    _base_url: str
    _cookies: dict[str, str] = field(factory=dict, kw_only=True)
    _headers: dict[str, str] = field(factory=dict, kw_only=True)
    _timeout: httpx.Timeout | None = field(default=None, kw_only=True)
    _verify_ssl: str | bool | ssl.SSLContext = field(default=True, kw_only=True)
    _follow_redirects: bool = field(default=False, kw_only=True)
    _httpx_args: dict[str, Any] = field(factory=dict, kw_only=True)
    _resilience: Optional["ResilienceConfig"] = field(default=None, kw_only=True)
    _client: httpx.Client | None = field(default=None, init=False)
    _async_client: httpx.AsyncClient | None = field(default=None, init=False)

    def with_headers(self, headers: dict[str, str]) -> Self:
        """Get a new client matching this one with additional headers"""
        return evolve(self, headers={**self._headers, **headers})

    def with_cookies(self, cookies: dict[str, str]) -> Self:
        """Get a new client matching this one with additional cookies"""
        return evolve(self, cookies={**self._cookies, **cookies})

    def with_timeout(self, timeout: httpx.Timeout) -> Self:
        """Get a new client matching this one with a new timeout (in seconds)"""
        return evolve(self, timeout=timeout)

    def with_resilience(self, resilience: "ResilienceConfig") -> Self:
        """Get a new client matching this one with resilience configuration"""
        return evolve(self, resilience=resilience)

    def set_httpx_client(self, client: httpx.Client) -> Self:
        """Manually set the underlying httpx.Client

        **NOTE**: This will override any other settings on the client, including cookies, headers, and timeout.
        """
        self._client = client
        return self

    def _build_httpx_kwargs(self, *, is_async: bool = False) -> dict[str, Any]:
        """Build kwargs for httpx.Client or httpx.AsyncClient construction.

        Injects retry transport and logging event hooks when a
        :class:`~kraken_connector.resilience.ResilienceConfig` is set.
        """
        kwargs: dict[str, Any] = {
            "base_url": self._base_url,
            "cookies": self._cookies,
            "headers": self._headers,
            "timeout": self._timeout,
            "verify": self._verify_ssl,
            "follow_redirects": self._follow_redirects,
            **self._httpx_args,
        }
        if self._resilience is not None:
            from .resilience import (
                AsyncRetryTransport,
                RetryTransport,
                make_event_hooks,
            )

            if self._resilience.max_retries > 0:
                if is_async:
                    async_base = httpx.AsyncHTTPTransport(verify=self._verify_ssl)
                    kwargs["transport"] = AsyncRetryTransport(
                        async_base, self._resilience
                    )
                else:
                    sync_base = httpx.HTTPTransport(verify=self._verify_ssl)
                    kwargs["transport"] = RetryTransport(sync_base, self._resilience)
            if self._resilience.enable_logging:
                hooks = make_event_hooks(self._resilience)
                existing: dict[str, list[Any]] = kwargs.pop("event_hooks", {})
                kwargs["event_hooks"] = {
                    "request": existing.get("request", []) + hooks["request"],
                    "response": existing.get("response", []) + hooks["response"],
                }
        return kwargs

    def get_or_create_httpx_client(self) -> httpx.Client:
        """Get the underlying httpx.Client, constructing a new one if not previously set
        """
        if self._client is None:
            self._client = httpx.Client(**self._build_httpx_kwargs())
        return self._client

    def __enter__(self) -> Self:
        """Enter a context manager for self.client—you cannot enter twice (see httpx docs)
        """
        self.get_or_create_httpx_client().__enter__()
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        """Exit a context manager for internal httpx.Client (see httpx docs)"""
        self.get_or_create_httpx_client().__exit__(*args, **kwargs)

    def set_async_httpx_client(self, async_client: httpx.AsyncClient) -> Self:
        """Manually set the underlying httpx.AsyncClient

        **NOTE**: This will override any other settings on the client, including cookies, headers, and timeout.
        """
        self._async_client = async_client
        return self

    def get_or_create_async_httpx_client(self) -> httpx.AsyncClient:
        """Get the underlying httpx.AsyncClient, constructing a new one if not previously set
        """
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                **self._build_httpx_kwargs(is_async=True)
            )
        return self._async_client

    async def __aenter__(self) -> Self:
        """Enter a context manager for underlying httpx.AsyncClient—you cannot enter twice (see httpx docs)
        """
        await self.get_or_create_async_httpx_client().__aenter__()
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        """Exit a context manager for underlying httpx.AsyncClient (see httpx docs)"""
        await self.get_or_create_async_httpx_client().__aexit__(*args, **kwargs)


@define
class HTTPAuthenticatedClient(HTTPClient):
    """A HTTPClient which has been authenticated for use on secured endpoints.

    Inherits all functionality from HTTPClient and adds API key authentication.
    The ``get_or_create_httpx_client`` and ``get_or_create_async_httpx_client`` methods inject the
    API-Key header before constructing the underlying httpx client.

    Attributes:
        api_key: The API key to use for authentication
        api_secret: The API secret used to sign the authenticated request.
        auth_header_name: The name of the Authorization header
    """

    _api_key: str | None = field(default=None, kw_only=True, repr=False)
    _api_secret: str | None = field(default=None, kw_only=True, repr=False)
    _follow_redirects: bool = field(default=False, kw_only=True)

    auth_header_name: str = "API-Key"
    hmac_msg_signature: str = "API-Sign"

    def get_or_create_httpx_client(self) -> httpx.Client:
        """Get the underlying httpx.Client, constructing a new one if not previously set
        """
        if self._client is None:
            if self._api_key is None:
                raise ValueError("api_key is required for authenticated client")
            self._headers[self.auth_header_name] = self._api_key
            self._client = httpx.Client(**self._build_httpx_kwargs())
        return self._client

    def get_or_create_async_httpx_client(self) -> httpx.AsyncClient:
        """Get the underlying httpx.AsyncClient, constructing a new one if not previously set
        """
        if self._async_client is None:
            if self._api_key is None:
                raise ValueError("api_key is required for authenticated client")
            self._headers[self.auth_header_name] = self._api_key
            self._async_client = httpx.AsyncClient(
                **self._build_httpx_kwargs(is_async=True)
            )
        return self._async_client
