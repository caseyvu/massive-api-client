from httpx import Response
from typing import Optional


class APIException(Exception):
    
    def __init__(self, message: Optional[str] = None, response: Optional[Response] = None):
        self.status = None if response is None else response.status_code
        self.response_text = None if response is None else response.text
        self.message = message
        super().__init__(message) 

    def __str__(self):
        return f"{super().__str__()}\nStatus={self.status}\nResponse Content: {self.response_text}"


class RateLimitException(APIException):
    pass


class BadResponseException(APIException):
    pass

