# Trading

All 8 Kraken WebSocket v2 trading methods are supported. A `TokenManager` must be configured for automatic token injection.

## Setup

```python
from kraken_connector import HTTPAuthenticatedClient
from kraken_connector.ws import KrakenWSClient, TokenManager

auth_client = HTTPAuthenticatedClient(
    "https://api.kraken.com",
    api_key="your-api-key",
    api_secret="your-api-secret",
)
tm = TokenManager(auth_client=auth_client)

async with KrakenWSClient(token_manager=tm) as client:
    # trading methods available here
    ...
```

## Place an order

```python
from kraken_connector.ws.trading import AddOrderParams

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
```

Use `validate=True` for dry-run validation without execution.

## Amend an order

Amend modifies an order **in-place**, preserving the original `order_id` and queue priority:

```python
from kraken_connector.ws.trading import AmendOrderParams

resp = await client.amend_order(
    AmendOrderParams(
        order_id="OXXXXX-XXXXX-XXXXXX",
        token="",
        limit_price=26500.0,
    )
)
```

## Edit an order

Edit is a **cancel-and-replace** -- a new `order_id` is assigned:

```python
from kraken_connector.ws.trading import EditOrderParams

resp = await client.edit_order(
    EditOrderParams(
        order_id="OXXXXX-XXXXX-XXXXXX",
        symbol="BTC/USD",
        token="",
        order_qty=0.2,
        limit_price=26500.0,
    )
)
```

## Cancel orders

```python
from kraken_connector.ws.trading import (
    CancelOrderParams,
    CancelAllParams,
)

# Cancel specific orders
await client.cancel_order(
    CancelOrderParams(token="", order_id=["OXXXXX-XXXXX-XXXXXX"])
)

# Cancel all open orders
await client.cancel_all(CancelAllParams(token=""))
```

## Dead man's switch

Auto-cancel all orders if the timer isn't refreshed:

```python
from kraken_connector.ws.trading import CancelAllOrdersAfterParams

# Set a 60-second dead man's switch
await client.cancel_all_orders_after(
    CancelAllOrdersAfterParams(token="", timeout=60)
)

# Disable the timer
await client.cancel_all_orders_after(
    CancelAllOrdersAfterParams(token="", timeout=0)
)
```

## Batch operations

### Batch add (2-15 orders on a single pair)

```python
from kraken_connector.ws.trading import BatchAddParams, AddOrderParams

await client.batch_add(
    BatchAddParams(
        symbol="BTC/USD",
        token="",
        orders=[
            AddOrderParams(
                symbol="BTC/USD", side="buy", order_type="limit",
                order_qty=0.1, limit_price=25000.0, token="",
            ),
            AddOrderParams(
                symbol="BTC/USD", side="buy", order_type="limit",
                order_qty=0.1, limit_price=24000.0, token="",
            ),
        ],
    )
)
```

### Batch cancel (2-50 orders)

```python
from kraken_connector.ws.trading import BatchCancelParams

await client.batch_cancel(
    BatchCancelParams(
        token="",
        orders=["OXXXXX-XXXXX-XXXXXX", "OYYYYY-YYYYY-YYYYYY"],
    )
)
```

## Error handling

Trading errors raise `TradingError`:

```python
from kraken_connector.ws import TradingError

try:
    resp = await client.add_order(params)
except TradingError as e:
    print("Rejected:", e.error)
    print("Request ID:", e.req_id)
```

Timeout waiting for a server response raises `asyncio.TimeoutError`. The timeout is controlled by `request_timeout` on the client (default 10 seconds).
