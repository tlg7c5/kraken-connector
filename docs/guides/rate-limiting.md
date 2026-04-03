# Rate Limiting

Kraken enforces tier-based rate limits on the REST API. kraken-connector provides a caller-controlled token-bucket `RateLimiter` that matches these limits.

## Setup

Create a limiter from your Kraken account tier:

```python
from kraken_connector import KrakenTier, RateLimiter

limiter = RateLimiter.from_tier(KrakenTier.STARTER)
```

## Usage

Wrap each API call in `acquire()` (sync) or `async_acquire()` (async). The limiter blocks when tokens are depleted, waiting for the bucket to refill:

=== "Sync"

    ```python
    from kraken_connector.api.market_data import get_server_time

    with limiter.acquire(cost=1):
        response = get_server_time.sync(client=client)
    ```

=== "Async"

    ```python
    async with limiter.async_acquire(cost=1):
        response = await get_server_time.asyncio(client=client)
    ```

## Token costs

Most API calls cost **1 token**. Ledger and trade history calls cost **2 tokens**:

```python
from kraken_connector.api.account_data import get_trades_history

with limiter.acquire(cost=2):
    response = get_trades_history.sync(client=auth_client, form_data=form)
```

## Tier parameters

| Tier         | Max tokens | Decay rate |
| ------------ | ---------- | ---------- |
| Starter      | 15         | 0.33/sec   |
| Intermediate | 20         | 0.5/sec    |
| Pro          | 20         | 1.0/sec    |

The limiter is **thread-safe** (uses `threading.Lock` for sync, `asyncio.Lock` for async) but **not multiprocessing-safe**. If you run multiple processes against the same API key, coordinate externally.

## Custom configuration

For non-standard setups, construct `RateLimiter` directly:

```python
limiter = RateLimiter(max_tokens=20.0, decay_rate=1.0)
```
