# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  pagination.py
@Time    :  2022/5/1 8:21 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from __future__ import annotations

import math
from typing import Generic, Sequence, TypeVar

from fastapi import Query
from pydantic import BaseModel

from .bases import AbstractPage, AbstractParams, RawParams

T = TypeVar("T")


class Params(BaseModel, AbstractParams):
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(20, gt=0, le=100, description="Page size")

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.size,
            offset=self.size * (self.page - 1),
        )


class Page(AbstractPage[T], Generic[T]):
    results: Sequence[T]
    total: int
    page: int
    size: int
    next: str
    previous: str
    total_pages: int

    __params_type__ = Params  # Set params related to Page

    @classmethod
    def create(
        cls,
        results: results,
        total: int,
        params: Params,
    ) -> Page[T]:
        page = params.page
        size = params.size
        total_pages = math.ceil(total / params.size)
        next = f"?page={page + 1}&size={size}" if (page + 1) <= total_pages else "null"
        previous = f"?page={page - 1}&size={size}" if (page - 1) >= 1 else "null"

        return cls(
            results=results,
            total=total,
            page=params.page,
            size=params.size,
            next=next,
            previous=previous,
            total_pages=total_pages,
        )
