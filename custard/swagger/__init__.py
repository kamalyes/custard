# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  __init__.py
@Time    :  2022/7/18 10:16
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from .swagger import Swagger2
from .exception import ParseMethodError
from .loader import load_file, load_url

def swagger_parse(url=None, file=None, deep=5, **kwargs):
    """
    解析swagger
    Args:
        url:
        file:
        deep:
        **kwargs:

    Returns:

    """
    if url:
        source = load_url(url, **kwargs)
    elif file:
        source = load_file(file)
    else:
        raise ParseMethodError("解析方式错误")
    return Swagger2(source, deep=deep)
