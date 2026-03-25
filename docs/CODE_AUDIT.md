# Code Audit: kraken-connector

**Date:** 2026-03-24
**Scope:** Full library audit — security, correctness, completeness, v2 readiness
**Codebase version:** 0.0.2 (commit 04d446a, branch `feature`)

---

## Executive Summary

The kraken-connector library wraps Kraken's REST API v1.1.0 via code generated from `openapi.json` using `openapi-python-client`. It provides sync and async HTTP clients with HMAC authentication, ~170 schema classes, and a stub WebSocket client.

The library has a solid generated foundation. All **P0** (6 critical/high-severity bugs and security issues) and **P1** (8 architectural/completeness issues) findings have been **resolved**. The non-functional WebSocket client was deleted; it will be rebuilt for v2. The test suite now includes 18 passing tests covering security, HTTP clients, exceptions, and endpoint error wiring. Kraken has released a WebSocket API v2 (no OpenAPI spec available); the REST API has not been versioned separately.

This document is organized so each finding can be addressed as an independent, incremental commit.

---

## How to Use This Document

Findings are grouped into four priority tiers:

- **P0** — Fix before any new work. These are crashes, security flaws, or broken infrastructure.
- **P1** — Fix before starting v2 work. These are architectural issues that will compound if carried forward.
- **P2** — Fix during the v2 migration. These are best addressed as part of the larger rewrite.
- **P3** — Improve when convenient. Low-severity or cosmetic issues.

Each finding has an **ID** (e.g., SEC-01) for cross-referencing in commits and PRs. Tackle them sequentially within each priority tier.

---

## P0 — Fix Before Any New Work

> **Status: All P0 findings resolved (2026-03-24)**

### SEC-01 | Dead signing function references non-existent attribute — RESOLVED

- **Severity:** Critical
- **File:** `kraken_connector/security.py`
- **Resolution:** Deleted the dead `_sign(self, data, urlpath)` function (lines 32-50). It was never called and referenced a non-existent `self.secret` attribute. The module now contains only `get_nonce()` and `sign_message()`.

---

### SEC-02 | Undefined `self.prefix` crashes async authenticated requests — RESOLVED

- **Severity:** High
- **File:** `kraken_connector/http.py`
- **Resolution:** Removed the `self.prefix` logic from `get_async_httpx_client()`. The async path now sets `self._headers[self.auth_header_name] = self._api_key`, matching the sync path exactly. Kraken uses a bare `API-Key` header with no prefix.

---

### SEC-03 | Sync and async auth paths are inconsistent — RESOLVED

- **Severity:** High
- **File:** `kraken_connector/http.py`
- **Resolution:** Fixed as part of SEC-02. Both `get_httpx_client()` and `get_async_httpx_client()` now use identical auth header logic.

---

### BUG-01 | WebSocket `process_events()` calls non-existent method — RESOLVED

- **Severity:** Critical
- **File:** `kraken_connector/ws.py`
- **Resolution:** Changed `await self.connect()` to `await self.connect_public()` in `process_events()`. The WebSocket client still needs a full rebuild for v2 (see INC-01).

---

### BUG-02 | `Ordertype` exported but never defined — RESOLVED

- **Severity:** High
- **File:** `kraken_connector/schemas/__init__.py`
- **Resolution:** Removed `"Ordertype"` from `__all__`. No class by this name existed.

---

### BUG-04 | Test suite is completely broken — RESOLVED

- **Severity:** Medium
- **File:** `tests/`
- **Resolution:** Deleted `test_foo.py` (which imported non-existent `kraken_connector.foo`). Created:
  - `tests/test_smoke.py` — 2 tests: package import, client instantiation (HTTPClient and HTTPAuthenticatedClient)
  - `tests/test_security.py` — 4 tests: nonce type, nonce monotonicity, signature determinism with known test vector, return type
  - All 6 tests passing.

---

## P1 — Fix Before V2 Work

> **Status: All P1 findings resolved (2026-03-24)**

### SEC-04 | Nonce generation allows collisions — RESOLVED

- **Severity:** Medium
- **File:** `kraken_connector/security.py`
- **Resolution:** Changed nonce precision from milliseconds (`time.time() * 1000`) to microseconds (`time.time() * 1_000_000`). Added test verifying nonce has at least 16 digits.

---

### SEC-05 | Authenticated client follows redirects by default — RESOLVED

- **Severity:** Medium
- **File:** `kraken_connector/http.py`
- **Resolution:** Changed `HTTPAuthenticatedClient._follow_redirects` default from `True` to `False`, matching `HTTPClient`. Prevents credential leakage via redirects.

---

### AP-01 | `with_headers()` / `with_cookies()` mutate AND copy — RESOLVED

