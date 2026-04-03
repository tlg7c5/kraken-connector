# Quick Start

## REST API

Create an `HTTPClient` and call any endpoint module:

=== "Sync"

    ```python
    from kraken_connector import HTTPClient
    from kraken_connector.api.market_data import get_server_time

    client = HTTPClient("https://api.kraken.com")
    response = get_server_time.sync(client=client)
    print(response)
    ```

=== "Async"

    ```python
    import asyncio
    from kraken_connector import HTTPClient
    from kraken_connector.api.market_data import get_server_time

    async def main():
        client = HTTPClient("https://api.kraken.com")
        response = await get_server_time.asyncio(client=client)
        print(response)

    asyncio.run(main())
    ```

Every endpoint module exposes four functions:

| Function             | Returns                | Description                                           |
| -------------------- | ---------------------- | ----------------------------------------------------- |
| `sync()`             | Parsed model or `None` | Sync call, returns just the parsed response           |
| `sync_detailed()`    | `Response[T]`          | Sync call with status code, headers, and parsed body  |
| `asyncio()`          | Parsed model or `None` | Async call, returns just the parsed response          |
| `asyncio_detailed()` | `Response[T]`          | Async call with status code, headers, and parsed body |

## WebSocket

Connect to the Kraken WebSocket v2 API and stream data:

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

`KrakenWSClient` is an async context manager. It connects on `__aenter__` and disconnects on `__aexit__`. Use `async for` to iterate over incoming messages.

## Next steps

- [Authentication](authentication.md) -- set up authenticated clients for private endpoints
- [REST API guide](../guides/rest-api.md) -- endpoint module structure and response handling
- [WebSocket guide](../guides/websocket.md) -- subscriptions, reconnection, and message types
