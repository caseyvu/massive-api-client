# massive-api-client

`massive-api-client` is an async wrapper around parts of the official `massive` Python client.

It focuses on two things:

- async access to selected Massive.com REST APIs
- automatic sleeping and retrying when a rate limit is hit, which is especially helpful on the free tier

This package is still a work in progress, so it currently supports only a subset of endpoints. It reuses response models from `massive.rest.models`, which makes it easy to work alongside the official client.

## Features

- Async client built on `httpx.AsyncClient`
- Reuses models from the official `massive` package
- Async pagination support through `async for`
- Built-in retry/sleep behavior for HTTP `429 Too Many Requests`
- Small and focused API surface

## Supported APIs

### Reference

- `list_tickers(...)`
- `get_ticker_details(ticker, ...)`
- `get_ticker_events(ticker, ...)`
- `list_ticker_news(...)`
- `get_ticker_types(...)`
- `get_related_companies(ticker)`

### Aggregates

- `list_aggs(ticker, multiplier, timespan, from_, to, ...)`
- `get_grouped_daily_aggs(date, ...)`

### Indicators

- `get_sma(ticker, ...)`
- `get_ema(ticker, ...)`
- `get_rsi(ticker, ...)`
- `get_macd(ticker, ...)`

## Installation

Install from PyPI:

```bash
pip install massive-api-client
```

## Quick Start

```python
import asyncio

from massive_api_client import MassiveAPIClient
from massive_api_client.config import MassiveClientConfig


async def main() -> None:
    client = MassiveAPIClient(
        MassiveClientConfig(
            massive_api_key="YOUR_MASSIVE_API_KEY",
        )
    )

    try:
        details = await client.get_ticker_details("AAPL")
        print(details.name)

        sma = await client.get_sma("AAPL", timespan="day", window=10, limit=5)
        print(sma.values[0].value)

        tickers = [
            ticker
            async for ticker in client.list_tickers(search="apple", limit=5, max_num_pages=1)
        ]
        print([ticker.ticker for ticker in tickers])
    finally:
        await client.close()


asyncio.run(main())
```

## Pagination

The following methods return async iterators:

- `list_tickers(...)`
- `list_ticker_news(...)`
- `list_aggs(...)`

Example:

```python
bars = [
    bar
    async for bar in client.list_aggs(
        ticker="AAPL",
        multiplier=1,
        timespan="day",
        from_="2024-01-01",
        to="2024-01-31",
        max_num_pages=1,
    )
]
```

`max_num_pages` is available as a defensive guard for paginated endpoints. It is default to 10000 pages.

## Rate Limit Handling

When Massive returns HTTP `429`, the client will:

1. sleep for `rate_limit_sleep_secs`
2. retry the same request
3. repeat until `rate_limit_max_retries` is reached

If the request is still rate-limited after all retries, a `RateLimitException` is raised.

Default settings:

- `rate_limit_sleep_secs=60.0`
- `rate_limit_max_retries=3`

## Configuration

Use `MassiveClientConfig` to configure the client:

```python
from massive_api_client.config import MassiveClientConfig


config = MassiveClientConfig(
    massive_api_key="YOUR_MASSIVE_API_KEY",
    api_base_url="https://api.massive.com",
    timeout_secs=30.0,
    rate_limit_sleep_secs=60.0,
    rate_limit_max_retries=3,
)
```

Fields:

- `massive_api_key`: required Massive API key
- `api_base_url`: defaults to `https://api.massive.com`
- `timeout_secs`: request timeout in seconds, default to 30 seconds
- `rate_limit_sleep_secs`: how long to wait before retrying after HTTP `429`, default to 1 minute
- `rate_limit_max_retries`: maximum retry attempts after HTTP `429`, default to 3 - meaning together with the initial call, it will call the API upto 4 times

## Return Types

Responses are deserialized into models from the official `massive` package, for example:

- `Ticker`
- `TickerDetails`
- `TickerNews`
- `TickerTypes`
- `Agg`
- `GroupedDailyAgg`
- `SMAIndicatorResults`
- `EMAIndicatorResults`
- `RSIIndicatorResults`
- `MACDIndicatorResults`

This means you can keep using the official model types while switching to an async workflow.

## Errors

- `RateLimitException`: raised when rate-limit retries are exhausted
- `BadResponseException`: raised when the API response is missing an expected field
- `httpx` exceptions: non-rate-limit HTTP failures are surfaced by `httpx`

## Notes

- This project is intentionally small (focusing on author's personal requirements) and currently covers only part of the Massive API.
- The client is not an async context manager right now, so close it explicitly with `await client.close()`.

## Development

```bash
pip install -e . pytest
pytest
```

## License

MIT
