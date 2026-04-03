import httpx
import pytest
from http import HTTPStatus
from massive.rest.models import Branding, CompanyAddress, TickerDetails
from unittest.mock import call, patch, AsyncMock

from massive_api_client.config import MassiveClientConfig
from massive_api_client.exceptions import RateLimitException
from massive_api_client.rest import MassiveAPIClient


TEST_API_KEY = ""
TEST_BASE_URL = "https://test.testdomain.com"
TEST_RATE_LIMIT_SLEEP_SECS = 10.0
TEST_RATE_LIMIT_MAX_RETRIES = 3

TEST_TICKER = "AAPL"

EXPECTED_URI = f"/v3/reference/tickers/{TEST_TICKER}"
RESPONSE = {
    "results": {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "market": "stocks",
        "locale": "us",
        "primary_exchange": "XNAS",
        "type": "CS",
        "active": True,
        "currency_name": "usd",
        "cik": "0000320193",
        "composite_figi": "BBG000B9XRY4",
        "share_class_figi": "BBG001S5N8V8",
        "market_cap": 2488795282370,
        "phone_number": "(408) 996-1010",
        "address": {
            "address1": "ONE APPLE PARK WAY",
            "city": "CUPERTINO",
            "state": "CA",
            "postal_code": "95014"
        },
        "description": "Apple designs a wide variety of consumer electronic devices, including smartphones (iPhone), tablets (iPad), PCs (Mac), smartwatches (Apple Watch), AirPods, and TV boxes (Apple TV), among others. The iPhone makes up the majority of Apple's total revenue. In addition, Apple offers its customers a variety of services such as Apple Music, iCloud, Apple Care, Apple TV+, Apple Arcade, Apple Card, and Apple Pay, among others. Apple's products run internally developed software and semiconductors, and the firm is well known for its integration of hardware, software and services. Apple's products are distributed online as well as through company-owned stores and third-party retailers. The company generates roughly 40% of its revenue from the Americas, with the remainder earned internationally.",
        "sic_code": "3571",
        "sic_description": "ELECTRONIC COMPUTERS",
        "ticker_root": "AAPL",
        "homepage_url": "https://www.apple.com",
        "total_employees": 154000,
        "list_date": "1980-12-12",
        "branding": {
            "logo_url": "https://api.massive.com/v1/reference/company-branding/d3d3LmFwcGxlLmNvbQ/images/2022-05-01_logo.svg",
            "icon_url": "https://api.massive.com/v1/reference/company-branding/d3d3LmFwcGxlLmNvbQ/images/2022-05-01_icon.png"
        },
        "share_class_shares_outstanding": 16319440000,
        "weighted_shares_outstanding": 16185181000
    },
    "status": "OK",
    "request_id": "ce8688b5f3a571351376ebd77acd146e"
}

EXPECTED_ITEM = TickerDetails(
    ticker="AAPL",
    name="Apple Inc.",
    market="stocks",
    locale="us",
    primary_exchange="XNAS",
    type="CS",
    active=True,
    currency_name="usd",
    cik="0000320193",
    composite_figi="BBG000B9XRY4",
    share_class_figi="BBG001S5N8V8",
    market_cap=2488795282370,
    phone_number="(408) 996-1010",
    address=CompanyAddress(
        address1="ONE APPLE PARK WAY",
        city="CUPERTINO",
        state="CA",
        postal_code="95014",
    ),
    description="Apple designs a wide variety of consumer electronic devices, including smartphones (iPhone), tablets (iPad), PCs (Mac), smartwatches (Apple Watch), AirPods, and TV boxes (Apple TV), among others. The iPhone makes up the majority of Apple's total revenue. In addition, Apple offers its customers a variety of services such as Apple Music, iCloud, Apple Care, Apple TV+, Apple Arcade, Apple Card, and Apple Pay, among others. Apple's products run internally developed software and semiconductors, and the firm is well known for its integration of hardware, software and services. Apple's products are distributed online as well as through company-owned stores and third-party retailers. The company generates roughly 40% of its revenue from the Americas, with the remainder earned internationally.",
    sic_code="3571",
    sic_description="ELECTRONIC COMPUTERS",
    ticker_root="AAPL",
    homepage_url="https://www.apple.com",
    total_employees=154000,
    list_date="1980-12-12",
    branding=Branding(
        logo_url="https://api.massive.com/v1/reference/company-branding/d3d3LmFwcGxlLmNvbQ/images/2022-05-01_logo.svg",
        icon_url="https://api.massive.com/v1/reference/company-branding/d3d3LmFwcGxlLmNvbQ/images/2022-05-01_icon.png",
    ),
    share_class_shares_outstanding=16319440000,
    weighted_shares_outstanding=16185181000,
)

config = MassiveClientConfig(
    massive_api_key=TEST_API_KEY, 
    api_base_url=TEST_BASE_URL,
    rate_limit_sleep_secs=TEST_RATE_LIMIT_SLEEP_SECS,
    rate_limit_max_retries=TEST_RATE_LIMIT_MAX_RETRIES,
)


@pytest.mark.asyncio
async def test_with_rate_limit_self_recovered():
    responses = [
        httpx.Response(HTTPStatus.TOO_MANY_REQUESTS, text="Rate limit reached"),
        httpx.Response(HTTPStatus.OK, json=RESPONSE),
    ]

    def transport_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == EXPECTED_URI:
            return responses.pop(0)
        return httpx.Response(404, json={"error": "not found"})

    massiveAPIClient = MassiveAPIClient(config)
    massiveAPIClient._client = httpx.AsyncClient(transport=httpx.MockTransport(handler=transport_handler))

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = await massiveAPIClient.get_ticker_details(TEST_TICKER)
        assert result == EXPECTED_ITEM

        mock_sleep.assert_awaited_once_with(TEST_RATE_LIMIT_SLEEP_SECS)


@pytest.mark.asyncio
async def test_with_rate_limit_retries_exceeded():
    def transport_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == EXPECTED_URI:
            return httpx.Response(HTTPStatus.TOO_MANY_REQUESTS, text="Rate limit reached")
        return httpx.Response(404, json={"error": "not found"})

    massiveAPIClient = MassiveAPIClient(config)
    massiveAPIClient._client = httpx.AsyncClient(transport=httpx.MockTransport(handler=transport_handler))

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(RateLimitException):
            result = await massiveAPIClient.get_ticker_details(TEST_TICKER)
            
        assert mock_sleep.await_count == TEST_RATE_LIMIT_MAX_RETRIES
        mock_sleep.assert_has_awaits(
            [
                call(TEST_RATE_LIMIT_SLEEP_SECS),
                call(TEST_RATE_LIMIT_SLEEP_SECS),
                call(TEST_RATE_LIMIT_SLEEP_SECS),
            ]
        )