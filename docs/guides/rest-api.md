# REST API

## Endpoint modules

REST endpoints are organized by Kraken API domain under `kraken_connector.api`:

| Module                      | Description                                                                        |
| --------------------------- | ---------------------------------------------------------------------------------- |
| `market_data`               | Public market data (server time, assets, ticker, OHLC, order book, trades, spread) |
| `account_data`              | Account balance, trade balance, open/closed orders, trade history, positions       |
| `trading`                   | Add/cancel/edit orders                                                             |
| `funding`                   | Deposit/withdrawal methods, addresses, status                                      |
| `earn`                      | Staking strategies, allocations                                                    |
| `subaccounts`               | Subaccount management                                                              |
| `websockets_authentication` | WebSocket token generation                                                         |

Import any endpoint directly:

```python
from kraken_connector.api.market_data import get_server_time
from kraken_connector.api.account_data import get_account_balance
from kraken_connector.api.trading import add_order
```

## Calling endpoints

Every endpoint module exposes four functions:

=== "sync"

    ```python
    from kraken_connector import HTTPClient
    from kraken_connector.api.market_data import get_server_time

    client = HTTPClient("https://api.kraken.com")
    response = get_server_time.sync(client=client)
    ```

=== "asyncio"

    ```python
    response = await get_server_time.asyncio(client=client)
    ```

=== "sync_detailed"

    ```python
    resp = get_server_time.sync_detailed(client=client)
    print(resp.status_code)  # HTTPStatus.OK
    print(resp.headers)
    print(resp.parsed)       # ServerTimeResponse
    ```

=== "asyncio_detailed"

    ```python
    resp = await get_server_time.asyncio_detailed(client=client)
    ```

The `_detailed` variants return a `Response[T]` wrapper with `status_code`, `headers`, `content` (raw bytes), and `parsed` (the typed model).

The plain `sync()` / `asyncio()` variants return just the parsed model (or `None` on undocumented status codes).

## Endpoints with request data

Private and parameterized endpoints accept `form_data` or `json_body`:

```python
from kraken_connector import HTTPAuthenticatedClient
from kraken_connector.api.account_data import get_account_balance

auth_client = HTTPAuthenticatedClient(
    "https://api.kraken.com",
    api_key="your-key",
    api_secret="your-secret",
)
balance = get_account_balance.sync(client=auth_client)
```

## Response models

Responses are deserialized into attrs-based models under `kraken_connector.schemas`. Every model has:

- `to_dict()` -- serialize back to a plain dict
- `from_dict(d)` -- class method to construct from a dict

```python
response = get_server_time.sync(client=client)
if response:
    print(response.to_dict())
```

## Error handling

See [Error Handling](error-handling.md) for the full error taxonomy. The key patterns:

```python
from kraken_connector import KrakenAPIError, UnexpectedStatus

try:
    balance = get_account_balance.sync(client=auth_client)
except KrakenAPIError as e:
    print("API error:", e.errors)
except UnexpectedStatus as e:
    print("HTTP", e.status_code)
```
