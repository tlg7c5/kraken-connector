# kraken-connector

A typed Python client for the Kraken cryptocurrency exchange, covering both the REST API and WebSocket API v2.

Built on [httpx](https://www.python-httpx.org/) for HTTP, [websockets](https://websockets.readthedocs.io/) for streaming, and [attrs](https://www.attrs.org/) for data models.

## Highlights

- **REST API** with typed request/response models across 7 endpoint groups
- **WebSocket v2** async client with typed channel models and automatic reconnection
- **Trading** via all 8 WS v2 methods with automatic token injection
- **Order book management** with CRC32 checksum validation
- **Rate limiting** matching Kraken's tier-based limits
- **Fully typed** with `py.typed` marker and strict mypy

## Install

```bash
pip install kraken-connector
```

## Next steps

<div class="grid cards" markdown>

-   :material-rocket-launch: **[Getting Started](getting-started/installation.md)**

    ---

    Install and make your first API call

-   :material-book-open-variant: **[Guides](guides/rest-api.md)**

    ---

    In-depth walkthroughs for REST, WebSocket, trading, and more

-   :material-sitemap: **[Architecture](architecture.md)**

    ---

    How the library is structured and why

-   :material-api: **[API Reference](reference/http.md)**

    ---

    Auto-generated reference from source docstrings

</div>
