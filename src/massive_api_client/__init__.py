import importlib.metadata
from .rest import MassiveAPIClient
from .exceptions import *


__version__ = importlib.metadata.version("massive-api-client")