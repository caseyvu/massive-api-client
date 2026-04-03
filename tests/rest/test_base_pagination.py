import httpx
import pytest
from http import HTTPStatus
from massive.rest.models import Ticker
from unittest.mock import call, patch, AsyncMock

from massive_api_client.config import MassiveClientConfig
from massive_api_client.exceptions import RateLimitException
from massive_api_client.rest import MassiveAPIClient


TEST_API_KEY = ""
TEST_BASE_URL = "https://test.testdomain.com"
TEST_TIMEOUT_SECS = 5.0
TEST_RATE_LIMIT_SLEEP_SECS = 10.0
TEST_RATE_LIMIT_MAX_RETRIES = 3
TEST_PAGE2_CURSOR = "page2cursor"

EXPECTED_URI = "/v3/reference/tickers"
PAGE1_RESP = {
    "results": [
        {
            "ticker": "A",
            "name": "Agilent Technologies Inc.",
            "market": "stocks",
            "locale": "us",
            "primary_exchange": "XNYS",
            "type": "CS",
            "active": True,
            "currency_name": "usd",
            "cik": "0001090872",
            "composite_figi": "BBG000C2V3D6",
            "share_class_figi": "BBG001SCTQY4",
            "last_updated_utc": "2022-04-27T00:00:00Z"
        },
        {
            "ticker": "AA",
            "name": "Alcoa Corporation",
            "market": "stocks",
            "locale": "us",
            "primary_exchange": "XNYS",
            "type": "CS",
            "active": True,
            "currency_name": "usd",
            "cik": "0001675149",
            "composite_figi": "BBG00B3T3HD3",
            "share_class_figi": "BBG00B3T3HF1",
            "last_updated_utc": "2022-04-27T00:00:00Z"
        }
    ],
    "status": "OK",
    "request_id": "37089bb3b4ef99a796cdc82ff971e447",
    "count": 2,
    "next_url": f"{TEST_BASE_URL}/v3/reference/tickers?cursor={TEST_PAGE2_CURSOR}"
}

PAGE2_RESP = {
    "results": [
        {
            "ticker": "AAA",
            "name": "AAF First Priority CLO Bond ETF",
            "market": "stocks",
            "locale": "us",
            "primary_exchange": "ARCX",
            "type": "ETF",
            "active": True,
            "currency_name": "usd",
            "composite_figi": "BBG00X5FSP48",
            "share_class_figi": "BBG00X5FSPZ4",
            "last_updated_utc": "2022-04-27T00:00:00Z"
        },
        {
            "ticker": "AAAU",
            "name": "Goldman Sachs Physical Gold ETF Shares",
            "market": "stocks",
            "locale": "us",
            "primary_exchange": "BATS",
            "type": "ETF",
            "active": True,
            "currency_name": "usd",
            "cik": "0001708646",
            "composite_figi": "BBG00LPXX872",
            "share_class_figi": "BBG00LPXX8Z1",
            "last_updated_utc": "2022-04-27T00:00:00Z"
        }
    ],
    "status": "OK",
    "request_id": "40d60d83fa0628503b4d13387b7bde2a",
    "count": 2
}

EMPTY_PAGE_RESP = {
    "results": [],
    "status": "OK",
    "request_id": "40d60d83fa0628503b4d13387b7bde2a",
    "count": 2
}

EXPECTED_ITEMS = [
    Ticker(
        ticker="A",
        name="Agilent Technologies Inc.",
        market="stocks",
        locale="us",
        primary_exchange="XNYS",
        type="CS",
        active=True,
        currency_name="usd",
        cik="0001090872",
        composite_figi="BBG000C2V3D6",
        share_class_figi="BBG001SCTQY4",
        last_updated_utc="2022-04-27T00:00:00Z",
    ),
    Ticker(
        ticker="AA",
        name="Alcoa Corporation",
        market="stocks",
        locale="us",
        primary_exchange="XNYS",
        type="CS",
        active=True,
        currency_name="usd",
        cik="0001675149",
        composite_figi="BBG00B3T3HD3",
        share_class_figi="BBG00B3T3HF1",
        last_updated_utc="2022-04-27T00:00:00Z",
    ),
    Ticker(
        ticker="AAA",
        name="AAF First Priority CLO Bond ETF",
        market="stocks",
        locale="us",
        primary_exchange="ARCX",
        type="ETF",
        active=True,
        currency_name="usd",
        composite_figi="BBG00X5FSP48",
        share_class_figi="BBG00X5FSPZ4",
        last_updated_utc="2022-04-27T00:00:00Z",
    ),
    Ticker(
        ticker="AAAU",
        name="Goldman Sachs Physical Gold ETF Shares",
        market="stocks",
        locale="us",
        primary_exchange="BATS",
        type="ETF",
        active=True,
        currency_name="usd",
        cik="0001708646",
        composite_figi="BBG00LPXX872",
        share_class_figi="BBG00LPXX8Z1",
        last_updated_utc="2022-04-27T00:00:00Z",
    ),
]


config = MassiveClientConfig(
    massive_api_key=TEST_API_KEY, 
    api_base_url=TEST_BASE_URL,
    timeout_secs=TEST_TIMEOUT_SECS,
    rate_limit_sleep_secs=TEST_RATE_LIMIT_SLEEP_SECS,
    rate_limit_max_retries=TEST_RATE_LIMIT_MAX_RETRIES,
)


