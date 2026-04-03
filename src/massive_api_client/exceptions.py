from httpx import Response
from typing import Optional


class APIException(Exception):
    
    def __init__(self, message: Optional[str] = None, response: Optional[Response] = None):
        self.status = None if response is None else response.status_code
        self.response_text = None if response is None else response.text
        self.message = message


class RateLimitException(APIException):
    pass


class BadResponseException(APIException):
    pass

