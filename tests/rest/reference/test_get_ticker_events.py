import httpx
import pytest
from http import HTTPStatus
from massive.rest.models import TickerChange, TickerChangeEvent, TickerChangeResults

from massive_api_client.config import MassiveClientConfig
from massive_api_client.rest import MassiveAPIClient


TEST_API_KEY = ""
TEST_BASE_URL = "https://test.testdomain.com"
TEST_TICKER = "META"

EXPECTED_URI = f"/vX/reference/tickers/{TEST_TICKER}/events"
RESPONSE = {
    "results": {
        "name": "Meta Platforms, Inc. Class A Common Stock",
        "composite_figi": "BBG000MM2P62",
        "cik": "0001326801",
        "events": [
            {
                "ticker_change": {
                    "ticker": "META"
                },
                "type": "ticker_change",
                "date": "2022-06-09"
            },
            {
                "ticker_change": {
                    "ticker": "FB"
                },
                "type": "ticker_change",
                "date": "2012-05-18"
            }
        ]
    },
    "status": "OK",
    "request_id": "4646b1b77e7c624f43923e703425a952"
}

EXPECTED_ITEM = TickerChangeResults(
    name="Meta Platforms, Inc. Class A Common Stock",
    composite_figi="BBG000MM2P62",
    cik="0001326801",
    events=[
        TickerChangeEvent(
            type="ticker_change",
            date="2022-06-09",
            ticker_change=TickerChange(ticker="META")
        ),
        TickerChangeEvent(
            type="ticker_change",
            date="2012-05-18",
            ticker_change=TickerChange(ticker="FB")
        ),
    ]
)

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

    result = await massiveAPIClient.get_ticker_events(TEST_TICKER)
    assert result.name == EXPECTED_ITEM.name
    assert result.composite_figi == EXPECTED_ITEM.composite_figi
    assert result.cik == EXPECTED_ITEM.cik
    assert result.events[0] == EXPECTED_ITEM.events[0]
    assert result.events[1] == EXPECTED_ITEM.events[1]
