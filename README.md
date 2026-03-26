# kraken-connector

[![Release](https://img.shields.io/github/v/release/tlg7c5/kraken-connector)](https://img.shields.io/github/v/release/tlg7c5/kraken-connector)
[![Build status](https://img.shields.io/github/actions/workflow/status/tlg7c5/kraken-connector/main.yml?branch=main)](https://github.com/tlg7c5/kraken-connector/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/tlg7c5/kraken-connector/branch/main/graph/badge.svg)](https://codecov.io/gh/tlg7c5/kraken-connector)
[![Commit activity](https://img.shields.io/github/commit-activity/m/tlg7c5/kraken-connector)](https://img.shields.io/github/commit-activity/m/tlg7c5/kraken-connector)
[![License](https://img.shields.io/github/license/tlg7c5/kraken-connector)](https://img.shields.io/github/license/tlg7c5/kraken-connector)

WS and HTTP clients for Kraken exchange API

- **Github repository**: <https://github.com/tlg7c5/kraken-connector/>
- **Documentation** <https://tlg7c5.github.io/kraken-connector/>

## Getting started with your project

First, create a repository on GitHub with the same name as this project, and then run the following commands:

```bash
git init -b main
git add .
git commit -m "init commit"
git remote add origin git@github.com:tlg7c5/kraken-connector.git
git push -u origin main
```

Finally, install the environment and the pre-commit hooks with

```bash
make install
```

You are now ready to start development on your project!
The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

To finalize the set-up for publishing to PyPi or Artifactory, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/publishing/#set-up-for-pypi).
For activating the automatic documentation with MkDocs, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/mkdocs/#enabling-the-documentation-on-github).
To enable the code coverage reports, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/codecov/).

## Releasing a new version

- Create an API Token on [Pypi](https://pypi.org/).
- Add the API Token to your projects secrets with the name `PYPI_TOKEN` by visiting [this page](https://github.com/tlg7c5/kraken-connector/settings/secrets/actions/new).
- Create a [new release](https://github.com/tlg7c5/kraken-connector/releases/new) on Github.
- Create a new tag in the form `*.*.*`.

For more details, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/cicd/#how-to-trigger-a-release).

## Usage

### Basic client

```python
from kraken_connector import HTTPClient, HTTPAuthenticatedClient

# Public endpoints
client = HTTPClient("https://api.kraken.com")

# Authenticated endpoints
auth_client = HTTPAuthenticatedClient(
    "https://api.kraken.com",
    api_key="your-api-key",
    api_secret="your-api-secret",
)
```

### Retry on network errors

Retry is disabled by default. Enable it via `ResilienceConfig`:

```python
from kraken_connector import HTTPClient, ResilienceConfig

config = ResilienceConfig(
    max_retries=3,        # retry up to 3 times on network errors
    backoff_base=1.0,     # initial backoff delay in seconds
    backoff_max=30.0,     # maximum backoff delay
)
client = HTTPClient("https://api.kraken.com", resilience=config)
```

Only transient network errors (connection refused, timeouts) are retried. API-level errors (rate limits, validation) are never retried at the transport layer — callers handle those via `KrakenAPIError`.

### Rate limiting

The `RateLimiter` is a caller-controlled token bucket matching Kraken's tier-based rate limits. It is **not** automatic — callers opt in explicitly:

```python
from kraken_connector import KrakenTier, RateLimiter
from kraken_connector.api.market_data import get_server_time

limiter = RateLimiter.from_tier(KrakenTier.STARTER)

# Sync — most API calls cost 1 token
with limiter.acquire(cost=1):
    response = get_server_time.sync(client=client)

# Async
async with limiter.async_acquire(cost=1):
    response = await get_server_time.asyncio(client=client)

# Ledger/trade history calls cost 2 tokens
with limiter.acquire(cost=2):
    response = get_trade_history.sync(client=auth_client, form_data=form)
```

The rate limiter blocks (sleeps) when tokens are depleted, waiting for the bucket to refill. It is thread-safe but not multiprocessing-safe.

**Kraken tier parameters:**

| Tier         | Max tokens | Decay rate |
| ------------ | ---------- | ---------- |
| Starter      | 15         | 0.33/sec   |
| Intermediate | 20         | 0.5/sec    |
| Pro          | 20         | 1.0/sec    |

### Request logging

Enable request/response logging via `ResilienceConfig`:

```python
import logging
from kraken_connector import HTTPClient, ResilienceConfig

logging.basicConfig(level=logging.DEBUG)

config = ResilienceConfig(enable_logging=True, log_level=logging.DEBUG)
client = HTTPClient("https://api.kraken.com", resilience=config)
# Logs: "HTTP GET https://api.kraken.com/0/public/Time"
# Logs: "HTTP GET https://api.kraken.com/0/public/Time -> 200 (0.12s)"
```

Logging uses Python's stdlib `logging` module under the logger name `kraken_connector`. Consumers can wire any logging framework (e.g., structlog) via its stdlib integration.

### WebSocket v2

The `ws` package provides a full client for [Kraken's WebSocket v2 API](https://docs.kraken.com/api/docs/websocket-v2/), with typed models, automatic reconnection, order book management, and trading support.

#### Public subscription

```python
import asyncio
from kraken_connector.ws import KrakenWSClient
from kraken_connector.ws.subscribe import TickerParams
from kraken_connector.ws.envelopes import WSDataMessage

async def main():
    async with KrakenWSClient() as client:
        await client.subscribe(TickerParams(symbol=["BTC/USD"]))
        async for msg in client:
            if isinstance(msg, WSDataMessage) and msg.channel == "ticker":
                print(msg.data)

asyncio.run(main())
```

#### Authenticated subscription

Private channels (executions, balances) require a WebSocket token. `TokenManager` handles token lifecycle automatically:

```python
from kraken_connector import HTTPAuthenticatedClient
from kraken_connector.ws import KrakenWSClient, TokenManager
from kraken_connector.ws.subscribe import ExecutionsParams

auth_client = HTTPAuthenticatedClient(
    "https://api.kraken.com",
    api_key="your-api-key",
    api_secret="your-api-secret",
)
tm = TokenManager(auth_client=auth_client)

async with KrakenWSClient(token_manager=tm) as client:
    await client.subscribe(ExecutionsParams())
    async for msg in client:
        print(msg.channel, msg.sequence, msg.data)
```

#### Trading

All 8 WS v2 trading methods are supported. The token is auto-injected when a `TokenManager` is configured:

```python
from kraken_connector.ws.trading import AddOrderParams, CancelAllOrdersAfterParams

async with KrakenWSClient(token_manager=tm) as client:
    # Place a limit order.
    resp = await client.add_order(
        AddOrderParams(
            symbol="BTC/USD",
            side="buy",
            order_type="limit",
            order_qty=0.1,
            limit_price=26000.0,
            token="",  # auto-injected by TokenManager
        )
    )
    print("Order placed:", resp.result)

    # Dead man's switch — cancel all orders if no refresh within 60s.
    await client.cancel_all_orders_after(
        CancelAllOrdersAfterParams(token="", timeout=60)
    )
```

#### Order book management

Subscribe to the `book` channel and the client maintains local order book state with CRC32 checksum validation:

```python
from kraken_connector.ws import KrakenWSClient
from kraken_connector.ws.subscribe import BookParams
from kraken_connector.ws.book import BookChecksumEvent

async with KrakenWSClient() as client:
    await client.subscribe(BookParams(symbol=["BTC/USD"], depth=10))
    async for msg in client:
        if isinstance(msg, BookChecksumEvent):
            print("Checksum mismatch — resubscribe:", msg.symbol)
            continue
        book = client.book_manager.get("BTC/USD")
        if book:
            print("Best bid:", book.best_bid, "Best ask:", book.best_ask)
```

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry). Now using [PDM](https://pdm-project.org/) for dependency management.
