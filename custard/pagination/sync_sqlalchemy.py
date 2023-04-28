# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  sync_sqlalchemy.py
@Time    :  2022/5/1 8:21 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from __future__ import annotations

from typing import Any, Optional, TypeVar

from sqlalchemy.orm import Query
from sqlalchemy.sql import Select

from .api import create_page, resolve_params
from .bases import AbstractPage, AbstractParams

T = TypeVar("T", Select, Query)


def paginate_query(query: T, params: AbstractParams) -> T:
    raw_params = params.to_raw_params()
    return query.limit(raw_params.limit).offset(raw_params.offset)


def _to_dict(obj: Any) -> Any:
    try:
        return obj._asdict()
    except AttributeError:
        return obj


def paginate(query: Query, params: Optional[AbstractParams] = None) -> AbstractPage:
    params = resolve_params(params)

    total = query.count()
    items = [_to_dict(item) for item in paginate_query(query, params)]

    return create_page(items, total, params)


__all__ = ["paginate_query", "paginate"]
