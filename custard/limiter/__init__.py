# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  __init__.py
@Time    :  2022/5/27 12:09 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from math import ceil
from typing import Callable, Union

from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket

from ..limiter.enums import GlobalVarEnum
from ..limiter.execres import RateLimitException


async def default_identifier(request: Union[Request, WebSocket]):
    forwarded = request.headers.get("X-Forwarded-For")
    ip = forwarded.split(",")[0] if forwarded else request.client.host
    return ip + ":" + request.scope["path"]


async def http_default_callback(request: Request, response: Response, pexpire: int) -> RateLimitException:
    """
    default callback when too many requests
    :param request:
    :param pexpire: The remaining milliseconds
    :param response:
    :return:
    """
    expire = ceil(pexpire / 1000)
    raise RateLimitException(headers={"Retry-After": str(expire)})


async def ws_default_callback(ws: WebSocket, pexpire: int) -> RateLimitException:
    """
    default callback when too many requests
    :param ws:
    :param pexpire: The remaining milliseconds
    :return:
    """
    expire = ceil(pexpire / 1000)
    raise RateLimitException(headers={"Retry-After": str(expire)})


class Limiter:
    redis = None
    prefix: str = None
    lua_sha: str = None
    identifier: Callable = None
    http_callback: Callable = None
    ws_callback: Callable = None
    lua_script = """local key = KEYS[1]
local limit = tonumber(ARGV[1])
local expire_time = ARGV[2]
local current = tonumber(redis.call('get', key) or "0")
if current > 0 then
 if current + 1 > limit then
 return redis.call("PTTL",key)
 else
        redis.call("INCR", key)
 return 0
 end
else
    redis.call("SET", key, 1,"px",expire_time)
 return 0
end"""

    @classmethod
    async def init(
        cls,
        redis,
        prefix: str = f"{GlobalVarEnum.APP_NAME.lower()}:limiter",
        identifier: Callable = default_identifier,
        http_callback: Callable = http_default_callback,
        ws_callback: Callable = ws_default_callback,
    ):
        cls.redis = redis
        cls.prefix = prefix
        cls.identifier = identifier
        cls.http_callback = http_callback
        cls.ws_callback = ws_callback
        cls.lua_sha = await redis.script_load(cls.lua_script)

    @classmethod
    async def close(cls):
        await cls.redis.close()
