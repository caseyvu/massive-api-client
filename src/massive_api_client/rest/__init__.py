from .aggs import AggsClient
from .indicators import IndicatorsClient
from .reference import TickersClient

class MassiveAPIClient(AggsClient, IndicatorsClient, TickersClient):
    pass