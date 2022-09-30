# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  __init__.py
@Time    :  2022/9/30 6:55 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""

# arrays
from .arrays import (
    chunk,
    compact,
    difference,
    drop,
    drop_right,
    fill,
    index_of,
    initial,
    pull
)

# maths
from .maths import (
    add,
    ceil,
    divide,
    floor,
    max,
    mean,
    min,
    multiply,
    substract,
    sum
)

# number
from .number import (
    clamp,
    in_range,
    random
)

# string
from .string import (
    camel_case,
    capitalize,
    ends_with,
    escape,
    lower_case,
    lower_first,
    pad,
    pad_end,
    pad_start,
    repeat,
    replace,
    starts_with
)

# utilities
from .utilities import (
    is_number
)
