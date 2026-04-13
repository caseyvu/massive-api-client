
import pytest

from massive_api_client.config import MassiveClientConfig
from massive_api_client.rest import MassiveAPIClient


TEST_API_KEY = ""
TEST_BASE_URL = "https://test.testdomain.com"
TEST_TIMEOUT_SECS = 5.0
TEST_RATE_LIMIT_SLEEP_SECS = 10.0
TEST_RATE_LIMIT_MAX_RETRIES = 3

config = MassiveClientConfig(
    massive_api_key=TEST_API_KEY, 
    api_base_url=TEST_BASE_URL,
    timeout_secs=TEST_TIMEOUT_SECS,
    rate_limit_sleep_secs=TEST_RATE_LIMIT_SLEEP_SECS,
    rate_limit_max_retries=TEST_RATE_LIMIT_MAX_RETRIES,
)

@pytest.mark.asyncio
async def test_close_client():
    massiveAPIClient = MassiveAPIClient(config)
    assert massiveAPIClient._client.is_closed is False

    await massiveAPIClient.close()
    
    assert massiveAPIClient._client.is_closed is True
