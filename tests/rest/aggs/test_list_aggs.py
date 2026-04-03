import httpx
import pytest
from http import HTTPStatus
from datetime import datetime
from massive.rest.models import Agg

from massive_api_client.config import MassiveClientConfig
from massive_api_client.rest import MassiveAPIClient


TEST_API_KEY = ""
TEST_BASE_URL = "https://test.testdomain.com"
TEST_PAGE2_CURSOR = "page2cursor"
TEST_TICKER = "AAPL"
TEST_MULTIPLIER = 1
TEST_TIMESPAN = "day"
TEST_DATE_FROM = "2005-04-02"
TEST_DATE_TO = "2005-04-04"
TEST_TS_FROM = 1775001600 # 2026-04-01
TEST_TS_TO = 1775174400 # 2026-04-03

EXPECTED_URI_1 = f"/v2/aggs/ticker/{TEST_TICKER}/range/{TEST_MULTIPLIER}/{TEST_TIMESPAN}/{TEST_DATE_FROM}/{TEST_DATE_TO}"
EXPECTED_URI_2 = f"/v2/aggs/ticker/{TEST_TICKER}/range/{TEST_MULTIPLIER}/{TEST_TIMESPAN}/{TEST_TS_FROM * 1000}/{TEST_TS_TO * 1000}"
PAGE1_RESP = {
    "ticker": "AAPL",
    "queryCount": 2,
    "resultsCount": 2,
    "adjusted": True,
    "results": [
        {
            "v": 642646396.0,
            "vw": 1.469,
            "o": 1.5032,
            "c": 1.4604,
            "h": 1.5064,
            "l": 1.4489,
            "t": 1112331600000,
            "n": 82132
        },
        {
            "v": 578172308.0,
            "vw": 1.4589,
            "o": 1.4639,
            "c": 1.4675,
            "h": 1.4754,
            "l": 1.4343,
            "t": 1112587200000,
            "n": 65543
        }
    ],
    "status": "OK",
    "request_id": "12afda77aab3b1936c5fb6ef4241ae42",
    "count": 2
}

EXPECTED_ITEMS = [
    Agg(
        open=1.5032,
        high=1.5064,
        low=1.4489,
        close=1.4604,
        volume=642646396.0,
        vwap=1.469,
        timestamp=1112331600000,
        transactions=82132,
    ),
    Agg(
        open=1.4639,
        high=1.4754,
        low=1.4343,
        close=1.4675,
        volume=578172308.0,
        vwap=1.4589,
        timestamp=1112587200000,
        transactions=65543,
    ),
]


config = MassiveClientConfig(
    massive_api_key=TEST_API_KEY,
    api_base_url=TEST_BASE_URL,
)


@pytest.mark.asyncio
async def test_list_aggs_with_string_ts():
    def transport_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == EXPECTED_URI_1:
            cursor_val = request.url.params.get("cursor")
            if cursor_val is None:
                return httpx.Response(HTTPStatus.OK, json=PAGE1_RESP)
        return httpx.Response(404, json={"error": "not found"})

    massiveAPIClient = MassiveAPIClient(config)
    massiveAPIClient._client = httpx.AsyncClient(transport=httpx.MockTransport(handler=transport_handler))

    result = [item async for item in massiveAPIClient.list_aggs(TEST_TICKER, TEST_MULTIPLIER, TEST_TIMESPAN, TEST_DATE_FROM, TEST_DATE_TO)]
    assert len(result) == 2
    for idx, item in enumerate(result):
        assert item == EXPECTED_ITEMS[idx]


@pytest.mark.asyncio
async def test_list_aggs_with_datetime_ts():
    def transport_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == EXPECTED_URI_2:
            cursor_val = request.url.params.get("cursor")
            if cursor_val is None:
                return httpx.Response(HTTPStatus.OK, json=PAGE1_RESP)
        return httpx.Response(404, json={"error": "not found"})

    massiveAPIClient = MassiveAPIClient(config)
    massiveAPIClient._client = httpx.AsyncClient(transport=httpx.MockTransport(handler=transport_handler))

    result = [item async for item in massiveAPIClient.list_aggs(
        TEST_TICKER, TEST_MULTIPLIER, TEST_TIMESPAN, 
        datetime.fromtimestamp(TEST_TS_FROM), datetime.fromtimestamp(TEST_TS_TO))]
    assert len(result) == 2
    for idx, item in enumerate(result):
        assert item == EXPECTED_ITEMS[idx]
