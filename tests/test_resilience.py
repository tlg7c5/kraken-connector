"""Tests for retry transport, rate limiter, and request logging."""
import asyncio
import logging
import threading
import time
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from kraken_connector import (
    HTTPAuthenticatedClient,
    HTTPClient,
    KrakenTier,
    RateLimiter,
    ResilienceConfig,
)
from kraken_connector.resilience import (
    AsyncRetryTransport,
    RetryTransport,
    make_event_hooks,
)

# ---------------------------------------------------------------------------
# ResilienceConfig defaults
# ---------------------------------------------------------------------------


class TestResilienceConfigDefaults:
    def test_retry_disabled_by_default(self) -> None:
        config = ResilienceConfig()
        assert config.max_retries == 0

    def test_logging_disabled_by_default(self) -> None:
        config = ResilienceConfig()
        assert config.enable_logging is False

    def test_backoff_defaults(self) -> None:
        config = ResilienceConfig()
        assert config.backoff_base == 0.5
        assert config.backoff_max == 30.0

    def test_retryable_exceptions_include_network_errors(self) -> None:
        config = ResilienceConfig()
        assert httpx.ConnectError in config.retryable_exceptions
        assert httpx.ReadTimeout in config.retryable_exceptions


# ---------------------------------------------------------------------------
# RetryTransport (sync)
# ---------------------------------------------------------------------------


class TestRetryTransport:
    def test_succeeds_first_try(self) -> None:
        response = httpx.Response(200)
        wrapped = MagicMock(spec=httpx.BaseTransport)
        wrapped.handle_request.return_value = response
        config = ResilienceConfig(max_retries=3)
        transport = RetryTransport(wrapped, config)

        result = transport.handle_request(httpx.Request("GET", "https://example.com"))

        assert result.status_code == 200
        assert wrapped.handle_request.call_count == 1

    @patch("kraken_connector.resilience.time.sleep")
    def test_retries_on_connect_error(self, mock_sleep: MagicMock) -> None:
        response = httpx.Response(200)
        wrapped = MagicMock(spec=httpx.BaseTransport)
        wrapped.handle_request.side_effect = [
            httpx.ConnectError("connection refused"),
            response,
        ]
        config = ResilienceConfig(max_retries=3, backoff_base=1.0)
        transport = RetryTransport(wrapped, config)

        result = transport.handle_request(httpx.Request("GET", "https://example.com"))

        assert result.status_code == 200
        assert wrapped.handle_request.call_count == 2
        mock_sleep.assert_called_once_with(1.0)

    @patch("kraken_connector.resilience.time.sleep")
    def test_exhausts_retries(self, mock_sleep: MagicMock) -> None:
        wrapped = MagicMock(spec=httpx.BaseTransport)
        wrapped.handle_request.side_effect = httpx.ConnectError("refused")
        config = ResilienceConfig(max_retries=2, backoff_base=0.5)
        transport = RetryTransport(wrapped, config)

        with pytest.raises(httpx.ConnectError):
            transport.handle_request(httpx.Request("GET", "https://example.com"))

        assert wrapped.handle_request.call_count == 3
        assert mock_sleep.call_count == 2

    def test_does_not_retry_non_retryable(self) -> None:
        wrapped = MagicMock(spec=httpx.BaseTransport)
        wrapped.handle_request.side_effect = ValueError("bad value")
        config = ResilienceConfig(max_retries=3)
        transport = RetryTransport(wrapped, config)

        with pytest.raises(ValueError, match="bad value"):
            transport.handle_request(httpx.Request("GET", "https://example.com"))

        assert wrapped.handle_request.call_count == 1

    @patch("kraken_connector.resilience.time.sleep")
    def test_backoff_timing(self, mock_sleep: MagicMock) -> None:
        wrapped = MagicMock(spec=httpx.BaseTransport)
        wrapped.handle_request.side_effect = [
            httpx.ConnectError("err"),
            httpx.ConnectError("err"),
            httpx.ConnectError("err"),
            httpx.Response(200),
        ]
        config = ResilienceConfig(max_retries=3, backoff_base=1.0, backoff_max=10.0)
        transport = RetryTransport(wrapped, config)

        transport.handle_request(httpx.Request("GET", "https://example.com"))

        delays = [call.args[0] for call in mock_sleep.call_args_list]
        assert delays == [1.0, 2.0, 4.0]

    @patch("kraken_connector.resilience.time.sleep")
    def test_backoff_caps_at_max(self, mock_sleep: MagicMock) -> None:
        wrapped = MagicMock(spec=httpx.BaseTransport)
        wrapped.handle_request.side_effect = [
            httpx.ConnectError("err"),
            httpx.ConnectError("err"),
            httpx.ConnectError("err"),
            httpx.Response(200),
        ]
        config = ResilienceConfig(max_retries=3, backoff_base=1.0, backoff_max=3.0)
        transport = RetryTransport(wrapped, config)

        transport.handle_request(httpx.Request("GET", "https://example.com"))

        delays = [call.args[0] for call in mock_sleep.call_args_list]
        assert delays == [1.0, 2.0, 3.0]

    def test_close_delegates(self) -> None:
        wrapped = MagicMock(spec=httpx.BaseTransport)
        transport = RetryTransport(wrapped, ResilienceConfig())
        transport.close()
        wrapped.close.assert_called_once()


