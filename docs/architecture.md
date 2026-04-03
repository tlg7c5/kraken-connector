# Architecture

This page explains how kraken-connector is structured and the reasoning behind key design choices. It's aimed at contributors and anyone who wants to understand the internals.

## Module layout

```
kraken_connector/
├── __init__.py              # Public API: clients, exceptions, resilience
├── http.py                  # HTTPClient, HTTPAuthenticatedClient
├── resilience.py            # ResilienceConfig, RetryTransport, RateLimiter
├── security.py              # HMAC-SHA512 signing, nonce generation
├── exceptions.py            # KrakenAPIError, UnexpectedStatus, InvalidResponseModel
├── types.py                 # Response[T], File, Unset sentinel
├── constants/               # Enums for API parameters (order types, intervals, etc.)
├── api/                     # REST endpoint modules by domain
│   ├── market_data/
│   ├── account_data/
│   ├── trading/
│   ├── funding/
│   ├── earn/
│   ├── subaccounts/
│   └── websockets_authentication/
├── schemas/                 # attrs-based request/response models (~100+)
└── ws/                      # WebSocket v2 client
    ├── client.py            # KrakenWSClient — connection, subscriptions, trading
    ├── subscribe.py         # Typed subscription parameter models
    ├── trading.py           # Trading parameter and result models
    ├── envelopes.py         # WSRequest, WSResponse, WSDataMessage, WSErrorResponse
    ├── dispatcher.py        # Raw JSON → typed message routing
    ├── channels/            # Typed channel data models (ticker, book, trade, etc.)
    ├── book.py              # OrderBook, OrderBookManager, CRC32 validation
    ├── sequence.py          # SequenceTracker for private channel gap detection
    ├── subscriptions.py     # Subscription state tracking
    ├── token.py             # TokenManager for WS authentication
    └── constants.py         # ConnectionState, ChannelName, enums
```

## Design decisions

### attrs over pydantic

All data models use [attrs](https://www.attrs.org/) (`@define` / `@_attrs_define`). attrs was chosen for:

- **Lightweight** -- no runtime validation overhead; models are thin wrappers
- **Compatibility** -- the initial schema generation used `openapi-python-client`, which targets attrs
- **Explicit serialization** -- `to_dict()` / `from_dict()` class methods give full control over field mapping

### httpx over requests

[httpx](https://www.python-httpx.org/) provides both sync and async clients from a single API. This lets every REST endpoint expose `sync()` and `asyncio()` variants without maintaining two HTTP stacks.

The `ResilienceConfig` integrates at the httpx transport layer (`RetryTransport` / `AsyncRetryTransport`), keeping retry logic transparent to endpoint modules.

### websockets for WS transport

The [websockets](https://websockets.readthedocs.io/) library was chosen for its clean async API and close adherence to the WebSocket protocol specification. The `KrakenWSClient` wraps a single `websockets.connect()` connection.

### Code generation for schemas

The `kraken_connector/schemas/` directory was initially generated from Kraken's OpenAPI specification (`openapi.json`) using [openapi-python-client](https://github.com/openapi-generators/openapi-python-client). This produces one attrs class per schema with consistent `to_dict()` / `from_dict()` methods.

The `api/` endpoint modules were also generated from the same spec, producing the four-function pattern (`sync`, `sync_detailed`, `asyncio`, `asyncio_detailed`) for each endpoint.

### Unset sentinel

Optional fields use a custom `Unset` sentinel (not `None`) to distinguish "field not provided" from "field explicitly set to null." This matches the OpenAPI spec's distinction between omitted and null-valued fields.

```python
from kraken_connector.types import UNSET, Unset

if not isinstance(field_value, Unset):
    # field was explicitly provided
```

## Data flow

### REST request

```
Caller
  → endpoint module (get_server_time.sync)
    → HTTPClient.get_or_create_httpx_client()
      → RetryTransport (if configured)
        → httpx.Client.request()
          → Kraken REST API
    ← httpx.Response
    → _parse_response() → Schema.from_dict()
  ← Response[T] or parsed model
```

### WebSocket message

```
Kraken WS v2
  → websockets connection
    → _recv_loop()
      → parse_message() (dispatcher)
        → typed message (WSDataMessage, WSResponse, etc.)
      → internal routing:
          - status → _handle_status()
          - pong → _pong_event.set()
          - heartbeat → dropped
          - book data → OrderBookManager.process_message()
          - sequence check → SequenceTracker.check()
          - req_id correlation → resolve pending Future
      → message_queue.put()
    ← async for msg in client (consumer)
```

## Background tasks

`KrakenWSClient` runs three background `asyncio.Task`s:

| Task                 | Purpose                                          |
| -------------------- | ------------------------------------------------ |
| `_recv_loop`         | Receive and dispatch messages from the WebSocket |
| `_ping_loop`         | Send periodic pings and await pong responses     |
| `_heartbeat_monitor` | Detect server silence and trigger reconnection   |

All three are cancelled on disconnect and restarted on reconnect.
