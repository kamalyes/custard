# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  maths.py
@Time    :  2022/9/30 6:55 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import math

import utilities as helpers


def add(augend, addend):
    """Adds two numbers

    Arguments:
        augend {number} -- The first number in an addition
        addend {number} -- The second number in an addition

    Returns:
        (number) -- Returns the total
    """
    return augend + addend if helpers.is_number(augend) and helpers.is_number(addend) else str(
        augend) + str(addend)


def ceil(number, precision=0):
    """Computes number rounded up to precision

    Arguments:
        number {number} -- The number to round up

    Keyword Arguments:
        precision {int} -- The precision to round up to (default: {0})

    Returns:
        (number) -- Returns the rounded up number
    """
    return call_math_operator(number, precision, math.ceil)


def divide(dividend, divisor):
    """Divide two numbers

    Arguments:
        dividend {number]} -- The first number in a division
        divisor {[number} -- The second number in a division

    Returns:
        (number) -- Returns the quotient
    """
    try:
        return dividend / divisor
    except Exception:
        pass


def call_math_operator(number, precision=0, op=None):
    """Computes numbers ceil or floor base on operator

    Arguments:
        number {number} -- The number to round

    Keyword Arguments:
        precision {int} -- The precision to round (default: {0})
        op {*} -- The operator to round (default: {None})

    Returns:
        (number) -- Returns the rounded number
    """
    try:
        multiplier = 10 ** precision
        return op(number * multiplier) / multiplier
    except Exception:
        print('Number or precision must be a number')


def floor(number, precision=0):
    """Computes number rounded down to precision.

    Arguments:
        number {number} -- The number to round down

    Keyword Arguments:
        precision {number} -- The precision to round down to (default: {0})

    Returns:
        (number) -- Returns the rounded down number.
    """
    return call_math_operator(number, precision, math.floor)


def max(array):
    """Computes the maximum value of array. If array is empty or falsey, undefined is returned

    Arguments:
        array {list} -- The array to iterate over

    Returns:
        (*) -- Returns the maximum value
    """
    if len(array) == 0:
        return None

    max = 0
    for item in array:
        if item > max:
            max = item

    return max


def mean(array):
    """Computes the mean of the values in array

    Arguments:
        array {list} -- The array to iterate over

    Returns:
        (number) -- Returns the mean
    """
    try:
        return sum(array) / len(array)
    except ZeroDivisionError as detail:
        print(f'Handle run-time error: {detail}')


def min(array):
    """Computes the minimum value of array. If array is empty or falsey, undefined is returned

    Arguments:
        array {list} -- The array to iterate over

    Returns:
        (*) -- Returns the minimum value
    """
    if len(array) == 0:
        return None

    min = array[0]
    for item in array:
        if item < min:
            min = item

    return min


def multiply(multiplier, multiplicand):
    """Multiply two numbers

    Arguments:
        multiplier {number} --  The first number in a multiplication.
        multiplicand {number} -- The second number in a multiplication

    Returns:
        (number) -- Returns the product
    """
    return multiplier * multiplicand


def substract(minuend, subtrahend):
    """Subtract two numbers

    Arguments:
        minuend {number} -- The first number in a subtraction
        subtrahend {number} -- The second number in a subtraction

    Returns:
        (number) -- Returns the difference
    """
    return minuend - subtrahend


def sum(array):
    """Computes the sum of the values in array

    Arguments:
        array {list} -- The array to iterate over

    Returns:
        (number) -- Returns the sum
    """
    result = 0
    for i in array:
        result += i

    return result
