""" A client library for accessing Kraken's REST API and Websockets API."""
from .exceptions import InvalidResponseModel, KrakenAPIError, UnexpectedStatus
from .http import HTTPAuthenticatedClient, HTTPClient
from .types import File, FileJsonType, Response

__all__ = (
    "File",
    "FileJsonType",
    "HTTPAuthenticatedClient",
    "HTTPClient",
    "InvalidResponseModel",
    "KrakenAPIError",
    "Response",
    "UnexpectedStatus",
)
