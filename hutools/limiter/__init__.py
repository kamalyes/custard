# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  __init__.py
@Time    :  2022/5/2 2:52 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""

from math import ceil
from typing import Callable

import aioredis
from starlette.requests import Request
from starlette.responses import Response

from ..limiter.execres import RateLimitException


async def default_identifier(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0]
    else:
        ip = request.client.host
    return ip + ":" + request.scope["path"]


async def default_callback(request: Request, response: Response, pexpire: int):
    """
    default callback when too many requests
    :param request:
    :param pexpire: The remaining milliseconds
    :param response:
    :return:
    """
    expire = ceil(pexpire / 1000)
    raise RateLimitException(headers={"Retry-After": str(expire)})


class Limiter:
    redis: aioredis.Redis = None
    prefix: str = None
    lua_sha: str = None
    identifier: Callable = None
    callback: Callable = None
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
            redis: aioredis.Redis,
            prefix: str = "limiter",
            identifier: Callable = default_identifier,
            callback: Callable = default_callback,
    ):
        cls.redis = redis
        cls.prefix = prefix
        cls.identifier = identifier
        cls.callback = callback
        cls.lua_sha = await redis.script_load(cls.lua_script)

    @classmethod
    async def close(cls):
        await cls.redis.close()
