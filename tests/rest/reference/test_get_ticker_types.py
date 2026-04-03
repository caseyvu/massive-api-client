import httpx
import pytest
from http import HTTPStatus
from massive.rest.models import TickerTypes

from massive_api_client.config import MassiveClientConfig
from massive_api_client.rest import MassiveAPIClient


TEST_API_KEY = ""
TEST_BASE_URL = "https://test.testdomain.com"

EXPECTED_URI = "/v3/reference/tickers/types"
RESPONSE = {
    "results": [
        {
            "code": "CS",
            "description": "Common Stock",
            "asset_class": "stocks",
            "locale": "us"
        },
        {
            "code": "PFD",
            "description": "Preferred Stock",
            "asset_class": "stocks",
            "locale": "us"
        }
    ],
    "status": "OK",
    "request_id": "efbfc7c2304bba6c2f19a2567f568134",
    "count": 2
}

EXPECTED_ITEMS = [
    TickerTypes(
        asset_class="stocks",
        code="CS",
        description="Common Stock",
        locale="us",
    ),
    TickerTypes(
        asset_class="stocks",
        code="PFD",
        description="Preferred Stock",
        locale="us",
    ),
]

config = MassiveClientConfig(
    massive_api_key=TEST_API_KEY,
    api_base_url=TEST_BASE_URL,
)


@pytest.mark.asyncio
async def test_get_ticker_types():
    def transport_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == EXPECTED_URI:
            return httpx.Response(HTTPStatus.OK, json=RESPONSE)
        return httpx.Response(404, json={"error": "not found"})

    massiveAPIClient = MassiveAPIClient(config)
    massiveAPIClient._client = httpx.AsyncClient(transport=httpx.MockTransport(handler=transport_handler))

    result = await massiveAPIClient.get_ticker_types()
    assert result == EXPECTED_ITEMS