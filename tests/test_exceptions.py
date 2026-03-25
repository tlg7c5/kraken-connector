"""Tests for exception classes and KrakenAPIError endpoint wiring."""

import pytest

from kraken_connector.exceptions import KrakenAPIError, UnexpectedStatus


def test_kraken_api_error_stores_errors():
    err = KrakenAPIError(["EGeneral:Invalid arguments"])
    assert err.errors == ["EGeneral:Invalid arguments"]


def test_kraken_api_error_message_format():
    err = KrakenAPIError(["EGeneral:Invalid arguments", "EOrder:Insufficient funds"])
    assert "EGeneral:Invalid arguments" in str(err)
    assert "EOrder:Insufficient funds" in str(err)


def test_kraken_api_error_is_exception():
    with pytest.raises(KrakenAPIError):
        raise KrakenAPIError(["EGeneral:Test"])


def test_unexpected_status_stores_fields():
    err = UnexpectedStatus(status_code=404, content=b"not found")
    assert err.status_code == 404
    assert err.content == b"not found"


def test_kraken_api_error_raised_on_error_response():
    """Verify _parse_response raises KrakenAPIError when API returns errors."""
    from unittest.mock import MagicMock

    from kraken_connector.api.market_data import get_server_time

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "error": ["EGeneral:Invalid arguments"],
        "result": {},
    }
    mock_client = MagicMock()
    mock_client.raise_on_unexpected_status = False

    with pytest.raises(KrakenAPIError) as exc_info:
        get_server_time._parse_response(client=mock_client, response=mock_response)
    assert exc_info.value.errors == ["EGeneral:Invalid arguments"]
