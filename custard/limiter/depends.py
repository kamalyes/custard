# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  depends.py
@Time    :  2022/5/27 12:09 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from typing import Any, Callable, Coroutine, Optional

from pydantic import conint
from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket

from custard.limiter import Limiter
from custard.limiter.enums import GlobalVarEnum


class RateLimiter:
    def __init__(
        self,
        times: conint(ge=0) = 1,
        milliseconds: conint(ge=-1) = 0,
        seconds: conint(ge=-1) = 0,
        minutes: conint(ge=-1) = 0,
        hours: conint(ge=-1) = 0,
        identifier: Optional[Callable] = None,
        callback: Optional[Callable] = None,
    ):
        self.times = times
        self.milliseconds = milliseconds + 1000 * seconds + 60000 * minutes + 3600000 * hours
        self.identifier = identifier
        self.callback = callback

    async def _check(self, key):
        redis = Limiter.redis
        pexpire = await redis.evalsha(Limiter.lua_sha, 1, key, str(self.times), str(self.milliseconds))
        return pexpire

    async def __call__(self, request: Request, response: Response):
        if not Limiter.redis:
            raise Exception(GlobalVarEnum.INIT_ERR_MSG)
        route_index = 0
        dep_index = 0
        for i, route in enumerate(request.app.routes):
            if route.path == request.scope["path"] and request.method in route.methods:
                route_index = i
                for j, dependency in enumerate(route.dependencies):
                    if self is dependency.dependency:
                        dep_index = j
                        break

        # moved here because constructor run before app startup
        identifier = self.identifier or Limiter.identifier
        callback = self.callback or Limiter.http_callback
        rate_key = await identifier(request)
        key = f"{Limiter.prefix}:{rate_key}:{route_index}:{dep_index}"
        pexpire = await self._check(key)
        if pexpire != 0:
            return await callback(request, response, pexpire)
        return None


class WebSocketRateLimiter(RateLimiter):
    async def __call__(self, ws: WebSocket, context_key="") -> Coroutine[Any, Any, Any]:
        if not Limiter.redis:
            raise Exception(GlobalVarEnum.INIT_ERR_MSG)
        identifier = self.identifier or Limiter.identifier
        rate_key = await identifier(ws)
        key = f"{Limiter.prefix}:ws:{rate_key}:{context_key}"
        pexpire = await self._check(key)
        callback = self.callback or Limiter.ws_callback
        if pexpire != 0:
            return await callback(ws, pexpire)
        return None
