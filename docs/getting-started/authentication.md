# Authentication

Kraken's private endpoints (account data, trading, funding) require an API key and secret. The WebSocket private channels additionally require a short-lived token obtained via the REST API.

## REST API authentication

Use `HTTPAuthenticatedClient` for private REST endpoints:

```python
from kraken_connector import HTTPAuthenticatedClient

auth_client = HTTPAuthenticatedClient(
    "https://api.kraken.com",
    api_key="your-api-key",
    api_secret="your-api-secret",
)
```

The client injects the `API-Key` header automatically. Each request is signed with an HMAC-SHA512 signature (`API-Sign`) computed from your secret and the request payload.

!!! warning "Never hard-code credentials"
Use environment variables or a secrets manager:

    ```python
    import os

    auth_client = HTTPAuthenticatedClient(
        "https://api.kraken.com",
        api_key=os.environ["KRAKEN_API_KEY"],
        api_secret=os.environ["KRAKEN_API_SECRET"],
    )
    ```

## Obtaining API keys

1. Log in to your Kraken account
2. Navigate to **Security** > **API**
3. Create a new key with the permissions your application needs
4. Copy the key and secret immediately -- the secret is only shown once

## WebSocket authentication

Private WebSocket channels (executions, balances) require a token from the `GetWebSocketsToken` REST endpoint. `TokenManager` handles the full lifecycle -- acquisition, caching, and refresh before expiry:

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
        print(msg.channel, msg.data)
```

When a `TokenManager` is configured:

- **Subscriptions**: Private channel params (`ExecutionsParams`, `BalancesParams`) get the token injected automatically
- **Trading methods**: The token is auto-injected into all trading requests
- **Reconnection**: The token is invalidated and re-fetched on reconnect

The `TokenManager` caches the token and refreshes it 60 seconds before expiry (configurable via `refresh_margin`).
