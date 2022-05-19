# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.7
# Python Version 3.9.11
"""
@File    :  __init__.py
@Time    :  2022/5/15 10:37 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
__version__ = '0.0.1'
__version_tuple__ = (0, 0, 1)
__all__ = ('func_timeout', 'func_set_timeout', 'FunctionTimedOut', 'StoppableThread')

from .dafunc import func_timeout, func_set_timeout
from .exceptions import FunctionTimedOut
from .stop_pable_thread import StoppableThread
