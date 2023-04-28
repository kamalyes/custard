# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  test_depends.py
@Time    :  2022/5/27 12:09 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from time import sleep

from starlette.testclient import TestClient

from custard.limiter.examples import app


def test_limiter() -> None:
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200

        response = client.get("/")
        assert response.status_code == 200

        response = client.get("/")
        assert response.status_code == 429

        response = client.post("/")
        assert response.status_code == 200

        response = client.post("/")
        assert response.status_code == 429
        sleep(5)

        response = client.get("/")
        assert response.status_code == 200

        response = client.post("/")
        assert response.status_code == 200


def test_limiter_multiple() -> None:
    with TestClient(app) as client:
        response = client.get("/multiple")
        assert response.status_code == 200

        response = client.get("/multiple")
        assert response.status_code == 429
        sleep(5)

        response = client.get("/multiple")
        assert response.status_code == 200

        response = client.get("/multiple")
        assert response.status_code == 429
        sleep(10)

        response = client.get("/multiple")
        assert response.status_code == 200


def test_limiter_websockets() -> None:
    with TestClient(app) as client, client.websocket_connect("/ws") as ws:
        ws.send_text("Hi")
        data = ws.receive_text()
        assert data == "Hello, world"

        ws.send_text("Hi")
        data = ws.receive_text()
        assert data == "Hello again"

        ws.send_text("Hi 2")
        data = ws.receive_text()
        assert data == "Hello, world"
        ws.close()
