# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  number.py
@Time    :  2022/9/30 6:55 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from random import randint, uniform


def clamp(number, lower, upper):
    """Clamps number within the inclusive lower and upper bounds

    Arguments:
        number {number]} -- The number to clamp
        lower {[number} -- The lower bound
        upper {[number} -- The upper bound

    Returns:
        (number) -- Returns the clamped number
    """
    if is_clamp(number, lower, upper):
        return number
    if is_clamp(lower, number, upper):
        return lower
    if is_clamp(upper, number, lower):
        return upper


def is_clamp(number, lower, upper):
    """Check clamp number within the inclusive lower and upper bounds

    Arguments:
        number {number} -- The number to clamp
        lower {number} -- The lower bound
        upper {number} -- The upper bound

    Returns:
        (bool) -- Returns number is clamp or not
    """
    return is_between(lower, number, upper) or is_between(upper, number, lower)


def is_between(a, b, c):
    """Check a number is between two other numbers

    Arguments:
        a {number} -- The first number
        b {number} -- The second number
        c {number} -- The third number

    Returns:
        (bool) -- Return True if number is between else False
    """
    return a <= b <= c


def in_range(number, start, end=None):
    """Checks if n is between start and up to, but not including, end. If end is not specified, it's set to start with start then set to 0. If start is greater than end the params are swapped to support negative ranges.

    Arguments:
        number {number} -- The number to check
        start {number} -- The start of the range

    Keyword Arguments:
        end {*} -- The end of the range. (default: {None})

    Returns:
        (boolean) -- Returns True if number is in the range, else False
    """
    if (end == None):
        end = start
        start = 0

    return basein_range(number, start, end)


def basein_range(number, start, end):
    """Check number is between range

    Arguments:
        number {number} -- The number to check
        start {number} -- The number start of range
        end {number} -- The number end of range

    Returns:
        (boolean) -- Returns True if number is between of range
    """
    return min(start, end) <= number < max(start, end)


def random(lower=0, upper=1, floating=False):
    """Produces a random number between the inclusive lower and upper bounds. If only one argument is provided a number between 0 and the given number is returned. If floating is true, or either lower or upper are floats, a floating-point number is returned instead of an integer.

    Keyword Arguments:
        lower {int} -- The lower bound (default: {0})
        upper {int} -- The upper bound (default: {1})
        floating {bool} -- Specify returning a floating-point number (default: {False})

    Returns:
        (number) -- Returns the random number
    """
    floating = (isinstance(lower, float) or
                isinstance(upper, float) or
                floating is True or
                upper is True)
    if upper < lower:
        upper, lower = lower, upper

    if floating:
        rnd = uniform(lower, upper)
    else:
        rnd = randint(lower, upper)

    return rnd
