# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  async_lur
@Time    :  2022/10/18 10:00 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import asyncio

import aiohttp
from custard.cache.async_lru import alru_cache


@alru_cache(maxsize=32)
async def get_pep(num):
    resource = 'http://www.python.org/dev/peps/pep-%05d/' % num
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(resource) as s:
                return await s.read()
        except aiohttp.ClientError:
            return 'Not Found'


async def main():
    for n in 8, 290, 308, 320, 8, 218, 320, 279, 289, 320, 9991:
        pep = await get_pep(n)
        print(n, len(pep))

    print(get_pep.cache_info())
    # CacheInfo(hits=3, misses=8, maxsize=32, currsize=8)

    # closing is optional, but highly recommended
    await get_pep.close()


loop = asyncio.get_event_loop()

loop.run_until_complete(main())

loop.close()