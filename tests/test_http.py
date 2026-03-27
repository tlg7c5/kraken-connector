"""Tests for HTTP client behavior — auth header injection and copy isolation."""


from kraken_connector import HTTPAuthenticatedClient, HTTPClient


def test_authenticated_client_sets_api_key_header():
    """Verify get_or_create_httpx_client injects the API-Key header."""
    client = HTTPAuthenticatedClient(
        "https://api.kraken.com",
        api_key="test-key",
        api_secret="test-secret",  # noqa: S106
    )
    httpx_client = client.get_or_create_httpx_client()
    assert httpx_client.headers["API-Key"] == "test-key"


def test_authenticated_client_sets_api_key_header_async():
    """Verify get_or_create_async_httpx_client injects the API-Key header."""
    client = HTTPAuthenticatedClient(
        "https://api.kraken.com",
        api_key="test-key",
        api_secret="test-secret",  # noqa: S106
    )
    async_client = client.get_or_create_async_httpx_client()
    assert async_client.headers["API-Key"] == "test-key"


def test_with_headers_returns_independent_copy():
    """with_headers must not mutate the original client."""
    original = HTTPClient("https://api.kraken.com", headers={"X-Original": "yes"})
    _ = original.get_or_create_httpx_client()  # force client creation
    copy = original.with_headers({"X-New": "added"})
    assert "X-New" not in original._headers
    assert copy._headers["X-New"] == "added"
    # Copy should not carry forward the original's httpx client instance
    assert copy._client is None


def test_with_cookies_returns_independent_copy():
    """with_cookies must not mutate the original client."""
    original = HTTPClient("https://api.kraken.com", cookies={"session": "abc"})
    _ = original.get_or_create_httpx_client()
    copy = original.with_cookies({"new_cookie": "xyz"})
    assert "new_cookie" not in original._cookies
    assert copy._cookies["new_cookie"] == "xyz"
    assert copy._client is None


def test_with_timeout_returns_independent_copy():
    """with_timeout must not mutate the original client."""
    import httpx

    original = HTTPClient("https://api.kraken.com")
    _ = original.get_or_create_httpx_client()
    new_timeout = httpx.Timeout(30.0)
    copy = original.with_timeout(new_timeout)
    assert copy._timeout == new_timeout
    assert original._timeout is None
    assert copy._client is None


def test_authenticated_client_repr_hides_credentials():
    """SEC-06 regression: repr must not leak API key or secret."""
    key = "super-secret-api-key"
    secret = "super-secret-api-secret"  # noqa: S105
    client = HTTPAuthenticatedClient(
        "https://api.kraken.com", api_key=key, api_secret=secret
    )
    representation = repr(client)
    assert key not in representation
    assert secret not in representation
