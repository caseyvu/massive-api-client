import asyncio
import httpx
import inspect
import logging
from collections.abc import AsyncIterator
from datetime import datetime
from enum import Enum
from http import HTTPStatus
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse

from ..config import MassiveClientConfig
from ..exceptions import BadResponseException, RateLimitException


logger = logging.getLogger(__name__)


class BaseClient:

    RATE_LIMIT_HTTP_CODE = HTTPStatus.TOO_MANY_REQUESTS
    RESULTS_FIELD = "results"
    NEXT_URL_FIELD = "next_url"
    HTTP_METHOD_GET = "GET"
    DEFAULT_MAX_NUM_PAGES = 10000


    def __init__(self, config: MassiveClientConfig) -> None:
        self._api_key = config.massive_api_key
        self._base_url = config.api_base_url.rstrip("/")
        self._rate_limit_sleep_secs = config.rate_limit_sleep_secs
        self._rate_limit_max_retries = config.rate_limit_max_retries
        self._client = httpx.AsyncClient(timeout=config.timeout_secs)
        self._headers = {
            "Authorization": "Bearer " + self._api_key,
            "Accept-Encoding": "gzip",
        }

    async def close(self) -> None:
        await self._client.aclose()

    async def request(self, uri: str, params: Optional[Dict] = None, deserializer=None, result_key: Optional[str] = RESULTS_FIELD, method: str = HTTP_METHOD_GET) -> Any:
        full_url = self.make_full_url(uri)
        raw_resp = await self._request_with_retries(method, full_url, params, self._headers)
        response = raw_resp.json()
        if result_key is not None and result_key not in response:
            raise BadResponseException(message=f"API Response does not contain field: {result_key}", response=raw_resp)
        
        resp_obj = response if result_key is None else response[result_key]
        return self._apply_deserializer(deserializer, resp_obj)

    async def request_with_pagination(
            self, uri: str, params: Optional[Dict] = None, deserializer=None, 
            max_num_pages: Optional[int] = DEFAULT_MAX_NUM_PAGES, # Defensive check to avoid infinite pagination 
            result_key: str = RESULTS_FIELD, method: str = HTTP_METHOD_GET) -> AsyncIterator[Any]:
        full_url = self.make_full_url(uri)

        max_num_pages = self.DEFAULT_MAX_NUM_PAGES if max_num_pages is None else max_num_pages
        page_i = 0
        while page_i < max_num_pages:
            raw_resp = await self._request_with_retries(method, full_url, params, self._headers)
            response = raw_resp.json()
            if result_key not in response:
                raise BadResponseException(message=f"API Response does not contain field: {result_key}", response=raw_resp)
        
            for item in response[result_key]:
                yield self._apply_deserializer(deserializer, item)

            next_url = response.get(self.NEXT_URL_FIELD)
            if next_url is None:
                break
            
            parsed = urlparse(next_url)
            params = parsed.query
            page_i += 1

    def _apply_deserializer(self, deserializer, resp_obj) -> Any:
        if deserializer:
            if type(resp_obj) == list:
                return [deserializer(o) for o in resp_obj]
            return deserializer(resp_obj)
        return resp_obj

    def make_full_url(self, uri: str) -> str:
        return f"{self._base_url}{uri}"
    
    async def _request_with_retries(self, method: str, url: str, params: Optional[Union[Dict, str]] = None, headers: Optional[Dict] = None) -> httpx.Response:
        response = await self._client.request(method, url, params=params, headers=headers)

        retries_count = 0
        while response.status_code == self.RATE_LIMIT_HTTP_CODE and retries_count < self._rate_limit_max_retries:
            logger.warning(
                "Rate limited with status_code=%s; sleeping %s seconds before retry %s for %s %s",
                response.status_code,
                self._rate_limit_sleep_secs,
                retries_count + 1,
                method,
                url,
            )
            await asyncio.sleep(self._rate_limit_sleep_secs)
            response = await self._client.request(method, url, params=params, headers=headers)
            retries_count += 1

        if response.status_code == self.RATE_LIMIT_HTTP_CODE:
            raise RateLimitException(message=f"Receive status_code={response.status_code} even after {retries_count} retries", response=response)
        
        response.raise_for_status()
        return response

    def _get_params(
        self, fn, caller_locals: Dict[str, Any], datetime_res: str = "nanos"
    ):
        params = {}
        # https://docs.python.org/3.8/library/inspect.html#inspect.Signature
        for argname, v in inspect.signature(fn).parameters.items():
            if argname in ["max_num_pages"]: # ignore these params as they are ops params
                continue

            # Only params with default are considered part of "params"
            if v.default is v.empty:
                continue
            
            val = caller_locals.get(argname, v.default)
            if val is None: # If val is None, we can skip this
                continue

            if isinstance(val, Enum):
                val = val.value
            elif isinstance(val, bool):
                val = str(val).lower()
            elif isinstance(val, datetime):
                val = int(val.timestamp() * self.time_mult(datetime_res))

            param_name = argname
            for ext in ["lt", "lte", "gt", "gte", "any_of"]:
                if argname.endswith(f"_{ext}"):
                    param_name = argname[: -len(f"_{ext}")] + f".{ext}"
                    break
            if param_name.endswith(".any_of"):
                val = ",".join(val)
            params[param_name] = val

        return params
    
    @staticmethod
    def time_mult(timestamp_res: str) -> int:
        if timestamp_res == "nanos":
            return 1000000000
        elif timestamp_res == "micros":
            return 1000000
        elif timestamp_res == "millis":
            return 1000

        return 1
        
