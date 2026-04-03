# kraken-connector

[![Release](https://img.shields.io/github/v/release/tlg7c5/kraken-connector)](https://img.shields.io/github/v/release/tlg7c5/kraken-connector)
[![Build status](https://img.shields.io/github/actions/workflow/status/tlg7c5/kraken-connector/main.yml?branch=main)](https://github.com/tlg7c5/kraken-connector/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/tlg7c5/kraken-connector/branch/main/graph/badge.svg)](https://codecov.io/gh/tlg7c5/kraken-connector)
[![License](https://img.shields.io/github/license/tlg7c5/kraken-connector)](https://img.shields.io/github/license/tlg7c5/kraken-connector)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/kraken-connector)](https://pypi.org/project/kraken-connector/)

A typed Python client for the [Kraken](https://www.kraken.com/) cryptocurrency exchange, covering both the REST API and WebSocket API v2. Built on [httpx](https://www.python-httpx.org/) for HTTP, [websockets](https://websockets.readthedocs.io/) for streaming, and [attrs](https://www.attrs.org/) for data models.

## Features

- **REST API** -- typed request/response models across 7 endpoint groups (market data, account data, trading, funding, earn, subaccounts, websocket auth)
- **WebSocket v2** -- async client with typed channel models for ticker, OHLC, trades, order book, executions, and balances
- **Trading** -- all 8 WS v2 trading methods (add, edit, cancel, batch add, batch cancel, cancel all, cancel all after, amend)
- **Order book management** -- local order book state with incremental updates and CRC32 checksum validation
- **Automatic reconnection** -- configurable backoff with subscription and sequence tracking across reconnects
- **Rate limiting** -- caller-controlled token-bucket limiter matching Kraken's tier-based rate limits
- **Retry** -- configurable retry transport with exponential backoff for transient network errors
- **Request logging** -- optional request/response logging via Python's stdlib `logging`
- **Fully typed** -- `py.typed` marker, strict mypy, attrs-based models with `to_dict()`/`from_dict()`

## Requirements

Python 3.11+

## Installation

```bash
pip install kraken-connector
```

## Quick Start

### REST API

```python
from kraken_connector import HTTPClient
from kraken_connector.api.market_data import get_server_time

client = HTTPClient("https://api.kraken.com")
response = get_server_time.sync(client=client)
print(response)
```

### WebSocket

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

See the [documentation](https://tlg7c5.github.io/kraken-connector/) for guides on authentication, rate limiting, trading, order book management, error handling, and more.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

[MIT](LICENSE)
