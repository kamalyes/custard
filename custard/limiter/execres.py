from fastapi import status

from custard.limiter.enums import GlobalVarEnum


class RateLimitException(Exception):
    def __init__(
        self,
        headers: dict,
        code: int = 429,
        detail: str = GlobalVarEnum.INIT_ERR_MSG,
        status_code: int = status.HTTP_429_TOO_MANY_REQUESTS,
    ):
        self.code = code
        self.headers = headers
        self.detail = detail
        self.status_code = status_code
