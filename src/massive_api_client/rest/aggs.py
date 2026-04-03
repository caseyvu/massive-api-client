from collections.abc import AsyncIterator
from datetime import datetime, date
from massive.rest.models import Agg, GroupedDailyAgg, Sort
from typing import List, Optional, Union

from .base import BaseClient


class AggsClient(BaseClient):
    async def list_aggs(
        self,
        ticker: str,
        multiplier: int,
        timespan: str,
        # "from" is a keyword in python https://www.w3schools.com/python/python_ref_keywords.asp
        from_: Union[str, int, datetime, date],
        to: Union[str, int, datetime, date],
        adjusted: Optional[bool] = None,
        sort: Optional[Union[str, Sort]] = None,
        limit: Optional[int] = None,
        max_num_pages: Optional[int] = None,
    ) -> AsyncIterator[Agg]:
        """
        List aggregate bars for a ticker over a given date range in custom time window sizes.

        :param ticker: The ticker symbol.
        :param multiplier: The size of the timespan multiplier.
        :param timespan: The size of the time window.
        :param from_: The start of the aggregate time window as YYYY-MM-DD, a date, Unix MS Timestamp, or a datetime.
        :param to: The end of the aggregate time window as YYYY-MM-DD, a date, Unix MS Timestamp, or a datetime.
        :param adjusted: Whether or not the results are adjusted for splits. By default, results are adjusted. Set this to false to get results that are NOT adjusted for splits.
        :param sort: Sort the results by timestamp. asc will return results in ascending order (oldest at the top), desc will return results in descending order (newest at the top).The end of the aggregate time window.
        :param limit: Limits the number of base aggregates queried to create the aggregate results. Max 50000 and Default 5000. Read more about how limit is used to calculate aggregate results in our article on Aggregate Data API Improvements.
        :return: Iterator of aggregates
        """
        if isinstance(from_, datetime):
            from_ = int(from_.timestamp() * self.time_mult("millis"))

        if isinstance(to, datetime):
            to = int(to.timestamp() * self.time_mult("millis"))
            
        uri = f"/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_}/{to}"

        async for r in self.request_with_pagination(
            uri=uri, 
            params=self._get_params(self.list_aggs, locals()), 
            deserializer=Agg.from_dict,
            max_num_pages=max_num_pages,
        ):
            yield r

    async def get_grouped_daily_aggs(
        self,
        date: Union[str, date],
        market_type: str = "stocks",
        locale: str = "us",
        adjusted: Optional[bool] = None,
        include_otc: bool = False,
    ) -> List[GroupedDailyAgg]:
        """
        Get the daily open, high, low, and close (OHLC) for the entire market.

        :param date: The beginning date for the aggregate window.
        :param adjusted: Whether or not the results are adjusted for splits. By default, results are adjusted. Set this to false to get results that are NOT adjusted for splits.
        :return: List of grouped daily aggregates
        """
        uri = f"/v2/aggs/grouped/locale/{locale}/market/{market_type}/{date}"

        return await self.request(
            uri=uri, 
            params=self._get_params(self.get_grouped_daily_aggs, locals()),
            deserializer=GroupedDailyAgg.from_dict,
        )