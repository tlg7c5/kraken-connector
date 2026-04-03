# Order Book Management

The WebSocket client maintains local order book state from snapshot and incremental update messages, with CRC32 checksum validation for data integrity.

## Subscribing

```python
from kraken_connector.ws import KrakenWSClient
from kraken_connector.ws.subscribe import BookParams

async with KrakenWSClient() as client:
    await client.subscribe(BookParams(symbol=["BTC/USD"], depth=10))
```

Available depths: **10**, **25**, **100**, **500**, **1000**.

## Reading book state

The `book_manager` property provides access to the local order book:

```python
book = client.book_manager.get("BTC/USD")
if book:
    print("Best bid:", book.best_bid)   # (Decimal price, Decimal qty) or None
    print("Best ask:", book.best_ask)
    print("Spread:", book.spread)       # Decimal or None
    print("Asks:", book.asks[:5])       # sorted ascending by price
    print("Bids:", book.bids[:5])       # sorted descending by price
```

The book is automatically updated as snapshot and incremental update messages arrive on the `book` channel. You don't need to apply updates manually.

## Checksum validation

Kraken sends CRC32 checksums with incremental book updates. The client validates these automatically. When a mismatch occurs, a `BookChecksumEvent` is emitted to the message queue instead of raising an exception:

```python
from kraken_connector.ws.book import BookChecksumEvent

async for msg in client:
    if isinstance(msg, BookChecksumEvent):
        print(f"Checksum mismatch for {msg.symbol}")
        print(f"  Expected: {msg.expected}, Computed: {msg.computed}")
        # Resubscribe to get a fresh snapshot
        await client.unsubscribe(BookParams(symbol=[msg.symbol], depth=10))
        await client.subscribe(BookParams(symbol=[msg.symbol], depth=10))
        continue

    book = client.book_manager.get("BTC/USD")
    if book:
        print(book.best_bid, book.best_ask)
```

## Reconnection behavior

On reconnect, the book manager is **cleared** and a fresh snapshot is obtained when the book channel is re-subscribed. This ensures consistency after any missed updates.

## Multiple symbols

Subscribe to multiple symbols and access each book independently:

```python
await client.subscribe(BookParams(symbol=["BTC/USD", "ETH/USD"], depth=25))

btc_book = client.book_manager.get("BTC/USD")
eth_book = client.book_manager.get("ETH/USD")
```