- **Severity:** High
- **File:** `kraken_connector/http.py`
- **Resolution:** Removed all `_client` / `_async_client` mutation blocks from `with_headers()`, `with_cookies()`, and `with_timeout()`. Methods now return a pure `evolve()` copy only. The copy lazily creates fresh httpx clients on first use. Added regression tests verifying copy isolation.

---

### AP-04 | HTTPAuthenticatedClient duplicates HTTPClient — RESOLVED

- **Severity:** Medium
- **File:** `kraken_connector/http.py`
- **Resolution:** `HTTPAuthenticatedClient` now inherits from `HTTPClient`. Removed all duplicated fields and methods. Only `_api_key`, `_api_secret`, `_follow_redirects` (override), auth constants, and overridden `get_httpx_client()` / `get_async_httpx_client()` remain. Added regression tests for auth header injection in both sync and async paths.

---

### INC-01 | WebSocket client is non-functional — RESOLVED

- **Severity:** Critical
- **File:** `kraken_connector/ws.py` (deleted)
- **Resolution:** Deleted the non-functional WebSocket module entirely. Removed `websockets` from dependencies in `pyproject.toml`. Will be rebuilt from scratch for v2 (see V2-01).

---

### INC-02 | API submodule `__init__.py` files are all empty — RESOLVED

- **Severity:** High
- **Files:** All 8 `__init__.py` files under `kraken_connector/api/`
- **Resolution:** Populated all submodule `__init__.py` files with imports of their endpoint modules. Top-level `api/__init__.py` imports all subpackages. Users can now write `from kraken_connector.api.trading import add_order`.

---

### INC-03 | Package `__init__.py` exports are minimal — RESOLVED

- **Severity:** High
- **File:** `kraken_connector/__init__.py`
- **Resolution:** Added re-exports for `InvalidResponseModel`, `KrakenAPIError`, `UnexpectedStatus`, `File`, `FileJsonType`, and `Response`. All included in `__all__`.

---

### INC-04 | Exception hierarchy is too sparse — RESOLVED

- **Severity:** Medium
- **File:** `kraken_connector/exceptions.py` + 48 endpoint files
- **Resolution:** Added `KrakenAPIError` exception class with `errors` attribute. Wired error checking into all 48 endpoint `_parse_response()` functions — after parsing the response schema, checks the `error` field and raises `KrakenAPIError` if non-empty. Handles all error field type variants (`List[str]`, `List[List[str]]`, `str`). Added regression test verifying error wiring with a mock Kraken error response.

---

## P2 — Fix During V2 Migration

> **Status: AP-03, V2-02, V2-04 resolved (2026-03-24). V2-01, V2-03, CQ-01 deferred.**

### V2-01 | WebSocket v2 requires a ground-up rebuild

- **Severity:** High
- **V2 relevance:** Direct

Kraken's WebSocket API v2 is available at `wss://ws.kraken.com/v2` (public) and `wss://ws-auth.kraken.com/v2` (private). It is event-driven with JSON-RPC-style messages and supports channels: `ticker`, `book` (L2/L3), `trade`, `ohlc`, `instrument`, `executions`.

The current `ws.py` targets v1 and is too incomplete to extend. Build a new WebSocket v2 client with:

- JSON message serialization/deserialization
- Subscription lifecycle management (subscribe, unsubscribe, snapshot + updates)
- Authentication via REST-obtained WebSocket token
- Automatic reconnection with exponential backoff
- Typed message models for each channel

**Reference:** https://docs.kraken.com/websockets-v2/

---

### V2-02 | REST URL prefix `/0/` is hardcoded in every endpoint — RESOLVED

- **Severity:** Medium
- **Files:** Every file in `kraken_connector/api/*/`
- **Resolution:** Extracted `API_VERSION_PREFIX = "/0"` to `kraken_connector/constants/api.py`. All 48 endpoint files now use the constant via f-string. Added regression tests verifying all endpoint URLs use the prefix.

---

### V2-03 | Schema names are opaque

- **Severity:** Medium
- **Files:** `kraken_connector/schemas/`

Generated names like `Add2`, `Closed2`, `Balance2`, `Info3`, `Info5` give no indication of their purpose. Examples:

- `Add2` = AddOrder response
- `Closed2` = GetClosedOrders response
- `Info5` = GetWithdrawalInformation response

**Recommendation:** During v2 migration, rename schemas to descriptive names (e.g., `AddOrderResponse`, `ClosedOrdersResponse`). If generated code is kept, configure `openapi-python-client` with a custom name mapping.

---

### V2-04 | No documented process for regenerating from OpenAPI spec — RESOLVED

- **Severity:** Low
- **File:** `openapi.json` (gitignored)
- **Resolution:** Added `make generate` target to the Makefile. Documented the full regeneration workflow and all manual post-generation edits in CONTRIBUTING.md.

---

### AP-03 | Dead `pass` statements in all endpoint functions — RESOLVED

