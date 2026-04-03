# WebSocket Client

`KrakenWSClient` provides an async client for [Kraken's WebSocket API v2](https://docs.kraken.com/api/docs/websocket-v2/) with typed models, automatic reconnection, and subscription tracking.

## Connection lifecycle

The client is an async context manager:

```python
from kraken_connector.ws import KrakenWSClient

async with KrakenWSClient() as client:
    # connected -- subscribe and iterate
    ...
# disconnected
```

Or manage the connection manually:

```python
client = KrakenWSClient()
await client.connect()
# ...
await client.disconnect()
```

## Configuration

All parameters are optional with sensible defaults:

```python
client = KrakenWSClient(
    url="wss://ws.kraken.com/v2",       # WebSocket endpoint
    ping_interval=10.0,                  # seconds between client pings
    ping_timeout=10.0,                   # max wait for pong response
    heartbeat_timeout=30.0,              # max silence before reconnect
    backoff_base=0.5,                    # base delay for exponential backoff
    backoff_max=30.0,                    # maximum backoff delay
    max_reconnect_attempts=10,           # 0 = disable auto-reconnect
    request_timeout=10.0,               # max wait for subscribe/trading responses
    token_manager=None,                  # TokenManager for private channels
)
```

## Subscribing to channels

Subscribe using typed parameter objects:

```python
from kraken_connector.ws.subscribe import (
    TickerParams,
    BookParams,
    TradeParams,
    OHLCParams,
    InstrumentParams,
)

await client.subscribe(TickerParams(symbol=["BTC/USD", "ETH/USD"]))
await client.subscribe(BookParams(symbol=["BTC/USD"], depth=25))
await client.subscribe(TradeParams(symbol=["BTC/USD"]))
await client.subscribe(OHLCParams(symbol=["BTC/USD"], interval=5))
await client.subscribe(InstrumentParams())
```

Unsubscribe with the same params:

```python
await client.unsubscribe(TickerParams(symbol=["BTC/USD", "ETH/USD"]))
```

### Private channels

Private channels require a `TokenManager`. See [Authentication](../getting-started/authentication.md).

```python
from kraken_connector.ws.subscribe import ExecutionsParams, BalancesParams

# Token is injected automatically when TokenManager is configured
await client.subscribe(ExecutionsParams(snap_orders=True))
await client.subscribe(BalancesParams(snapshot=True))
```

## Receiving messages

Use `async for` to iterate over typed messages:

```python
from kraken_connector.ws.envelopes import WSDataMessage, WSErrorResponse

async for msg in client:
    if isinstance(msg, WSDataMessage):
        print(msg.channel, msg.type, msg.data)
    elif isinstance(msg, WSErrorResponse):
        print("Error:", msg.error)
```

Or receive one at a time:

```python
msg = await client.receive()
```

### Message types

| Type                | Description                                                            |
| ------------------- | ---------------------------------------------------------------------- |
| `WSDataMessage`     | Channel data (ticker, book, trade, ohlc, executions, balances, status) |
| `WSResponse`        | Success response to subscribe/unsubscribe/trading requests             |
| `WSErrorResponse`   | Error response to a request                                            |
| `SequenceGapEvent`  | Private channel sequence gap detected                                  |
| `BookChecksumEvent` | Order book checksum mismatch detected                                  |

Heartbeats and pong responses are handled internally and never reach the message queue.

## Automatic reconnection

When the connection drops (network error, pong timeout, heartbeat timeout), the client automatically:

1. Closes the dead connection
2. Retries with exponential backoff (up to `max_reconnect_attempts`)
3. Re-subscribes to all tracked channels
4. Invalidates and re-fetches the WebSocket token (if using `TokenManager`)
5. Resets the sequence tracker and clears order book state

During reconnection, `async for` blocks rather than raising `StopAsyncIteration`, so your consumer loop stays intact.

Set `max_reconnect_attempts=0` to disable auto-reconnect.

## Connection state

```python
from kraken_connector.ws.constants import ConnectionState

client.state          # ConnectionState.CONNECTED, DISCONNECTED, etc.
client.system_status  # "online", "maintenance", etc.
client.connection_id  # integer connection ID from the server
```
