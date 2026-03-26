# WebSocket v2 Build Plan

**Created:** 2026-03-25
**Status:** Planning
**Audit reference:** V2-01

---

## Objective

Build a new WebSocket v2 client for the Kraken exchange API, targeting async-first usage in an event-driven trading bot. The old `ws.py` (v1, non-functional) was deleted during the code audit. This is a ground-up build.

---

## Coverage Matrix

Audit of all Kraken WS v2 features against current implementation status.

### Methods (request/response)

| Method                    | Kraken WS v2 |                   Model                   |     Client Method      | Phase |   Status    |
| ------------------------- | :----------: | :---------------------------------------: | :--------------------: | :---: | :---------: |
| `ping` / `pong`           |     Yes      |      `PingRequest` / `PongResponse`       |       Automatic        |   2   |    Done     |
| `subscribe`               |     Yes      |                `WSRequest`                |  `client.subscribe()`  |   3   |    Done     |
| `unsubscribe`             |     Yes      |                `WSRequest`                | `client.unsubscribe()` |   3   |    Done     |
| `add_order`               |     Yes      |    `AddOrderParams` / `AddOrderResult`    |           —            |   6   | Model only  |
| `amend_order`             |     Yes      |                     —                     |           —            |   6   | Not started |
| `edit_order`              |     Yes      |   `EditOrderParams` / `EditOrderResult`   |           —            |   6   | Model only  |
| `cancel_order`            |     Yes      | `CancelOrderParams` / `CancelOrderResult` |           —            |   6   | Model only  |
| `cancel_all`              |     Yes      |   `CancelAllParams` / `CancelAllResult`   |           —            |   6   | Model only  |
| `cancel_all_orders_after` |     Yes      |                     —                     |           —            |   6   | Not started |
| `batch_add`               |     Yes      |    `BatchAddParams` / `BatchAddResult`    |           —            |   6   | Model only  |
| `batch_cancel`            |     Yes      | `BatchCancelParams` / `BatchCancelResult` |           —            |   6   | Model only  |

### Channels (subscription data feeds)

| Channel      | Kraken WS v2 |          Model           |    Subscribable    | Phase |   Status   |
| ------------ | :----------: | :----------------------: | :----------------: | :---: | :--------: |
| `ticker`     |     Yes      |       `TickerData`       |        Yes         |  1/3  |    Done    |
| `book`       |     Yes      | `BookData` / `BookLevel` |        Yes         |  1/3  |    Done    |
| `trade`      |     Yes      |       `TradeData`        |        Yes         |  1/3  |    Done    |
| `ohlc`       |     Yes      |        `OHLCData`        |        Yes         |  1/3  |    Done    |
| `instrument` |     Yes      |     `InstrumentData`     |        Yes         |  1/3  |    Done    |
| `executions` |     Yes      |     `ExecutionData`      |    Params only     |   4   | Model only |
| `balances`   |     Yes      |    `BalanceSnapshot`     |    Params only     |   4   | Model only |
| `heartbeat`  |     Auto     |    `HeartbeatMessage`    |  Auto (filtered)   |   2   |    Done    |
| `status`     |     Auto     |       `StatusData`       | Auto (intercepted) |   2   |    Done    |
| `level3`     |     Yes      |            —             |         —          |   —   |  Deferred  |

---

## Design Principles

1. **Async-first.** The WebSocket protocol is inherently async. Sync wrappers are out of scope for the initial build — callers run in an asyncio event loop.
2. **Typed throughout.** All messages — inbound and outbound — are `attrs` classes with `to_dict()` / `from_dict()` for serialization. No raw dicts cross the public API boundary.
3. **Explicit over automatic.** Subscription management and rate limiting are caller-controlled. The client provides the primitives; the caller decides policy.
4. **Correctness over speed.** Book checksums are validated. Sequence gaps are detected. Decimal parsing is used where precision matters.
5. **Testable without a network.** Every layer is testable with mock transports. No integration test requires a live Kraken connection.

---

## Protocol Reference

### Endpoints

| Environment | Public                        | Private                            |
| ----------- | ----------------------------- | ---------------------------------- |
| Production  | `wss://ws.kraken.com/v2`      | `wss://ws-auth.kraken.com/v2`      |
| Beta        | `wss://beta-ws.kraken.com/v2` | `wss://beta-ws-auth.kraken.com/v2` |

### Message Envelope

All messages are JSON. Three shapes:

**Client → Server (request):**

