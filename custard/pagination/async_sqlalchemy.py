# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  async_sqlalchemy.py
@Time    :  2022/5/1 8:21 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import func, select

from .api import create_page, resolve_params
from .bases import AbstractPage, AbstractParams
from .sync_sqlalchemy import paginate_query

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.sql import Select


async def paginate(
    session: AsyncSession,
    query: Select,
    params: Optional[AbstractParams] = None,
) -> AbstractPage:  # pragma: no cover # FIXME: fix coverage report generation
    params = resolve_params(params)

    total = await session.scalar(select(func.count()).select_from(query.subquery()))  # type: ignore
    items = await session.execute(paginate_query(query, params))

    return create_page(items.scalars().unique().all(), total, params)


__all__ = ["paginate"]
