# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  loader.py
@Time    :  2022/7/18 10:16
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import json

import requests


def load_json(json_str):
    """
    加载json数据
    Args:
        json_str:

    Returns:

    """
    return json.loads(json_str)


def load_file(path):
    """
    加载json文件
    Args:
        path:

    Returns:

    """
    with open(path, encoding='utf8') as f:
        return load_json(f.read())


def load_url(url, method='get', **kwargs):
    """
    通过url加载json
    Args:
        url:
        method:
        **kwargs:

    Returns:

    """
    return requests.request(url=url, method=method, **kwargs).json()
