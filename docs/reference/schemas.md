# Schemas

Response and request models generated from Kraken's OpenAPI specification. All models are [attrs](https://www.attrs.org/) classes with `to_dict()` and `from_dict()` methods.

## Market Data

::: kraken_connector.schemas.server_time_response
options:
show_source: false

::: kraken_connector.schemas.asset_info
options:
show_source: false

::: kraken_connector.schemas.asset_ticker_info
options:
show_source: false

## Account Data

::: kraken_connector.schemas.account_balance
options:
show_source: false

::: kraken_connector.schemas.extended_balance
options:
show_source: false

## Trading

::: kraken_connector.schemas.add_order_request
options:
show_source: false

::: kraken_connector.schemas.cancel_order_request
options:
show_source: false

## Funding

::: kraken_connector.schemas.deposit_method
options:
show_source: false

## Earn

::: kraken_connector.schemas.earn_strategy
options:
show_source: false

---

For the full list of schemas, see the `kraken_connector.schemas` package source or use:

```python
from kraken_connector import schemas
dir(schemas)
```