# ---------------------------------------------------------------------------
# AsyncRetryTransport
# ---------------------------------------------------------------------------


class TestAsyncRetryTransport:
    def test_retries_on_connect_error(self) -> None:
        async def _run() -> None:
            response = httpx.Response(200)
            wrapped = AsyncMock(spec=httpx.AsyncBaseTransport)
            wrapped.handle_async_request.side_effect = [
                httpx.ConnectError("refused"),
                response,
            ]
            config = ResilienceConfig(max_retries=2, backoff_base=0.01)
            transport = AsyncRetryTransport(wrapped, config)

            result = await transport.handle_async_request(
                httpx.Request("GET", "https://example.com")
            )

            assert result.status_code == 200
            assert wrapped.handle_async_request.call_count == 2

        asyncio.run(_run())

    def test_exhausts_retries(self) -> None:
        async def _run() -> None:
            wrapped = AsyncMock(spec=httpx.AsyncBaseTransport)
            wrapped.handle_async_request.side_effect = httpx.ConnectError("refused")
            config = ResilienceConfig(max_retries=1, backoff_base=0.01)
            transport = AsyncRetryTransport(wrapped, config)

            with pytest.raises(httpx.ConnectError):
                await transport.handle_async_request(
                    httpx.Request("GET", "https://example.com")
                )

            assert wrapped.handle_async_request.call_count == 2

        asyncio.run(_run())

    def test_aclose_delegates(self) -> None:
        async def _run() -> None:
            wrapped = AsyncMock(spec=httpx.AsyncBaseTransport)
            transport = AsyncRetryTransport(wrapped, ResilienceConfig())
            await transport.aclose()
            wrapped.aclose.assert_awaited_once()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# RateLimiter — tier factory
# ---------------------------------------------------------------------------


class TestRateLimiterTiers:
    def test_from_tier_starter(self) -> None:
        limiter = RateLimiter.from_tier(KrakenTier.STARTER)
        assert limiter.max_tokens == 15.0
        assert limiter.decay_rate == 0.33

    def test_from_tier_intermediate(self) -> None:
        limiter = RateLimiter.from_tier(KrakenTier.INTERMEDIATE)
        assert limiter.max_tokens == 20.0
        assert limiter.decay_rate == 0.5

    def test_from_tier_pro(self) -> None:
        limiter = RateLimiter.from_tier(KrakenTier.PRO)
        assert limiter.max_tokens == 20.0
        assert limiter.decay_rate == 1.0


# ---------------------------------------------------------------------------
# RateLimiter — acquire behavior
# ---------------------------------------------------------------------------


class TestRateLimiterAcquire:
    def test_acquire_does_not_block_when_tokens_available(self) -> None:
        limiter = RateLimiter(max_tokens=10.0, decay_rate=1.0)
        start = time.monotonic()
        with limiter.acquire(cost=1.0):
            pass
        elapsed = time.monotonic() - start
        assert elapsed < 0.1

    @patch("kraken_connector.resilience.time.sleep")
    def test_acquire_blocks_when_depleted(self, mock_sleep: MagicMock) -> None:
        limiter = RateLimiter(max_tokens=1.0, decay_rate=1.0)
        # Drain all tokens
        with limiter.acquire(cost=1.0):
            pass
        # Next acquire should need to wait
        # Mock sleep so we don't actually wait, but manually advance _last_refill

        def sleep_and_advance(duration: float) -> None:
            # Simulate time passing by adjusting _last_refill backward
            limiter._last_refill -= duration

        mock_sleep.side_effect = sleep_and_advance

        with limiter.acquire(cost=1.0):
            pass

        mock_sleep.assert_called_once()
        wait_time = mock_sleep.call_args[0][0]
        assert wait_time > 0

    def test_acquire_with_custom_cost(self) -> None:
        limiter = RateLimiter(max_tokens=10.0, decay_rate=1.0)
        with limiter.acquire(cost=3.0):
            pass
        # Should have 7 tokens left
        assert limiter._tokens == pytest.approx(7.0, abs=0.1)

    def test_tokens_cap_at_max(self) -> None:
        limiter = RateLimiter(max_tokens=10.0, decay_rate=100.0)
        # Simulate time passing by setting _last_refill far in the past
        limiter._last_refill = time.monotonic() - 1000
        with limiter.acquire(cost=1.0):
            pass
        # After refill + consume 1, tokens should be max - 1
        assert limiter._tokens == pytest.approx(9.0, abs=0.1)


