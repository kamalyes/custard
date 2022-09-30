# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  limiter.py
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

from custard.limiter import Limiter
from custard.limiter.depends import RateLimiter

app = FastAPI()


@app.on_event("startup")
async def startup():
    """https://aioredis.readthedocs.io/en/latest/getting-started/"""
    redis = await aioredis.from_url("redis://localhost:6379", password="PassWord@Redis123", encoding="utf8")
    await Limiter.init(redis)


@app.on_event("shutdown")
async def shutdown():
    await Limiter.close()


@app.get("/", dependencies=[Depends(RateLimiter(counts=2, seconds=5))])
async def index():
    return {"msg": "Hello World"}


@app.get(
    "/multiple",
    dependencies=[
        Depends(RateLimiter(counts=5, seconds=5)),
        Depends(RateLimiter(counts=6, seconds=15)),
    ],
)
async def multiple():
    return {"msg": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("limiter:app", debug=True, reload=True)
