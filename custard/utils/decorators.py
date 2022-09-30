# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  decorators.py
@Time    :  2022/5/30 1:35 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from functools import wraps
from typing import Callable, Dict, Tuple, TypeVar

from custard.utils import text

T = TypeVar("T")


def slugify(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args: Tuple[T, ...], **kwargs: Dict[str, T]) -> str:
        return text.slugify(fn(*args, **kwargs))

    return wrapper


def slugify_domain(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args: Tuple[T, ...], **kwargs: Dict[str, T]) -> str:
        return text.slugify(fn(*args, **kwargs), allow_dots=True)

    return wrapper


def slugify_unicode(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args: Tuple[T, ...], **kwargs: Dict[str, T]) -> str:
        return text.slugify(fn(*args, **kwargs), allow_unicode=True)

    return wrapper


def lowercase(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args: Tuple[T, ...], **kwargs: Dict[str, T]) -> str:
        return fn(*args, **kwargs).lower()

    return wrapper