@pytest.mark.asyncio
async def test_multiple_pages():
    def transport_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == EXPECTED_URI:
            cursor_val = request.url.params.get("cursor")
            if cursor_val is None:
                return httpx.Response(HTTPStatus.OK, json=PAGE1_RESP)
            elif cursor_val == TEST_PAGE2_CURSOR:
                return httpx.Response(HTTPStatus.OK, json=PAGE2_RESP)
        return httpx.Response(404, json={"error": "not found"})

    massiveAPIClient = MassiveAPIClient(config)
    massiveAPIClient._client = httpx.AsyncClient(transport=httpx.MockTransport(handler=transport_handler))

    result = [item async for item in massiveAPIClient.list_tickers()]
    assert len(result) == 4
    for idx, item in enumerate(result):
        assert item == EXPECTED_ITEMS[idx]


@pytest.mark.asyncio
async def test_one_page():
    def transport_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == EXPECTED_URI:
            cursor_val = request.url.params.get("cursor")
            if cursor_val is None:
                return httpx.Response(HTTPStatus.OK, json=PAGE2_RESP)
        return httpx.Response(404, json={"error": "not found"})

    massiveAPIClient = MassiveAPIClient(config)
    massiveAPIClient._client = httpx.AsyncClient(transport=httpx.MockTransport(handler=transport_handler))

    result = [item async for item in massiveAPIClient.list_tickers()]
    assert len(result) == 2
    for idx, item in enumerate(result):
        assert item == EXPECTED_ITEMS[idx + 2]


@pytest.mark.asyncio
async def test_no_result():
    def transport_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == EXPECTED_URI:
            cursor_val = request.url.params.get("cursor")
            if cursor_val is None:
                return httpx.Response(HTTPStatus.OK, json=EMPTY_PAGE_RESP)
        return httpx.Response(404, json={"error": "not found"})

    massiveAPIClient = MassiveAPIClient(config)
    massiveAPIClient._client = httpx.AsyncClient(transport=httpx.MockTransport(handler=transport_handler))

    result = [item async for item in massiveAPIClient.list_tickers()]
    assert len(result) == 0


@pytest.mark.asyncio
async def test_with_max_num_pages():
    def transport_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == EXPECTED_URI:
            cursor_val = request.url.params.get("cursor")
            if cursor_val is None:
                return httpx.Response(HTTPStatus.OK, json=PAGE1_RESP)
            elif cursor_val == TEST_PAGE2_CURSOR:
                return httpx.Response(HTTPStatus.OK, json=PAGE2_RESP)
        return httpx.Response(404, json={"error": "not found"})

    massiveAPIClient = MassiveAPIClient(config)
    massiveAPIClient._client = httpx.AsyncClient(transport=httpx.MockTransport(handler=transport_handler))

    result = [item async for item in massiveAPIClient.list_tickers(max_num_pages=1)]
    assert len(result) == 2
    for idx, item in enumerate(result):
        assert item == EXPECTED_ITEMS[idx]


@pytest.mark.asyncio
async def test_with_rate_limit_self_recovered():
    page2_responses = [
        httpx.Response(HTTPStatus.TOO_MANY_REQUESTS, text="Rate limit reached"),
        httpx.Response(HTTPStatus.OK, json=PAGE2_RESP),
    ]

    def transport_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == EXPECTED_URI:
            cursor_val = request.url.params.get("cursor")
            if cursor_val is None:
                return httpx.Response(HTTPStatus.OK, json=PAGE1_RESP)
            elif cursor_val == TEST_PAGE2_CURSOR:
                return page2_responses.pop(0)
        return httpx.Response(404, json={"error": "not found"})

    massiveAPIClient = MassiveAPIClient(config)
    massiveAPIClient._client = httpx.AsyncClient(transport=httpx.MockTransport(handler=transport_handler))
    
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = [item async for item in massiveAPIClient.list_tickers()]
        assert len(result) == 4
        for idx, item in enumerate(result):
            assert item == EXPECTED_ITEMS[idx]
        mock_sleep.assert_awaited_once_with(TEST_RATE_LIMIT_SLEEP_SECS)


@pytest.mark.asyncio
async def test_with_rate_limit_retries_exceeded():
    def transport_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == EXPECTED_URI:
            cursor_val = request.url.params.get("cursor")
            if cursor_val is None:
                return httpx.Response(HTTPStatus.OK, json=PAGE1_RESP)
            elif cursor_val == TEST_PAGE2_CURSOR:
                return httpx.Response(HTTPStatus.TOO_MANY_REQUESTS, text="Rate limit reached")
        return httpx.Response(404, json={"error": "not found"})

    massiveAPIClient = MassiveAPIClient(config)
    massiveAPIClient._client = httpx.AsyncClient(transport=httpx.MockTransport(handler=transport_handler))
    
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(RateLimitException):
            _result = [item async for item in massiveAPIClient.list_tickers()]
            
        assert mock_sleep.await_count == TEST_RATE_LIMIT_MAX_RETRIES
        mock_sleep.assert_has_awaits(
            [
                call(TEST_RATE_LIMIT_SLEEP_SECS),
                call(TEST_RATE_LIMIT_SLEEP_SECS),
                call(TEST_RATE_LIMIT_SLEEP_SECS),
            ]
        )