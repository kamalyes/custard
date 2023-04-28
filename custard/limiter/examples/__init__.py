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
import aioredis
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, WebSocket

from custard.limiter import Limiter
from custard.limiter.depends import RateLimiter, WebSocketRateLimiter

app = FastAPI()


@app.on_event("startup")
async def startup():
    r = aioredis.from_url("redis://localhost", password="M5Pi9YW6u", db=0, port=16389)
    await Limiter.init(r)


@app.on_event("shutdown")
async def shutdown():
    await Limiter.close()


@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def index_get():
    return {"msg": "Hello World"}


@app.post("/", dependencies=[Depends(RateLimiter(times=1, seconds=5))])
async def index_post():
    return {"msg": "Hello World"}


@app.get(
    "/multiple",
    dependencies=[
        Depends(RateLimiter(times=1, seconds=5)),
        Depends(RateLimiter(times=2, seconds=15)),
    ],
)
async def multiple():
    return {"msg": "Hello World"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ratelimit = WebSocketRateLimiter(times=1, seconds=5)
    while True:
        try:
            data = await websocket.receive_text()
            await ratelimit(websocket, context_key=data)  # NB: context_key is optional
            await websocket.send_text("Hello, world")
        except HTTPException:
            await websocket.send_text("Hello again")


if __name__ == "__main__":
    uvicorn.run("__init__:app", reload=True)
