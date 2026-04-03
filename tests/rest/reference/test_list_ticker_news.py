import httpx
import pytest
from http import HTTPStatus
from massive.rest.models import Insight, Publisher, TickerNews

from massive_api_client.config import MassiveClientConfig
from massive_api_client.rest import MassiveAPIClient


TEST_API_KEY = ""
TEST_BASE_URL = "https://test.testdomain.com"
TEST_PAGE2_CURSOR = "page2cursor"

EXPECTED_URI = "/v2/reference/news"
PAGE1_RESP = {
    "count": 1,
    "next_url": f"{TEST_BASE_URL}/v2/reference/news?cursor={TEST_PAGE2_CURSOR}",
    "request_id": "831afdb0b8078549fed053476984947a",
    "results": [
        {
        "amp_url": "https://m.uk.investing.com/news/stock-market-news/markets-are-underestimating-fed-cuts-ubs-3559968?ampMode=1",
        "article_url": "https://uk.investing.com/news/stock-market-news/markets-are-underestimating-fed-cuts-ubs-3559968",
        "author": "Sam Boughedda",
        "description": "UBS analysts warn that markets are underestimating the extent of future interest rate cuts by the Federal Reserve, as the weakening economy is likely to justify more cuts than currently anticipated.",
        "id": "8ec638777ca03b553ae516761c2a22ba2fdd2f37befae3ab6fdab74e9e5193eb",
        "image_url": "https://i-invdn-com.investing.com/news/LYNXNPEC4I0AL_L.jpg",
        "insights": [
            {
            "sentiment": "positive",
            "sentiment_reasoning": "UBS analysts are providing a bullish outlook on the extent of future Federal Reserve rate cuts, suggesting that markets are underestimating the number of cuts that will occur.",
            "ticker": "UBS"
            }
        ],
        "keywords": [
            "Federal Reserve",
            "interest rates",
            "economic data"
        ],
        "published_utc": "2024-06-24T18:33:53Z",
        "publisher": {
            "favicon_url": "https://s3.massive.com/public/assets/news/favicons/investing.ico",
            "homepage_url": "https://www.investing.com/",
            "logo_url": "https://s3.massive.com/public/assets/news/logos/investing.png",
            "name": "Investing.com"
        },
        "tickers": [
            "UBS"
        ],
        "title": "Markets are underestimating Fed cuts: UBS By Investing.com - Investing.com UK"
        }
    ],
    "status": "OK"
}

PAGE2_RESP = {
    "results": [
        {
            "id": "JeJEhAVoKaqJ2zF9nzQYMg07UlEeWlis6Dsop33TPQY",
            "publisher": {
                "name": "MarketWatch",
                "homepage_url": "https://www.marketwatch.com/",
                "logo_url": "https://s3.massive.com/public/assets/news/logos/marketwatch.svg",
                "favicon_url": "https://s3.massive.com/public/assets/news/favicons/marketwatch.ico"
            },
            "title": "Theres a big hole in the Feds theory of inflation\u2014incomes are falling at a record 10.9 rate",
            "author": "MarketWatch",
            "published_utc": "2022-04-28T17:08:00Z",
            "article_url": "https://www.marketwatch.com/story/theres-a-big-hole-in-the-feds-theory-of-inflationincomes-are-falling-at-a-record-10-9-rate-11651165705",
            "tickers": [
                "NFLX",
                "UBS",
            ],
            "amp_url": "https://www.marketwatch.com/amp/story/theres-a-big-hole-in-the-feds-theory-of-inflationincomes-are-falling-at-a-record-10-9-rate-11651165705",
            "image_url": "https://images.mktw.net/im-533637/social",
            "description": "If inflation is all due to an overly generous federal government giving its people too much money, then our inflation problem is about to go away."
        }
    ],
    "status": "OK",
    "request_id": "f5248459196e12f27520afd41cee5126",
    "count": 1
}

EXPECTED_ITEMS = [
    TickerNews(
        amp_url="https://m.uk.investing.com/news/stock-market-news/markets-are-underestimating-fed-cuts-ubs-3559968?ampMode=1",
        article_url="https://uk.investing.com/news/stock-market-news/markets-are-underestimating-fed-cuts-ubs-3559968",
        author="Sam Boughedda",
        description="UBS analysts warn that markets are underestimating the extent of future interest rate cuts by the Federal Reserve, as the weakening economy is likely to justify more cuts than currently anticipated.",
        id="8ec638777ca03b553ae516761c2a22ba2fdd2f37befae3ab6fdab74e9e5193eb",
        image_url="https://i-invdn-com.investing.com/news/LYNXNPEC4I0AL_L.jpg",
        insights=[
            Insight(
                sentiment="positive",
                sentiment_reasoning="UBS analysts are providing a bullish outlook on the extent of future Federal Reserve rate cuts, suggesting that markets are underestimating the number of cuts that will occur.",
                ticker="UBS",
            )
        ],
        keywords=[
            "Federal Reserve",
            "interest rates",
            "economic data",
        ],
        published_utc="2024-06-24T18:33:53Z",
        publisher=Publisher(
            favicon_url="https://s3.massive.com/public/assets/news/favicons/investing.ico",
            homepage_url="https://www.investing.com/",
            logo_url="https://s3.massive.com/public/assets/news/logos/investing.png",
            name="Investing.com",
        ),
        tickers=[
            "UBS",
        ],
        title="Markets are underestimating Fed cuts: UBS By Investing.com - Investing.com UK",
    ),
    TickerNews(
        id="JeJEhAVoKaqJ2zF9nzQYMg07UlEeWlis6Dsop33TPQY",
        publisher=Publisher(
            name="MarketWatch",
            homepage_url="https://www.marketwatch.com/",
            logo_url="https://s3.massive.com/public/assets/news/logos/marketwatch.svg",
            favicon_url="https://s3.massive.com/public/assets/news/favicons/marketwatch.ico",
        ),
        title="Theres a big hole in the Feds theory of inflation—incomes are falling at a record 10.9 rate",
        author="MarketWatch",
        published_utc="2022-04-28T17:08:00Z",
        article_url="https://www.marketwatch.com/story/theres-a-big-hole-in-the-feds-theory-of-inflationincomes-are-falling-at-a-record-10-9-rate-11651165705",
        tickers=[
            "NFLX",
            "UBS",
        ],
        amp_url="https://www.marketwatch.com/amp/story/theres-a-big-hole-in-the-feds-theory-of-inflationincomes-are-falling-at-a-record-10-9-rate-11651165705",
        image_url="https://images.mktw.net/im-533637/social",
        description="If inflation is all due to an overly generous federal government giving its people too much money, then our inflation problem is about to go away.",
    ),
]


config = MassiveClientConfig(
    massive_api_key=TEST_API_KEY,
    api_base_url=TEST_BASE_URL,
)


@pytest.mark.asyncio
async def test_list_ticker_news():
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

    result = [item async for item in massiveAPIClient.list_ticker_news()]
    assert len(result) == 2
    for idx, item in enumerate(result):
        assert item == EXPECTED_ITEMS[idx]
