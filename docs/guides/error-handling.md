# Error Handling

kraken-connector uses a layered exception hierarchy. Each layer surfaces a different class of failure.

## REST API errors

### KrakenAPIError

Raised when the Kraken API returns an error in the response body (HTTP 200 with error payload):

```python
from kraken_connector import KrakenAPIError

try:
    balance = get_account_balance.sync(client=auth_client)
except KrakenAPIError as e:
    print(e.errors)  # list[str], e.g. ["EGeneral:Invalid arguments"]
```

### UnexpectedStatus

Raised when the server returns an HTTP status code not documented in the OpenAPI spec, **only** if `raise_on_unexpected_status=True` on the client:

```python
from kraken_connector import HTTPClient, UnexpectedStatus

client = HTTPClient("https://api.kraken.com", raise_on_unexpected_status=True)

try:
    response = get_server_time.sync(client=client)
except UnexpectedStatus as e:
    print(e.status_code)  # int
    print(e.content)      # bytes
```

When `raise_on_unexpected_status=False` (default), undocumented status codes return `None`.

### InvalidResponseModel

Raised during deserialization when the response body is missing required fields:

```python
from kraken_connector import InvalidResponseModel

try:
    response = get_server_time.sync(client=client)
except InvalidResponseModel:
    print("Response didn't match expected schema")
```

### httpx exceptions

Network-level errors (timeouts, connection failures) propagate as standard `httpx` exceptions:

- `httpx.TimeoutException` -- request exceeded the client timeout
- `httpx.ConnectError` -- could not connect to the server

When [retry](logging.md) is configured, transient errors are retried before propagating.

## WebSocket errors

### SubscriptionError

Raised when the server rejects a subscribe or unsubscribe request:

```python
from kraken_connector.ws import SubscriptionError

try:
    await client.subscribe(TickerParams(symbol=["INVALID/PAIR"]))
except SubscriptionError as e:
    print(e.error)    # str, server error message
    print(e.req_id)   # int or None
```

### TradingError

Raised when the server rejects a trading method request:

```python
from kraken_connector.ws import TradingError

try:
    resp = await client.add_order(params)
except TradingError as e:
    print(e.error)
    print(e.req_id)
```

### TokenAcquisitionError

Raised by `TokenManager` when a WebSocket auth token cannot be obtained:

```python
from kraken_connector.ws import TokenAcquisitionError

try:
    async with KrakenWSClient(token_manager=tm) as client:
        await client.subscribe(ExecutionsParams())
except TokenAcquisitionError as e:
    print("Could not get WS token:", e)
```

### asyncio.TimeoutError

Raised when a subscribe, unsubscribe, or trading request doesn't receive a response within `request_timeout` (default 10 seconds).

## Event-based signals

Some conditions are surfaced as events in the message queue rather than exceptions, so they don't break the consumer loop:

### BookChecksumEvent

Emitted when a CRC32 checksum mismatch is detected on the order book. See [Order Book](order-book.md).

### SequenceGapEvent

Emitted when a gap is detected in the private channel sequence numbers, indicating missed messages:

```python
from kraken_connector.ws import SequenceGapEvent

async for msg in client:
    if isinstance(msg, SequenceGapEvent):
        print(f"Gap on {msg.channel}: expected {msg.expected}, got {msg.received}")
```
