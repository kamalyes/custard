# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  iterables.py
@Time    :  2022/5/1 8:21 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from itertools import islice
from typing import Generic, Iterable, Optional, TypeVar

from pydantic import conint

from .api import create_page, resolve_params
from .bases import AbstractPage, AbstractParams
from .limit_offset import LimitOffsetPage as DefaultLimitOffsetPage
from .limit_offset import LimitOffsetParams
from .pagination import Page as DefaultPage
from .pagination import Params

T = TypeVar("T")


class Page(DefaultPage, Generic[T]):
    total: Optional[conint(ge=0)]  # type: ignore


class LimitOffsetPage(DefaultLimitOffsetPage, Generic[T]):
    total: Optional[conint(ge=0)]  # type: ignore


def paginate(
    iterable: Iterable[T],
    params: Optional[AbstractParams] = None,
    total: Optional[int] = None,
) -> AbstractPage[T]:
    params = resolve_params(params)
    raw_params = params.to_raw_params()

    items = [*islice(iterable, raw_params.offset, raw_params.offset + raw_params.limit)]
    return create_page(items, total, params)  # type: ignore


__all__ = [
    "Page",
    "Params",
    "LimitOffsetPage",
    "LimitOffsetParams",
    "paginate",
]
