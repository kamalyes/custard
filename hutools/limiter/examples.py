# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  examples.py
@Time    :  2022/5/7 9:49 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import aioredis
import uvicorn
from fastapi import Depends, FastAPI

from app.middleware.limiter import PikaLimiter
from app.middleware.limiter.depends import RateLimiter

app = FastAPI()


@app.on_event("startup")
async def startup():
    """https://aioredis.readthedocs.io/en/latest/getting-started/"""
    redis = await aioredis.from_url("redis://localhost", encoding="utf8")
    await PikaLimiter.init(redis)


@app.on_event("shutdown")
async def shutdown():
    await PikaLimiter.close()


@app.get("/", dependencies=[Depends(RateLimiter(counts=2, seconds=5))])
async def index():
    return {"msg": "Hello World"}


@app.get(
    "/multiple",
    dependencies=[
        Depends(RateLimiter(counts=1, seconds=5)),
        Depends(RateLimiter(counts=2, seconds=15)),
    ],
)
async def multiple():
    return {"msg": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("examples:app", debug=True, reload=True)
