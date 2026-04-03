import httpx
import pytest
from http import HTTPStatus
from massive.rest.models import GroupedDailyAgg

from massive_api_client.config import MassiveClientConfig
from massive_api_client.rest import MassiveAPIClient


TEST_API_KEY = ""
TEST_BASE_URL = "https://test.testdomain.com"
TEST_DATE = "2005-04-04"


EXPECTED_URI = f"/v2/aggs/grouped/locale/us/market/stocks/{TEST_DATE}"
RESPONSE = {
    "queryCount": 1,
    "resultsCount": 1,
    "adjusted": True,
    "results": [
        {
            "T": "GIK",
            "v": 895345,
            "vw": 9.9979,
            "o": 9.99,
            "c": 10.02,
            "h": 10.02,
            "l": 9.9,
            "t": 1602705600000,
            "n": 96
        }
    ],
    "status": "OK",
    "request_id": "eae3ded2d6d43f978125b7a8a609fad9",
    "count": 1
}

EXPECTED_ITEM = [
    GroupedDailyAgg(
        ticker="GIK",
        open=9.99,
        high=10.02,
        low=9.9,
        close=10.02,
        volume=895345,
        vwap=9.9979,
        timestamp=1602705600000,
        transactions=96,
    )
]

config = MassiveClientConfig(
    massive_api_key=TEST_API_KEY,
    api_base_url=TEST_BASE_URL,
)


@pytest.mark.asyncio
async def test_get_ticker_events():
    def transport_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == EXPECTED_URI:
            return httpx.Response(HTTPStatus.OK, json=RESPONSE)
        return httpx.Response(404, json={"error": "not found"})

    massiveAPIClient = MassiveAPIClient(config)
    massiveAPIClient._client = httpx.AsyncClient(transport=httpx.MockTransport(handler=transport_handler))

    result = await massiveAPIClient.get_grouped_daily_aggs(TEST_DATE)
    assert result == EXPECTED_ITEM
