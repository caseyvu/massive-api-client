import httpx
import pytest
from http import HTTPStatus
from massive.rest.models import MACDIndicatorResults, MACDIndicatorValue, IndicatorUnderlying, Order, SeriesType

from massive_api_client.config import MassiveClientConfig
from massive_api_client.rest import MassiveAPIClient


TEST_API_KEY = ""
TEST_BASE_URL = "https://test.testdomain.com"
TEST_TICKER = "AAPL"

EXPECTED_URI = f"/v1/indicators/macd/{TEST_TICKER}"
EXPECTED_PARAMS = {
    "timestamp": "2024-01-05",
    "timestamp.gte": "2024-01-01",
    "timespan": "day",
    "short_window": "12",
    "long_window": "26",
    "signal_window": "9",
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
                "value": 1.28,
                "signal": 1.11,
                "histogram": 0.17,
            },
            {
                "timestamp": 1704499200000,
                "value": 1.43,
                "signal": 1.19,
                "histogram": 0.24,
            },
        ],
        "underlying": {
            "url": "https://api.massive.com/v2/aggs/ticker/AAPL/range/1/day/2024-01-01/2024-01-10",
            "aggregates": [],
        },
    },
    "status": "OK",
    "request_id": "b2cbd6714f3740f98737c2b7f2b71788",
}

EXPECTED_ITEM = MACDIndicatorResults(
    values=[
        MACDIndicatorValue(timestamp=1704412800000, value=1.28, signal=1.11, histogram=0.17),
        MACDIndicatorValue(timestamp=1704499200000, value=1.43, signal=1.19, histogram=0.24),
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
async def test_get_macd():
    def transport_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == EXPECTED_URI:
            assert set(request.url.params.keys()) == set(EXPECTED_PARAMS.keys())
            for key, value in EXPECTED_PARAMS.items():
                assert request.url.params.get(key) == value
            return httpx.Response(HTTPStatus.OK, json=RESPONSE)
        return httpx.Response(404, json={"error": "not found"})

    massiveAPIClient = MassiveAPIClient(config)
    massiveAPIClient._client = httpx.AsyncClient(transport=httpx.MockTransport(handler=transport_handler))

    result = await massiveAPIClient.get_macd(
        TEST_TICKER,
        timestamp="2024-01-05",
        timestamp_gte="2024-01-01",
        timespan="day",
        short_window=12,
        long_window=26,
        signal_window=9,
        adjusted=False,
        expand_underlying=True,
        order=Order.DESC,
        limit=2,
        series_type=SeriesType.CLOSE,
    )
    assert result == EXPECTED_ITEM
