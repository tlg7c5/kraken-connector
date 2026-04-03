# Logging

kraken-connector uses Python's stdlib `logging` module. All loggers are under the `kraken_connector` namespace.

## REST request logging

Enable request/response logging via `ResilienceConfig`:

```python
import logging
from kraken_connector import HTTPClient, ResilienceConfig

logging.basicConfig(level=logging.DEBUG)

config = ResilienceConfig(enable_logging=True, log_level=logging.DEBUG)
client = HTTPClient("https://api.kraken.com", resilience=config)
```

This logs:

```
DEBUG kraken_connector: HTTP GET https://api.kraken.com/0/public/Time
DEBUG kraken_connector: HTTP GET https://api.kraken.com/0/public/Time -> 200 (0.12s)
```

## Retry logging

When retry is enabled, transient failures are logged at WARNING:

```python
config = ResilienceConfig(max_retries=3, enable_logging=True)
client = HTTPClient("https://api.kraken.com", resilience=config)
```

```
WARNING kraken_connector: Retry 1/3 after 0.50s: [ConnectTimeout]
```

## WebSocket logging

The WebSocket client logs under `kraken_connector.ws`:

| Event                 | Level   | Example                                         |
| --------------------- | ------- | ----------------------------------------------- |
| Connect/disconnect    | INFO    | `Connecting to wss://ws.kraken.com/v2`          |
| System status         | INFO    | `System status: online (connection 12345)`      |
| Reconnect attempts    | WARNING | `Reconnect 1/10 after 0.50s`                    |
| Pong timeout          | WARNING | `Pong timeout after 10.0s`                      |
| Heartbeat timeout     | WARNING | `Heartbeat timeout: 31.2s since last message`   |
| Sequence gap          | WARNING | `Sequence gap on executions: expected 5, got 7` |
| Checksum mismatch     | WARNING | `Book checksum mismatch for BTC/USD`            |
| Re-subscribe failures | ERROR   | `Re-subscribe failed for ticker: ...`           |
| Max retries exhausted | ERROR   | `Max reconnect attempts (10) reached`           |

## Logger names

| Logger                | Source                                              |
| --------------------- | --------------------------------------------------- |
| `kraken_connector`    | REST client request/response hooks, retry transport |
| `kraken_connector.ws` | WebSocket client lifecycle and events               |

## Integration with structlog

Since kraken-connector uses stdlib logging, any framework with stdlib integration works:

```python
import structlog

structlog.configure(
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)
```
