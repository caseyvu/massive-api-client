from collections.abc import AsyncIterator
from massive.rest.models import (
    AssetClass,
    Locale,
    Order, 
    Sort,
    RelatedCompany,
    Ticker,
    TickerChange,
    TickerChangeEvent,
    TickerChangeResults,
    TickerDetails,
    TickerNews,
    TickerTypes,
)
from typing import Any, Dict, List, Optional, Union

from .base import BaseClient


class TickersClient(BaseClient):
    async def list_tickers(
        self,
        ticker: Optional[str] = None,
        ticker_lt: Optional[str] = None,
        ticker_lte: Optional[str] = None,
        ticker_gt: Optional[str] = None,
        ticker_gte: Optional[str] = None,
        type: Optional[str] = None,
        market: Optional[str] = None,
        exchange: Optional[str] = None,
        cusip: Optional[int] = None,
        cik: Optional[int] = None,
        date: Optional[str] = None,
        active: Optional[bool] = None,
        search: Optional[str] = None,
        limit: Optional[int] = 10,
        sort: Optional[Union[str, Sort]] = "ticker",
        order: Optional[Union[str, Order]] = "asc",
        max_num_pages: Optional[int] = None,
    ) -> AsyncIterator[Ticker]:
        """
        Query all ticker symbols which are supported by Massive.com. This API currently includes Stocks/Equities, Indices, Forex, and Crypto.

        :param ticker: Specify a ticker symbol. Defaults to empty string which queries all tickers.
        :param ticker_lt: Ticker less than.
        :param ticker_lte: Ticker less than or equal to.
        :param ticker_gt: Ticker greater than.
        :param ticker_gte: Ticker greater than or equal to.
        :param type: Specify the type of the tickers. Find the types that we support via our Ticker Types API. Defaults to empty string which queries all types.
        :param market: Filter by market type. By default all markets are included.
        :param exchange: Specify the assets primary exchange Market Identifier Code (MIC) according to ISO 10383. Defaults to empty string which queries all exchanges.
        :param cusip: Specify the CUSIP code of the asset you want to search for. Find more information about CUSIP codes at their website. Defaults to empty string which queries all CUSIPs.
        :param cik: Specify the CIK of the asset you want to search for. Find more information about CIK codes at their website. Defaults to empty string which queries all CIKs.
        :param date: Specify a point in time to retrieve tickers available on that date. Defaults to the most recent available date.
        :param search: Search for terms within the ticker and/or company name.
        :param active: Specify if the tickers returned should be actively traded on the queried date. Default is true.
        :param limit: Limit the size of the response per-page, default is 100 and max is 1000.
        :param sort: The field to sort the results on. Default is ticker. If the search query parameter is present, sort is ignored and results are ordered by relevance.
        :param order: The order to sort the results on. Default is asc (ascending).
        :return: Iterator of tickers.
        """
        uri = "/v3/reference/tickers"

        async for r in self.request_with_pagination(
            uri=uri, 
            params=self._get_params(self.list_tickers, locals()), 
            deserializer=Ticker.from_dict,
            max_num_pages=max_num_pages,
        ):
            yield r

    async def get_ticker_details(
        self,
        ticker: str,
        date: Optional[str] = None,
    ) -> TickerDetails:
        """
        Get a single ticker supported by Massive.com. This response will have detailed information about the ticker and the company behind it.

        :param ticker: The ticker symbol of the asset.
        :param date: Specify a point in time to get information about the ticker available on that date. When retrieving information from SEC filings, we compare this date with the period of report date on the SEC filing.
        :return: Ticker Details V3
        """
        uri = f"/v3/reference/tickers/{ticker}"

        return await self.request(
            uri=uri, 
            params=self._get_params(self.get_ticker_details, locals()),
            deserializer=TickerDetails.from_dict,
        )

    async def get_ticker_events(
        self,
        ticker: str,
        types: Optional[List[str]] = None,
    ) -> TickerChangeResults:
        """
        Get event history of ticker given particular point in time.
        :param ticker: The ticker symbol of the asset.
        :param types: A comma-separated list of the types of event to include. Currently ticker_change is the only supported event_type. Leave blank to return all supported event_types.
        :return: Ticker Event VX (Experimental)
        """
        uri = f"/vX/reference/tickers/{ticker}/events"

        params = {"types": ",".join(types) if types is not None else ""}

        def deserialize_event(e) -> TickerChangeEvent:
            return TickerChangeEvent(
                type=e.get("type"),
                date=e.get("date"),
                ticker_change=None if "ticker_change" not in e else TickerChange.from_dict(e.get("ticker_change")),
            )
        
        def deserialize_result(d) -> TickerChangeResults:
            return TickerChangeResults(
                name=d.get("name"),
                composite_figi=d.get("composite_figi"),
                cik=d.get("cik"),
                events=[deserialize_event(e) for e in d.get("events", [])]
            )

        return await self.request(
            uri=uri, 
            params=params,
            deserializer=deserialize_result,
        )

    async def list_ticker_news(
        self,
        ticker: Optional[str] = None,
        ticker_lt: Optional[str] = None,
        ticker_lte: Optional[str] = None,
        ticker_gt: Optional[str] = None,
        ticker_gte: Optional[str] = None,
        published_utc: Optional[str] = None,
        published_utc_lt: Optional[str] = None,
        published_utc_lte: Optional[str] = None,
        published_utc_gt: Optional[str] = None,
        published_utc_gte: Optional[str] = None,
        limit: Optional[int] = None,
        sort: Optional[Union[str, Sort]] = None,
        order: Optional[Union[str, Order]] = None,
        max_num_pages: Optional[int] = None,
    ) -> AsyncIterator[TickerNews]:
        """
        Get the most recent news articles relating to a stock ticker symbol, including a summary of the article and a link to the original source.

        :param ticker: Return results that contain this ticker.
        :param published_utc: Return results published on, before, or after this date.
        :param limit: Limit the number of results returned per-page, default is 10 and max is 1000.
        :param sort: Sort field used for ordering.
        :param order: Order results based on the sort field.
        :return: Iterator of Ticker News.
        """
        uri = "/v2/reference/news"

        async for r in self.request_with_pagination(
            uri=uri, 
            params=self._get_params(self.list_ticker_news, locals()), 
            deserializer=TickerNews.from_dict,
            max_num_pages=max_num_pages,
        ):
            yield r
    
    async def get_ticker_types(
        self,
        asset_class: Optional[Union[str, AssetClass]] = None,
        locale: Optional[Union[str, Locale]] = None,
    ) -> List[TickerTypes]:
        """
        List all ticker types that Massive.com has.

        :param asset_class: Filter by asset class.
        :param locale: Filter by locale.
        :param params: Any additional query params.
        :param raw: Return raw object instead of results object.
        :return: Ticker Types.
        """
        uri = "/v3/reference/tickers/types"

        return await self.request(
            uri=uri,
            params=self._get_params(self.get_ticker_types, locals()),
            deserializer=TickerTypes.from_dict,
        )

    async def get_related_companies(
        self,
        ticker: str,
    ) -> RelatedCompany:
        """
        Get a list of tickers related to the queried ticker based on News and Returns data.

        :param ticker: The ticker symbol to search.
        :return: Related Companies.
        """
        uri = f"/v1/related-companies/{ticker}"

        return await self.request(
            uri=uri,
            params={},
            deserializer=RelatedCompany.from_dict,
        )