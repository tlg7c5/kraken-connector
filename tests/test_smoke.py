"""Smoke tests to verify the package imports and basic instantiation work."""

import importlib
import inspect
import pkgutil

import kraken_connector.api as api_pkg
from kraken_connector import HTTPAuthenticatedClient, HTTPClient


def test_import_http_client():
    client = HTTPClient("https://api.kraken.com")
    assert client._base_url == "https://api.kraken.com"


def test_import_authenticated_client():
    client = HTTPAuthenticatedClient(
        "https://api.kraken.com",
        api_key="test-key",
        api_secret="test-secret",  # noqa: S106
    )
    assert client._api_key == "test-key"
    assert client._api_secret == "test-secret"  # noqa: S105


def test_authenticated_client_inherits_from_http_client():
    client = HTTPAuthenticatedClient(
        "https://api.kraken.com",
        api_key="test-key",
        api_secret="test-secret",  # noqa: S106
    )
    assert isinstance(client, HTTPClient)


def _discover_endpoint_modules():
    """Discover all endpoint modules under kraken_connector.api.*."""
    modules = []
    for domain_info in pkgutil.iter_modules(api_pkg.__path__, api_pkg.__name__ + "."):
        domain = importlib.import_module(domain_info.name)
        if not hasattr(domain, "__path__"):
            continue
        for endpoint_info in pkgutil.iter_modules(
            domain.__path__, domain.__name__ + "."
        ):
            modules.append(importlib.import_module(endpoint_info.name))
    return modules


def test_all_endpoint_modules_have_get_kwargs():
    """Every endpoint module must export a callable _get_kwargs."""
    modules = _discover_endpoint_modules()
    assert len(modules) >= 48, f"Expected >=48 endpoint modules, found {len(modules)}"
    for mod in modules:
        assert hasattr(mod, "_get_kwargs"), f"{mod.__name__} missing _get_kwargs"
        assert callable(mod._get_kwargs), f"{mod.__name__}._get_kwargs not callable"


def test_no_arg_get_kwargs_return_method_and_url():
    """_get_kwargs() with no required params must return a dict with 'method' and 'url'.
    """
    modules = _discover_endpoint_modules()
    tested = 0
    for mod in modules:
        sig = inspect.signature(mod._get_kwargs)
        # Skip functions that have required parameters
        required = [
            p
            for p in sig.parameters.values()
            if p.default is inspect.Parameter.empty
            and p.kind
            not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        ]
        if required:
            continue
        result = mod._get_kwargs()
        assert isinstance(
            result, dict
        ), f"{mod.__name__}._get_kwargs() did not return dict"
        assert "method" in result, f"{mod.__name__}._get_kwargs() missing 'method'"
        assert "url" in result, f"{mod.__name__}._get_kwargs() missing 'url'"
        tested += 1
    assert tested >= 15, f"Expected >=15 no-arg endpoints, only tested {tested}"