- **Severity:** Medium
- **Files:** All `kraken_connector/api/*/*.py`
- **Resolution:** Removed unreachable `pass` statements from all 47 `_get_kwargs()` functions. Added regression tests that dynamically discover all endpoint modules and verify `_get_kwargs` returns a dict with `method` and `url` keys.

---

### CQ-01 | Schema file names are excessively long

- **Severity:** Medium
- **Files:** `kraken_connector/schemas/`

Some file names exceed 100 characters:

```
list_allocations_response_200_result_items_item_amount_allocated_bonding_allocations_item.py
```

This causes problems with some filesystems, IDE tabs, and readability.

**Recommendation:** Address during v2 schema redesign. If regenerating, configure shorter name prefixes.

---

## P3 — Improve When Convenient

### SEC-06 | API secret has no `__repr__` masking

- **Severity:** Low
- **File:** `kraken_connector/http.py:174-175`

The `_api_secret` field is a plain `Optional[str]`. Attrs-generated `__repr__` will include the full secret in string representations, which could appear in logs or tracebacks.

**Recommendation:** Add `repr=False` to the field definition:

```python
_api_secret: Optional[str] = field(default=None, kw_only=True, repr=False)
```

Also apply to `_api_key`:

```python
_api_key: Optional[str] = field(default=None, kw_only=True, repr=False)
```

---

### AP-02 | `get_httpx_client()` name obscures side effects

- **Severity:** Medium
- **File:** `kraken_connector/http.py:80-93`

The method lazily creates an `httpx.Client` if one doesn't exist. The name `get_httpx_client()` implies a pure getter.

**Recommendation:** Rename to `get_or_create_httpx_client()`. This is a breaking change for existing consumers, so do it when making other breaking changes (e.g., v2 migration).

---

### AP-05 | Custom `Unset` sentinel type

- **Severity:** Low
- **File:** `kraken_connector/types.py:8-13`

The `Unset` type is used across all generated schemas to distinguish "field not present in response" from "field is null." While semantically valid, it adds cognitive load and doesn't integrate well with standard Python typing tools.

**Recommendation:** Low priority. If schemas are regenerated for v2, evaluate whether the distinction between Unset and None is needed. For most Kraken API responses, `Optional[T] = None` is sufficient.

---

### BUG-03 | Content-Type header commented out

- **Severity:** Medium
- **File:** `kraken_connector/http.py:227`

```python
# self._headers[self.content_type_key] = self.content_type_value
```

Kraken private endpoints expect `application/x-www-form-urlencoded`. httpx sets this automatically for `data=` kwargs, so this is likely safe in practice. However, if the signing code and httpx encode the data differently, the signature will mismatch.

**Recommendation:** Verify httpx's default Content-Type matches what `sign_message()` expects. If they align, remove the commented line. If not, uncomment it.

---

### INC-05 | No retry logic, rate limiting, or request logging

- **Severity:** Medium
- **Files:** Library-wide

The library has no mechanism for:

- Retrying failed requests (network errors, 5xx responses)
- Respecting Kraken's rate limits (documented in openapi.json)
- Logging requests/responses for debugging

**Recommendation:** Add optional middleware or hooks:

- Rate limiter using Kraken's documented token bucket algorithm
- Configurable retry with exponential backoff for transient errors
- Structured logging at DEBUG level for request/response pairs

---

### INC-06 | Empty `utils.py` module

- **Severity:** Low
- **File:** `kraken_connector/utils.py`

Contains only a docstring. The `utils/` subdirectory has functional code (`converters.py`, `validators.py`, `errors.py`), but this top-level file is dead.

**Recommendation:** Delete `kraken_connector/utils.py` (the empty module). The `utils/` package serves the same purpose.

---

### CQ-02 | Fragile header mutation pattern in authenticated endpoints

- **Severity:** Low
- **Files:** All private endpoint files (e.g., `api/trading/add_order.py:77-86`)

```python
# Force client initialization
client.get_httpx_client()
# Mutate client headers with HMAC signature
secured_client = client.with_headers(security_header)
# Use the mutated client
response = secured_client.get_httpx_client().request(**kwargs)
```

This depends on `get_httpx_client()` being called first to initialize the internal client, then `with_headers()` mutates that same client (see AP-01). The pattern is order-dependent and fragile.

**Note:** Partially mitigated by AP-01 fix (with_headers is now copy-only). The force-init + with_headers pattern still exists in endpoint code but is no longer dangerous since mutation was removed.

---

### CQ-03 | No `py.typed` marker

- **Severity:** Low
- **File:** Missing `kraken_connector/py.typed`

Downstream consumers using mypy won't pick up the library's type annotations without a `py.typed` marker file (PEP 561).

**Recommendation:** Add an empty `kraken_connector/py.typed` file.

