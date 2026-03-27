"""Resilience features: retry transport, rate limiting, and request logging."""
import asyncio
import logging
import threading
import time
from contextlib import asynccontextmanager, contextmanager
from enum import Enum
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Generator,
)

import httpx
from attrs import define, field

_logger = logging.getLogger("kraken_connector")

# Default set of httpx exceptions that indicate a transient network error.
_DEFAULT_RETRYABLE_EXCEPTIONS: tuple[type[Exception], ...] = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.PoolTimeout,
)


class KrakenTier(str, Enum):
    """Kraken account tier, determines rate limit parameters.

    See https://docs.kraken.com/api/ for tier-specific limits.
    """

    STARTER = "starter"
    INTERMEDIATE = "intermediate"
    PRO = "pro"

    def __str__(self) -> str:
        return self.value


# Tier parameters: (max_tokens, decay_rate per second)
_TIER_PARAMS: dict[KrakenTier, tuple[float, float]] = {
    KrakenTier.STARTER: (15.0, 0.33),
    KrakenTier.INTERMEDIATE: (20.0, 0.5),
    KrakenTier.PRO: (20.0, 1.0),
}


@define
class ResilienceConfig:
    """Configuration for retry and logging behavior.

    Passed to ``HTTPClient`` or ``HTTPAuthenticatedClient`` at construction
    time via the ``resilience`` keyword argument.

    Retry is disabled by default (``max_retries=0``).  Only transient network
    errors are retried — API-level errors (rate limits, validation) are never
    retried at the transport layer.

    Logging uses Python's stdlib ``logging`` module via httpx event hooks.
    Configure the ``kraken_connector`` logger in your application to control
    output (e.g., with structlog's stdlib integration).
    """

    max_retries: int = 0
    backoff_base: float = 0.5
    backoff_max: float = 30.0
    retryable_exceptions: tuple[type[Exception], ...] = field(
        default=_DEFAULT_RETRYABLE_EXCEPTIONS,
    )
    enable_logging: bool = False
    log_level: int = logging.DEBUG


class RetryTransport(httpx.BaseTransport):
    """Sync httpx transport that retries on transient network errors."""

    def __init__(
        self,
        wrapped: httpx.BaseTransport,
        config: ResilienceConfig,
    ) -> None:
        self._wrapped = wrapped
        self._config = config

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        last_exc: Exception = RuntimeError("no attempts made")
        for attempt in range(self._config.max_retries + 1):
            try:
                return self._wrapped.handle_request(request)
            except self._config.retryable_exceptions as exc:
                last_exc = exc
                if attempt < self._config.max_retries:
                    delay = min(
                        self._config.backoff_base * (2**attempt),
                        self._config.backoff_max,
                    )
                    _logger.warning(
                        "Retry %d/%d after %.2fs: %s",
                        attempt + 1,
                        self._config.max_retries,
                        delay,
                        exc,
                    )
                    time.sleep(delay)
        raise last_exc

    def close(self) -> None:
        self._wrapped.close()


class AsyncRetryTransport(httpx.AsyncBaseTransport):
    """Async httpx transport that retries on transient network errors."""

    def __init__(
        self,
        wrapped: httpx.AsyncBaseTransport,
        config: ResilienceConfig,
    ) -> None:
        self._wrapped = wrapped
        self._config = config

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        last_exc: Exception = RuntimeError("no attempts made")
        for attempt in range(self._config.max_retries + 1):
            try:
                return await self._wrapped.handle_async_request(request)
            except self._config.retryable_exceptions as exc:
                last_exc = exc
                if attempt < self._config.max_retries:
                    delay = min(
                        self._config.backoff_base * (2**attempt),
                        self._config.backoff_max,
                    )
                    _logger.warning(
                        "Retry %d/%d after %.2fs: %s",
                        attempt + 1,
                        self._config.max_retries,
                        delay,
                        exc,
                    )
                    await asyncio.sleep(delay)
        raise last_exc

    async def aclose(self) -> None:
        await self._wrapped.aclose()


@define
class RateLimiter:
    """Caller-controlled token bucket rate limiter matching Kraken's tiers.

    Usage::

        limiter = RateLimiter.from_tier(KrakenTier.STARTER)

        # Sync
        with limiter.acquire(cost=1):
            response = get_server_time.sync(client=client)

        # Async
        async with limiter.async_acquire(cost=2):
            response = await get_trade_history.asyncio(client=client)

    The ``cost`` parameter supports Kraken's variable token costs: most calls
    cost 1, but ledger/trade history calls cost 2.
    """

    max_tokens: float
    decay_rate: float
    _tokens: float = field(init=False)
    _last_refill: float = field(init=False)
    _lock: threading.Lock = field(init=False, factory=threading.Lock, repr=False)
    _async_lock: asyncio.Lock = field(init=False, factory=asyncio.Lock, repr=False)

    def __attrs_post_init__(self) -> None:
        self._tokens = self.max_tokens
        self._last_refill = time.monotonic()

    @classmethod
    def from_tier(cls, tier: KrakenTier) -> "RateLimiter":
        """Create a rate limiter with parameters matching *tier*."""
        max_tokens, decay_rate = _TIER_PARAMS[tier]
        return cls(max_tokens=max_tokens, decay_rate=decay_rate)

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.max_tokens, self._tokens + elapsed * self.decay_rate)
        self._last_refill = now

    @contextmanager
    def acquire(self, cost: float = 1.0) -> Generator[None, None, None]:
        """Block until *cost* tokens are available, then yield."""
        with self._lock:
            self._refill()
            if self._tokens < cost:
                wait = (cost - self._tokens) / self.decay_rate
                time.sleep(wait)
                self._refill()
            self._tokens -= cost
        yield

    @asynccontextmanager
    async def async_acquire(self, cost: float = 1.0) -> AsyncGenerator[None, None]:
        """Async version of :meth:`acquire`."""
        async with self._async_lock:
            self._refill()
            if self._tokens < cost:
                wait = (cost - self._tokens) / self.decay_rate
                await asyncio.sleep(wait)
                self._refill()
            self._tokens -= cost
        yield


def make_event_hooks(config: ResilienceConfig) -> dict[str, list[Callable[..., Any]]]:
    """Build httpx event_hooks for request/response logging."""
    level = config.log_level

    def on_request(request: httpx.Request) -> None:
        _logger.log(level, "HTTP %s %s", request.method, request.url)

    def on_response(response: httpx.Response) -> None:
        elapsed = response.elapsed.total_seconds() if response.elapsed else 0.0
        _logger.log(
            level,
            "HTTP %s %s -> %d (%.2fs)",
            response.request.method,
            response.request.url,
            response.status_code,
            elapsed,
        )

    return {"request": [on_request], "response": [on_response]}
