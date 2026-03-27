"""Tests for TokenManager lifecycle."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from kraken_connector.ws.token import TokenAcquisitionError, TokenManager


def _mock_auth_client() -> MagicMock:
    return MagicMock()


def _mock_token_response(
    token: str = "test-token", expires: int = 900  # noqa: S107
) -> MagicMock:
    result = MagicMock()
    result.token = token
    result.expires = expires
    response = MagicMock()
    response.result = result
    return response


class TestTokenManager:
    def test_get_token_fetches_on_first_call(self) -> None:
        async def _run() -> None:
            tm = TokenManager(auth_client=_mock_auth_client())
            with patch(
                "kraken_connector.ws.token.get_websockets_token.asyncio",
                new_callable=AsyncMock,
                return_value=_mock_token_response("abc123", 900),
            ):
                token = await tm.get_token()
                assert token == "abc123"  # noqa: S105

        asyncio.run(_run())

    def test_get_token_returns_cached_within_expiry(self) -> None:
        async def _run() -> None:
            tm = TokenManager(auth_client=_mock_auth_client(), refresh_margin=60.0)
            mock_fetch = AsyncMock(return_value=_mock_token_response("cached", 900))
            with patch(
                "kraken_connector.ws.token.get_websockets_token.asyncio",
                mock_fetch,
            ):
                t1 = await tm.get_token()
                t2 = await tm.get_token()
                assert t1 == t2 == "cached"
                assert mock_fetch.call_count == 1

        asyncio.run(_run())

    def test_get_token_refreshes_when_near_expiry(self) -> None:
        async def _run() -> None:
            tm = TokenManager(auth_client=_mock_auth_client(), refresh_margin=60.0)

            responses = [
                _mock_token_response("old", 900),
                _mock_token_response("new", 900),
            ]
            mock_fetch = AsyncMock(side_effect=responses)

            with (
                patch(
                    "kraken_connector.ws.token.get_websockets_token.asyncio",
                    mock_fetch,
                ),
                patch("kraken_connector.ws.token.time") as mock_time,
            ):
                # First fetch at t=0.
                mock_time.monotonic.return_value = 0.0
                t1 = await tm.get_token()
                assert t1 == "old"

                # Simulate time past expiry margin (900 - 60 = 840).
                mock_time.monotonic.return_value = 841.0
                t2 = await tm.get_token()
                assert t2 == "new"
                assert mock_fetch.call_count == 2

        asyncio.run(_run())

    def test_get_token_raises_on_api_error(self) -> None:
        async def _run() -> None:
            tm = TokenManager(auth_client=_mock_auth_client())
            with patch(
                "kraken_connector.ws.token.get_websockets_token.asyncio",
                new_callable=AsyncMock,
                side_effect=ConnectionError("network down"),
            ), pytest.raises(TokenAcquisitionError, match="REST call failed"):
                await tm.get_token()

        asyncio.run(_run())

    def test_get_token_raises_on_none_response(self) -> None:
        async def _run() -> None:
            tm = TokenManager(auth_client=_mock_auth_client())
            with patch(
                "kraken_connector.ws.token.get_websockets_token.asyncio",
                new_callable=AsyncMock,
                return_value=None,
            ), pytest.raises(TokenAcquisitionError, match="returned None"):
                await tm.get_token()

        asyncio.run(_run())

    def test_get_token_raises_on_unset_token_field(self) -> None:
        async def _run() -> None:
            from kraken_connector.types import UNSET

            tm = TokenManager(auth_client=_mock_auth_client())
            resp = MagicMock()
            result = MagicMock()
            result.token = UNSET
            result.expires = 900
            resp.result = result

            with patch(
                "kraken_connector.ws.token.get_websockets_token.asyncio",
                new_callable=AsyncMock,
                return_value=resp,
            ), pytest.raises(TokenAcquisitionError, match="no token"):
                await tm.get_token()

        asyncio.run(_run())

    def test_invalidate_forces_refetch(self) -> None:
        async def _run() -> None:
            tm = TokenManager(auth_client=_mock_auth_client())
            mock_fetch = AsyncMock(
                side_effect=[
                    _mock_token_response("first", 900),
                    _mock_token_response("second", 900),
                ]
            )
            with patch(
                "kraken_connector.ws.token.get_websockets_token.asyncio",
                mock_fetch,
            ):
                t1 = await tm.get_token()
                assert t1 == "first"

                tm.invalidate()
                assert not tm.is_valid

                t2 = await tm.get_token()
                assert t2 == "second"
                assert mock_fetch.call_count == 2

        asyncio.run(_run())

    def test_is_valid_property(self) -> None:
        tm = TokenManager(auth_client=_mock_auth_client())
        assert not tm.is_valid

    def test_concurrent_calls_only_fetch_once(self) -> None:
        async def _run() -> None:
            tm = TokenManager(auth_client=_mock_auth_client())
            mock_fetch = AsyncMock(return_value=_mock_token_response("shared", 900))
            with patch(
                "kraken_connector.ws.token.get_websockets_token.asyncio",
                mock_fetch,
            ):
                results = await asyncio.gather(
                    tm.get_token(),
                    tm.get_token(),
                    tm.get_token(),
                )
                assert all(t == "shared" for t in results)
                assert mock_fetch.call_count == 1

        asyncio.run(_run())
