"""Smoke tests to verify the package imports and basic instantiation work."""

from kraken_connector import HTTPAuthenticatedClient, HTTPClient


def test_import_http_client():
    client = HTTPClient("https://api.kraken.com")
    assert client._base_url == "https://api.kraken.com"


def test_import_authenticated_client():
    client = HTTPAuthenticatedClient(
        "https://api.kraken.com",
        api_key="test-key",
        api_secret="test-secret",
    )
    assert client._api_key == "test-key"
    assert client._api_secret == "test-secret"


def test_authenticated_client_inherits_from_http_client():
    client = HTTPAuthenticatedClient(
        "https://api.kraken.com",
        api_key="test-key",
        api_secret="test-secret",
    )
    assert isinstance(client, HTTPClient)
