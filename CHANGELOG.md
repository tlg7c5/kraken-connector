# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.1] - 2025-05-01

### Fixed

- `KrakenWSClient.__anext__` now blocks during reconnection instead of raising `TimeoutError`, keeping consumer loops intact across reconnects

## [0.1.0] - 2025-04-01

### Added

- `HTTPClient` and `HTTPAuthenticatedClient` with sync/async support via httpx
- HMAC-SHA512 request signing for authenticated endpoints
- REST endpoint modules for 7 API domains (market data, account data, trading, funding, earn, subaccounts, websocket auth)
- ~100+ attrs-based schema models generated from Kraken's OpenAPI spec
- `ResilienceConfig` with configurable retry transport and exponential backoff
- `RateLimiter` with tier-based token bucket matching Kraken's rate limits (Starter, Intermediate, Pro)
- Request/response logging via httpx event hooks
- `KrakenWSClient` for WebSocket API v2 with automatic reconnection and exponential backoff
- Typed subscription parameters for all public channels (ticker, book, trade, OHLC, instrument)
- Typed subscription parameters for private channels (executions, balances) with automatic token injection
- `TokenManager` for WebSocket token lifecycle (acquisition, caching, refresh)
- All 8 WS v2 trading methods (add_order, edit_order, amend_order, cancel_order, cancel_all, cancel_all_orders_after, batch_add, batch_cancel)
- `OrderBookManager` with local order book state, incremental updates, and CRC32 checksum validation
- `SequenceTracker` for private channel gap detection
- Async iterator API (`async for msg in client`)
- `py.typed` marker for PEP 561 compliance
- Strict mypy configuration

[0.1.1]: https://github.com/tlg7c5/kraken-connector/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/tlg7c5/kraken-connector/releases/tag/v0.1.0