class TestRateLimiterAsync:
    def test_async_acquire_does_not_block_when_available(self) -> None:
        async def _run() -> None:
            limiter = RateLimiter(max_tokens=10.0, decay_rate=1.0)
            async with limiter.async_acquire(cost=1.0):
                pass
            assert limiter._tokens == pytest.approx(9.0, abs=0.1)

        asyncio.run(_run())

    def test_async_acquire_with_custom_cost(self) -> None:
        async def _run() -> None:
            limiter = RateLimiter(max_tokens=10.0, decay_rate=1.0)
            async with limiter.async_acquire(cost=2.0):
                pass
            assert limiter._tokens == pytest.approx(8.0, abs=0.1)

        asyncio.run(_run())


class TestRateLimiterThreadSafety:
    def test_concurrent_acquire_no_negative_tokens(self) -> None:
        limiter = RateLimiter(max_tokens=5.0, decay_rate=100.0)
        errors: list = []  # type: ignore[type-arg]

        def worker() -> None:
            try:
                for _ in range(10):
                    with limiter.acquire(cost=1.0):
                        pass
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert not errors
        # Tokens should never go below 0 (lock prevents it)
        assert limiter._tokens >= -0.01


# ---------------------------------------------------------------------------
# Logging event hooks
# ---------------------------------------------------------------------------


class TestLoggingHooks:
    def test_event_hooks_created(self) -> None:
        config = ResilienceConfig(enable_logging=True)
        hooks = make_event_hooks(config)
        assert "request" in hooks
        assert "response" in hooks
        assert len(hooks["request"]) == 1
        assert len(hooks["response"]) == 1

    def test_request_hook_logs_method_and_url(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        config = ResilienceConfig(enable_logging=True, log_level=logging.INFO)
        hooks = make_event_hooks(config)
        request = httpx.Request("GET", "https://api.kraken.com/0/public/Time")

        with caplog.at_level(logging.INFO, logger="kraken_connector"):
            hooks["request"][0](request)

        assert "GET" in caplog.text
        assert "/0/public/Time" in caplog.text

    def test_response_hook_logs_status(self, caplog: pytest.LogCaptureFixture) -> None:
        import datetime

        config = ResilienceConfig(enable_logging=True, log_level=logging.INFO)
        hooks = make_event_hooks(config)
        request = httpx.Request("GET", "https://api.kraken.com/0/public/Time")
        response = httpx.Response(200, request=request)
        response.elapsed = datetime.timedelta(seconds=0.12)

        with caplog.at_level(logging.INFO, logger="kraken_connector"):
            hooks["response"][0](response)

        assert "200" in caplog.text

    def test_custom_log_level(self, caplog: pytest.LogCaptureFixture) -> None:
        config = ResilienceConfig(enable_logging=True, log_level=logging.WARNING)
        hooks = make_event_hooks(config)
        request = httpx.Request("GET", "https://api.kraken.com/0/public/Time")

        with caplog.at_level(logging.WARNING, logger="kraken_connector"):
            hooks["request"][0](request)

        assert len(caplog.records) == 1
        assert caplog.records[0].levelno == logging.WARNING


# ---------------------------------------------------------------------------
# Integration with HTTPClient / HTTPAuthenticatedClient
# ---------------------------------------------------------------------------


class TestClientIntegration:
    def test_client_with_resilience_config(self) -> None:
        config = ResilienceConfig(max_retries=3, enable_logging=True)
        client = HTTPClient("https://api.kraken.com", resilience=config)
        assert client._resilience is config

    def test_with_resilience_returns_new_client(self) -> None:
        original = HTTPClient("https://api.kraken.com")
        config = ResilienceConfig(max_retries=2)
        copy = original.with_resilience(config)
        assert original._resilience is None
        assert copy._resilience is config

    def test_retry_transport_used_when_configured(self) -> None:
        config = ResilienceConfig(max_retries=2)
        client = HTTPClient("https://api.kraken.com", resilience=config)
        httpx_client = client.get_or_create_httpx_client()
        assert isinstance(httpx_client._transport, RetryTransport)

    def test_no_retry_transport_when_disabled(self) -> None:
        config = ResilienceConfig(max_retries=0)
        client = HTTPClient("https://api.kraken.com", resilience=config)
        httpx_client = client.get_or_create_httpx_client()
        assert not isinstance(httpx_client._transport, RetryTransport)

    def test_authenticated_client_with_resilience(self) -> None:
        config = ResilienceConfig(max_retries=2)
        client = HTTPAuthenticatedClient(
            "https://api.kraken.com",
            api_key="test-key",
            api_secret="test-secret",  # noqa: S106
            resilience=config,
        )
        httpx_client = client.get_or_create_httpx_client()
        assert isinstance(httpx_client._transport, RetryTransport)
        assert httpx_client.headers["API-Key"] == "test-key"

    def test_logging_hooks_injected_when_enabled(self) -> None:
        config = ResilienceConfig(enable_logging=True)
        client = HTTPClient("https://api.kraken.com", resilience=config)
        httpx_client = client.get_or_create_httpx_client()
        assert len(httpx_client.event_hooks["request"]) >= 1
        assert len(httpx_client.event_hooks["response"]) >= 1

    def test_default_client_has_no_resilience(self) -> None:
        client = HTTPClient("https://api.kraken.com")
        assert client._resilience is None
