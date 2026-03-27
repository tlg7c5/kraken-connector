""" Contains shared errors types that can be raised from API functions """


class InvalidResponseModel(Exception):
    """Raised by schema models when required key-value pairs are not found."""


class UnexpectedStatus(Exception):
    """Raised by api functions when the response status an undocumented status and HTTPClient.raise_on_unexpected_status is True
    """

    def __init__(self, status_code: int, content: bytes):
        self.status_code = status_code
        self.content = content

        super().__init__(f"Unexpected status code: {status_code}")


class KrakenAPIError(Exception):
    """Raised when the Kraken API returns an error in the response body."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"Kraken API error: {', '.join(errors)}")


__all__ = ["InvalidResponseModel", "KrakenAPIError", "UnexpectedStatus"]
