from .aggs import AggsClient
from .reference import TickersClient

class MassiveAPIClient(AggsClient, TickersClient):
    pass