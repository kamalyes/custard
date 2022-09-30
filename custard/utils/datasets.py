# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  datasets.py
@Time    :  2022/5/30 1:35 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import operator

from collections import Counter
from functools import reduce
from typing import Dict, Tuple


def add_dicts(*args: Tuple[Dict, ...]) -> Dict:
    """
    Adds two or more dicts together. Common keys will have their values added.

    Returns:
    Example:
        >>> t1 = {'a':1, 'b':2}
        >>> t2 = {'b':1, 'c':3}
        >>> t3 = {'d':5}
        >>> add_dicts(t1, t2, t3)
        {'a': 1, 'c': 3, 'b': 3, 'd': 5}
    """

    counters = [Counter(arg) for arg in args]
    return dict(reduce(operator.add, counters))
