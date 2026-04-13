import httpx
import pytest
from http import HTTPStatus
from massive.rest.models import RSIIndicatorResults, IndicatorUnderlying, IndicatorValue, Order, SeriesType

from massive_api_client.config import MassiveClientConfig
from massive_api_client.rest import MassiveAPIClient


TEST_API_KEY = ""
TEST_BASE_URL = "https://test.testdomain.com"
TEST_TICKER = "AAPL"

EXPECTED_URI = f"/v1/indicators/rsi/{TEST_TICKER}"
EXPECTED_PARAMS = {
    "timestamp": "2024-01-05",
    "timestamp.lte": "2024-01-10",
    "timespan": "day",
    "window": "14",
    "adjusted": "false",
    "expand_underlying": "true",
    "order": "desc",
    "limit": "2",
    "series_type": "close",
}
RESPONSE = {
    "results": {
        "values": [
            {
                "timestamp": 1704412800000,
                "value": 56.41,
            },
            {
                "timestamp": 1704499200000,
                "value": 59.87,
            },
        ],
        "underlying": {
            "url": "https://api.massive.com/v2/aggs/ticker/AAPL/range/1/day/2024-01-01/2024-01-10",
            "aggregates": [],
        },
    },
    "status": "OK",
    "request_id": "500fafdc69ce44f0a1ac98c7b4c6dcca",
}

EXPECTED_ITEM = RSIIndicatorResults(
    values=[
        IndicatorValue(timestamp=1704412800000, value=56.41),
        IndicatorValue(timestamp=1704499200000, value=59.87),
    ],
    underlying=IndicatorUnderlying(
        url="https://api.massive.com/v2/aggs/ticker/AAPL/range/1/day/2024-01-01/2024-01-10",
        aggregates=[],
    ),
)

config = MassiveClientConfig(
    massive_api_key=TEST_API_KEY,
    api_base_url=TEST_BASE_URL,
)


@pytest.mark.asyncio
async def test_get_rsi():
    def transport_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == EXPECTED_URI:
            assert set(request.url.params.keys()) == set(EXPECTED_PARAMS.keys())
            for key, value in EXPECTED_PARAMS.items():
                assert request.url.params.get(key) == value
            return httpx.Response(HTTPStatus.OK, json=RESPONSE)
        return httpx.Response(404, json={"error": "not found"})

    massiveAPIClient = MassiveAPIClient(config)
    massiveAPIClient._client = httpx.AsyncClient(transport=httpx.MockTransport(handler=transport_handler))

    result = await massiveAPIClient.get_rsi(
        TEST_TICKER,
        timestamp="2024-01-05",
        timestamp_lte="2024-01-10",
        timespan="day",
        window=14,
        adjusted=False,
        expand_underlying=True,
        order=Order.DESC,
        limit=2,
        series_type=SeriesType.CLOSE,
    )
    assert result == EXPECTED_ITEM