---

## Appendix: Kraken API v2 Status

| API         | v1 Status       | v2 Status                                 | OpenAPI Spec                       |
| ----------- | --------------- | ----------------------------------------- | ---------------------------------- |
| REST (Spot) | Active, v1.1.0  | No separate v2 announced                  | Available (`openapi.json` in repo) |
| WebSocket   | Active (legacy) | **Available** at `wss://ws.kraken.com/v2` | **Not available** publicly         |

**REST API:** Kraken's REST API is versioned at v1.1.0 (path prefix `/0/`). There is no announced v2 for REST. The existing OpenAPI spec covers all current endpoints.

**WebSocket API v2:** Fully available with documentation at https://docs.kraken.com/websockets-v2/. Key differences from v1:

- JSON-RPC-style request/response with `method`, `params`, `result` fields
- New channels: `instrument` (replaces `systemStatus`), `executions` (replaces `openOrders` + `ownTrades`)
- Improved authentication flow
- Better error reporting with structured error objects

**Recommendation for v2 migration path:**

1. ~~Complete P0 fixes on the current codebase~~ **DONE** — ~~then complete P1 fixes~~ **DONE**
2. Build WebSocket v2 client as a new module (`kraken_connector/ws_v2.py` or `kraken_connector/websocket/`)
3. Keep REST API as-is (no v2 exists)
4. Deprecate v1 WebSocket client once v2 is functional

---

## Appendix: Findings Index

| ID     | Severity | Priority | File(s)               | Summary                                                    |
| ------ | -------- | -------- | --------------------- | ---------------------------------------------------------- |
| SEC-01 | Critical | P0       | `security.py`         | ~~Dead `_sign()` function~~ **RESOLVED**                   |
| SEC-02 | High     | P0       | `http.py`             | ~~Undefined `self.prefix` in async path~~ **RESOLVED**     |
| SEC-03 | High     | P0       | `http.py`             | ~~Inconsistent sync/async auth~~ **RESOLVED**              |
| SEC-04 | Medium   | P1       | `security.py`         | ~~Nonce collision risk~~ **RESOLVED**                      |
| SEC-05 | Medium   | P1       | `http.py`             | ~~Auth client follows redirects~~ **RESOLVED**             |
| SEC-06 | Low      | P3       | `http.py`             | No secret masking in repr                                  |
| BUG-01 | Critical | P0       | `ws.py`               | ~~Wrong method name in `process_events()`~~ **RESOLVED**   |
| BUG-02 | High     | P0       | `schemas/__init__.py` | ~~`Ordertype` export missing~~ **RESOLVED**                |
| BUG-03 | Medium   | P3       | `http.py`             | Content-Type commented out                                 |
| BUG-04 | Medium   | P0       | `tests/`              | ~~Broken test suite~~ **RESOLVED**                         |
| AP-01  | High     | P1       | `http.py`             | ~~Mutate-and-copy anti-pattern~~ **RESOLVED**              |
| AP-02  | Medium   | P3       | `http.py`             | Misleading getter name                                     |
| AP-03  | Medium   | P2       | `api/*/*.py`          | ~~Dead `pass` statements~~ **RESOLVED**                    |
| AP-04  | Medium   | P1       | `http.py`             | ~~Duplicated client classes~~ **RESOLVED**                 |
| AP-05  | Low      | P3       | `types.py`            | Custom Unset sentinel                                      |
| INC-01 | Critical | P1       | `ws.py`               | ~~Non-functional WebSocket client~~ **RESOLVED** (deleted) |
| INC-02 | High     | P1       | `api/*/__init__.py`   | ~~Empty submodule exports~~ **RESOLVED**                   |
| INC-03 | High     | P1       | `__init__.py`         | ~~Minimal package exports~~ **RESOLVED**                   |
| INC-04 | Medium   | P1       | `exceptions.py`       | ~~Sparse exception hierarchy~~ **RESOLVED**                |
| INC-05 | Medium   | P3       | Library-wide          | No retry/rate-limit/logging                                |
| INC-06 | Low      | P3       | `utils.py`            | Empty module                                               |
| V2-01  | High     | P2       | `ws.py`               | WS v2 rebuild needed                                       |
| V2-02  | Medium   | P2       | `api/*/*.py`          | ~~Hardcoded URL prefix~~ **RESOLVED**                      |
| V2-03  | Medium   | P2       | `schemas/`            | Opaque schema names                                        |
| V2-04  | Low      | P2       | `openapi.json`        | ~~No regen process~~ **RESOLVED**                          |
| CQ-01  | Medium   | P2       | `schemas/`            | Long file names                                            |
| CQ-02  | Low      | P3       | `api/*/*.py`          | Fragile header mutation                                    |
| CQ-03  | Low      | P3       | Package root          | Missing `py.typed`                                         |
