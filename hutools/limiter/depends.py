# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  depends.py
@Time    :  2022/5/2 2:52 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""

from typing import Callable, Optional

from pydantic import conint
from starlette.requests import Request
from starlette.responses import Response

from ..limiter import Limiter
from ..limiter.enums import GlobalVarEnum


class RateLimiter:
    def __init__(
            self,
            counts: conint(ge=0) = 1,
            milliseconds: conint(ge=-1) = 0,
            seconds: conint(ge=-1) = 0,
            minutes: conint(ge=-1) = 0,
            hours: conint(ge=-1) = 0,
            identifier: Optional[Callable] = None,
            callback: Optional[Callable] = None,
    ):
        self.counts = counts
        self.milliseconds = (
                milliseconds + 1000 * seconds + 60000 * minutes + 3600000 * hours
        )
        self.identifier = identifier
        self.callback = callback

    async def __call__(self, request: Request, response: Response):
        if not Limiter.redis:
            raise Exception(
                "You must call Limiter.init in startup event of fastapi!"
            )
        index = 0
        for route in request.app.routes:
            if route.path == request.scope["path"]:
                for idx, dependency in enumerate(route.dependencies):
                    if self is dependency.dependency:
                        index = idx
                        break
        # moved here because constructor run before app startup
        identifier = self.identifier or Limiter.identifier
        callback = self.callback or Limiter.callback
        redis = Limiter.redis
        rate_key = await identifier(request)
        key = f"{GlobalVarEnum.APP_NAME.lower()}:{Limiter.prefix}:{rate_key}:{index}"
        pexpire = await redis.evalsha(
            Limiter.lua_sha, 1, key, str(self.counts), str(self.milliseconds)
        )
        if pexpire != 0:
            return await callback(request, response, pexpire)
