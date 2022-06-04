from fastapi import status


class RateLimitException(Exception):
    def __init__(
            self,
            headers: dict,
            code: int = 429,
            detail: str = "The interview is too fast, please have a cup of tea and take a break!",
            status_code: int = status.HTTP_429_TOO_MANY_REQUESTS,
    ):
        self.code = code
        self.headers = headers
        self.detail = detail
        self.status_code = status_code