```json
{
  "method": "subscribe",
  "params": { "channel": "ticker", "symbol": ["BTC/USD"] },
  "req_id": 12345
}
```

**Server → Client (response to request):**

```json
{
  "method": "subscribe",
  "result": { "channel": "ticker", "symbol": "BTC/USD" },
  "success": true,
  "time_in": "2023-09-25T09:04:31.742599Z",
  "time_out": "2023-09-25T09:04:31.742648Z",
  "req_id": 12345
}
```

**Server → Client (error response):**

```json
{
  "method": "subscribe",
  "error": "Currency pair not supported XBT/USD",
  "success": false,
  "time_in": "...",
  "time_out": "...",
  "req_id": 12345
}
```

**Server → Client (data feed):**

```json
{
  "channel": "ticker",
  "type": "snapshot",
  "data": [ ... ]
}
```

Conventions:

- `req_id` (optional integer) is echoed back for client-side correlation
- `time_in` / `time_out` on all responses (RFC3339)
- Prices and quantities are numbers (use `Decimal` parsing for book checksums)
- Errors are string-based, no numeric codes

### Channels

#### Public (on `wss://ws.kraken.com/v2`)

| Channel      | Description                                | Key Params                                                     |
| ------------ | ------------------------------------------ | -------------------------------------------------------------- |
| `ticker`     | L1 best bid/offer + recent trade stats     | `symbol[]`, `event_trigger` ("bbo" or "trades")                |
| `book`       | L2 aggregated order book                   | `symbol[]`, `depth` (10/25/100/500/1000)                       |
| `trade`      | Matched trades                             | `symbol[]`, `snapshot` (default false)                         |
| `ohlc`       | OHLC candles                               | `symbol[]`, `interval` (1/5/15/30/60/240/1440/10080/21600 min) |
| `instrument` | Reference data for all assets + pairs      | `include_tokenized_assets`                                     |
| `level3`     | Individual orders in book (requires token) | `symbol[]`, `depth`, `token`                                   |

#### Private (on `wss://ws-auth.kraken.com/v2`)

| Channel      | Description                     | Key Params                                                           |
| ------------ | ------------------------------- | -------------------------------------------------------------------- |
| `executions` | Order lifecycle + trade fills   | `token`, `snap_orders`, `snap_trades`, `order_status`, `ratecounter` |
| `balances`   | Asset balances + ledger updates | `token`, `snapshot`                                                  |

#### Automatic (no subscription)

| Channel     | Description                                                                             |
| ----------- | --------------------------------------------------------------------------------------- |
| `heartbeat` | Sent ~1/sec when no other data flowing                                                  |
| `status`    | System state on connect + changes (`online`, `maintenance`, `cancel_only`, `post_only`) |

### Trading Methods (on `wss://ws-auth.kraken.com/v2`)

| Method                    | Description                                                           |
| ------------------------- | --------------------------------------------------------------------- |
| `add_order`               | Place single order                                                    |
| `amend_order`             | In-place order modification (preserves queue priority, same order_id) |
| `edit_order`              | Cancel-and-replace (new `order_id`, broader field support)            |
| `cancel_order`            | Cancel one or more orders                                             |
| `cancel_all`              | Cancel all open orders                                                |
| `cancel_all_orders_after` | Dead man's switch — auto-cancel all orders after timeout (in seconds) |
| `batch_add`               | Place 2–15 orders on one pair                                         |
| `batch_cancel`            | Cancel 2–50 orders                                                    |

All require `token` in params.

### Authentication

1. Obtain token via REST: `POST /0/private/GetWebSocketsToken` (existing endpoint in library)
2. Connect to `wss://ws-auth.kraken.com/v2`
3. Pass `token` in subscription params and trading method params
4. Token expires in 15 minutes; at least one private subscription must remain active

### Keepalive

- Server sends `{"channel": "heartbeat"}` ~1/sec when idle
- Server closes connections after ~60s of inactivity
- Client should send periodic `ping` requests; server responds with `pong`

### Reconnection

- No automatic subscription restoration — client must re-subscribe after reconnect
- Connection rate limit: ~150 per IP per 10min rolling window (Cloudflare); 10min ban on violation
- Recommended: immediate reconnect for random disconnects, 5s minimum interval after maintenance

### Rate Limits (Trading)

Trading rate limits are shared across REST, WebSocket, and FIX. Per-pair token bucket with tier-based thresholds and decay. The existing `RateLimiter` class applies here.

