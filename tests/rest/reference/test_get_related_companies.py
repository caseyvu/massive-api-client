import httpx
import pytest
from http import HTTPStatus
from massive.rest.models import RelatedCompany

from massive_api_client.config import MassiveClientConfig
from massive_api_client.rest import MassiveAPIClient


TEST_API_KEY = ""
TEST_BASE_URL = "https://test.testdomain.com"
TEST_TICKER = "AAPL"

EXPECTED_URI = f"/v1/related-companies/{TEST_TICKER}"
RESPONSE = {
    "request_id": "31d59dda-80e5-4721-8496-d0d32a654afe",
    "results": [
        {
        "ticker": "MSFT"
        },
        {
        "ticker": "GOOGL"
        },
        {
        "ticker": "AMZN"
        },
        {
        "ticker": "FB"
        },
        {
        "ticker": "TSLA"
        },
        {
        "ticker": "NVDA"
        },
        {
        "ticker": "INTC"
        },
        {
        "ticker": "ADBE"
        },
        {
        "ticker": "NFLX"
        },
        {
        "ticker": "PYPL"
        }
    ],
    "status": "OK",
    "stock_symbol": TEST_TICKER
}

EXPECTED_ITEMS = [
    RelatedCompany(ticker="MSFT"),
    RelatedCompany(ticker="GOOGL"),
    RelatedCompany(ticker="AMZN"),
    RelatedCompany(ticker="FB"),
    RelatedCompany(ticker="TSLA"),
    RelatedCompany(ticker="NVDA"),
    RelatedCompany(ticker="INTC"),
    RelatedCompany(ticker="ADBE"),
    RelatedCompany(ticker="NFLX"),
    RelatedCompany(ticker="PYPL"),
]

config = MassiveClientConfig(
    massive_api_key=TEST_API_KEY,
    api_base_url=TEST_BASE_URL,
)


@pytest.mark.asyncio
async def test_get_related_companies():
    def transport_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == EXPECTED_URI:
            return httpx.Response(HTTPStatus.OK, json=RESPONSE)
        return httpx.Response(404, json={"error": "not found"})

    massiveAPIClient = MassiveAPIClient(config)
    massiveAPIClient._client = httpx.AsyncClient(transport=httpx.MockTransport(handler=transport_handler))

    result = await massiveAPIClient.get_related_companies(TEST_TICKER)
    assert result == EXPECTED_ITEMS