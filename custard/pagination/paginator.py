# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  paginator.py
@Time    :  2022/5/1 8:21 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from typing import Callable, Optional, Sequence, TypeVar

from .api import create_page, resolve_params
from .bases import AbstractPage, AbstractParams

T = TypeVar("T")


def paginate(
    sequence: Sequence[T],
    params: Optional[AbstractParams] = None,
    length_function: Callable[[Sequence[T]], int] = len,
) -> AbstractPage[T]:
    params = resolve_params(params)
    raw_params = params.to_raw_params()

    return create_page(
        items=sequence[raw_params.offset : raw_params.offset + raw_params.limit],
        total=length_function(sequence),
        params=params,
    )


__all__ = ["paginate"]
