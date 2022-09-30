# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  string.py
@Time    :  2022/9/30 6:55 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""


def is_number(s):
    """Check input is number or not

    Arguments:
        s {*} -- The input to check

    Returns:
        (boolean)] -- Returns True if input a number else False
    """
    try:
        int(s)
        return True
    except ValueError:
        return False