| Tier         | Threshold | Decay/sec |
| ------------ | --------- | --------- |
| Starter      | 60        | 1/sec     |
| Intermediate | 125       | 2.34/sec  |
| Pro          | 180       | 3.75/sec  |

### Critical Edge Cases

- **Book checksum:** CRC32 over top 10 price levels. Must parse prices/quantities with `Decimal` to avoid float precision drift. Algorithm: for each of top 10 asks (ascending) then top 10 bids (descending), strip decimal point and leading zeros from price and qty, concatenate all into one string, CRC32.
- **Sequence numbers:** `executions` and `balances` include `sequence` integer. Gaps mean missed messages — must reconnect and re-snapshot.
- **Amend order vs edit order:** `amend_order` modifies an order in-place (same `order_id`, preserves queue priority). `edit_order` is cancel-and-replace (new `order_id`). `amend_order` is preferred when applicable; `edit_order` covers cases amend cannot (e.g., changing order type). Both return `original_order_id` in the response.
- **Edit order:** Cancel-and-replace semantics. Response includes `original_order_id`. Triggered stop/take-profit and conditional-close orders cannot be edited.
- **Dead man's switch (`cancel_all_orders_after`):** Client sends a timeout (in seconds). Server auto-cancels all orders if the timeout expires without being refreshed. Sending `timeout=0` disables the timer. Response includes `currentTime` and `triggerTime`. The bot should call this periodically (e.g., every 15–30s with a 60s timeout) as a safety net against connectivity loss or crashes.
- **Batch validation:** Entire batch validated before submission. One validation failure rejects the batch. Post-submission, individual failures don't reject remaining orders.
- **Instrument status:** Pair status transitions are pushed as updates. Client should honor status to avoid order rejections.

---

## Phased Build

Each phase produces a working, tested, committed increment. Later phases build on earlier ones but are planned in detail only when the prior phase is complete.

### Phase 1 — Message Models

**Goal:** Typed `attrs` classes for all inbound and outbound messages. Pure data layer, no I/O.

**Scope:**

- Request/response envelopes (subscribe, unsubscribe, ping/pong, error)
- Channel data models: ticker, book, trade, ohlc, instrument, level3, executions, balances, heartbeat, status
- Trading method request/response models: add_order, amend_order, edit_order, cancel_order, cancel_all, cancel_all_orders_after, batch_add, batch_cancel
- `to_dict()` / `from_dict()` serialization on all models
- Message routing: parse raw JSON → typed model (dispatcher/factory)

**Not in scope:** WebSocket transport, connection management, subscription state.

**Testing:** Unit tests for serialization round-trips using real Kraken message examples from docs.

---

### Phase 2 — Connection Manager

**Goal:** Async WebSocket connection with heartbeat tracking, ping/pong, auto-reconnect, and system status awareness.

**Scope:**

- `KrakenWSClient` class: connect, disconnect, send, receive
- Heartbeat monitoring (detect server silence > threshold)
- Client-initiated ping at configurable interval
- Automatic reconnection with exponential backoff (respecting 150/10min connection limit)
- System status tracking from `status` channel messages
- Connection state machine: `disconnected` → `connecting` → `connected` → `reconnecting` → `disconnected`

**Not in scope:** Subscription management, authentication, channel-specific logic.

**Testing:** Mock WebSocket transport. Test state transitions, reconnect backoff timing, heartbeat timeout detection.

---

### Phase 3 — Subscription Lifecycle

**Goal:** Subscribe/unsubscribe with snapshot/update dispatch and req_id correlation.

**Scope:**

- Subscription tracking: which channels/symbols are active
- `req_id` generation and response correlation (futures/callbacks)
- Snapshot vs update message routing
- Re-subscribe on reconnect (rebuild subscriptions from tracked state)
- Error handling for failed subscriptions

**Not in scope:** Authentication, book state management, trading methods.

**Testing:** Mock connection. Test subscribe → ack → snapshot → update flow, re-subscribe after reconnect, error responses.

---

### Phase 4 — Auth Integration

**Goal:** Authenticated connections for private channels and trading methods.

**Scope:**

- Token acquisition via existing REST `get_websockets_token` endpoint
- Token injection into subscription and trading params
- Token refresh before expiry (15min lifetime)
- Private channel subscription (executions, balances)
- Sequence number tracking and gap detection for private channels

**Not in scope:** Trading method execution, book management.

**Testing:** Mock REST token endpoint + mock WS connection. Test token refresh lifecycle, sequence gap detection.

---

### Phase 5 — Book Management

**Goal:** Local order book state with checksum validation.

**Scope:**

- `OrderBook` class maintaining sorted bid/ask levels
- Apply snapshot (full replace) and update (incremental) messages
- Truncate to subscribed depth after updates
- CRC32 checksum validation against top 10 levels
- `Decimal` parsing for price/quantity precision
- Checksum mismatch → signal to caller (re-subscribe or raise)

**Not in scope:** Level 3 book (can be added later as a subclass/variant).

**Testing:** Unit tests with known book states and checksums from Kraken docs. Test incremental updates, level removal (qty=0), depth truncation, checksum validation pass/fail.

---

### Phase 6 — Trading Methods

**Goal:** Place, edit, and cancel orders over WebSocket. Includes dead man's switch for safety.

**Scope:**

- `add_order`, `amend_order`, `edit_order`, `cancel_order`, `cancel_all` methods on the client
- `cancel_all_orders_after` (dead man's switch) — set/refresh/disable auto-cancel timer
- `batch_add`, `batch_cancel` methods
- Models for `amend_order` (params + result) and `cancel_all_orders_after` (params + result) — these were not modeled in Phase 1
- `req_id` correlation for trading responses (async: return awaitable that resolves on server response)
- Error handling for order rejections
- Integration with existing `RateLimiter` (caller-controlled, same pattern as REST)

**Methods (8 total):**

| Method                    |   Model Status    | Notes                                           |
| ------------------------- | :---------------: | ----------------------------------------------- |
| `add_order`               |      Phase 1      | —                                               |
| `amend_order`             | **Phase 6 (new)** | In-place modification, preserves queue priority |
| `edit_order`              |      Phase 1      | Cancel-and-replace                              |
| `cancel_order`            |      Phase 1      | —                                               |
| `cancel_all`              |      Phase 1      | —                                               |
| `cancel_all_orders_after` | **Phase 6 (new)** | Dead man's switch, safety-critical              |
| `batch_add`               |      Phase 1      | —                                               |
| `batch_cancel`            |      Phase 1      | —                                               |

**Not in scope:** Order state management, position tracking (caller responsibility).

**Testing:** Mock WS connection. Test request serialization, response correlation, error handling, batch validation rejection, dead man's switch set/refresh/disable lifecycle.

---

### Phase 7 — Consumer API and Documentation

**Goal:** Clean public API, usage documentation, README update.

**Scope:**

- Finalize public API surface: what's exported from `__init__.py`
- Async iterator interface for channel data streams
- Callback registration as alternative to iterators (if warranted by Phase 1–6 experience)
- README usage examples: public subscription, authenticated subscription, trading, book management
- Docstrings on all public classes and methods

**Testing:** Integration-style tests exercising the full stack with mock transport.

---

## Dependencies and Decisions

### Decisions (resolved)

| Decision              | Resolution                      | Notes                                                                                              |
| --------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------- |
| WebSocket library     | `websockets`                    | Async-native, familiar to the team, no strong reason to choose otherwise.                          |
| Module structure      | `ws/` package                   | Package needed given ~30 model classes + connection + subscription + book + trading modules.       |
| Level 3 support       | Defer, design for extensibility | Level 3 is niche (requires special access). Phase 5 book design must allow L3 as a later addition. |
| Phase 5 vs 6 ordering | Book first, then trading        | Market data streaming needed before order execution for the trading bot.                           |

### Cross-phase dependencies

```
Phase 1 (models) ← Phase 2 (connection) ← Phase 3 (subscriptions)
                                          ← Phase 4 (auth)
Phase 1 + Phase 3 ← Phase 5 (book)
Phase 1 + Phase 3 + Phase 4 ← Phase 6 (trading)
Phase 1–6 ← Phase 7 (consumer API + docs)
```

Phases 5 and 6 are independent of each other and can be built in either order. Priority should be based on which the trading bot needs first.

---

## Out of Scope (Initial Build)

- Sync WebSocket API (async only)
- `level3` channel (design for extensibility, build later — requires special Kraken access)
- Automatic order management / position tracking
- Multi-connection load balancing
- FIX protocol support
- Colocation endpoint support

---

## Verification Strategy

Each phase includes:

1. Unit tests with mock transport (no network)
2. Pre-commit checks (ruff, black, mypy)
3. All prior tests still pass
4. Commit with descriptive message

After Phase 7:

- Manual smoke test against Kraken beta WebSocket (`wss://beta-ws.kraken.com/v2`)
- Update `docs/CODE_AUDIT.md` to mark V2-01 as resolved
