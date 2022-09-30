# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  arrays.py
@Time    :  2022/9/30 6:55 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import utilities as helper


def chunk(array, size=1):
    """Creates an array of elements split into groups the length of size. If array can't be split evenly, the final chunk will be the remaining elements.

    Arguments:
        array {list} -- The array to process

    Keyword Arguments:
        size {int} -- The length of each chunk (default: {1})

    Returns:
        (list) -- Returns the new array of chunks.
    """
    result = []

    if helper.is_number(size) is not True or len(array) == 0:
        return result
    elif size >= len(array):
        result.append(array)
    else:
        result = append_list(array, size, result)

    return result


def append_list(array, size, result):
    """Creates an arrays with small array inside

    Arguments:
        array {list} -- The array to process
        size {int} -- The length of each chunk
        result {type} -- New arrays of chunks

    Returns:
        (list) -- Returns the new array of chunks
    """
    # condition to stop recusion
    if len(array) == 0:
        return result
    else:
        temp = array[0: size]
        result.append(temp)
        # remove each temp array in primary array
        new_array = list(set(array) - set(temp))

        append_list(new_array, size, result)

    return result


def compact(array):
    """Creates an array with all falsey values removed. The values False, None, and "" are falsey.

    Arguments:
        array {list} -- The array to compact.

    Returns:
        (list) -- Returns the new array of filtered values.
    """
    return [i for i in array if i not in [False, None, '']]


def difference(array, values):
    """Creates an array of array values not included in the other given arrays using SameValueZero for equality comparisons. The order and references of result values are determined by the first array.

    Arguments:
        array {list} -- The array to inspect.
        values {list} -- The values to exclude.

    Returns:
        (list) -- Returns the new array of filtered values.
    """
    return list(set(array) - set(values))


def drop(array, number=1):
    """Creates a slice of array with n elements dropped from the beginning.

    Arguments:
        array {list} -- The array to query.

    Keyword Arguments:
        number {int} -- The number of elements to drop. (default: {1})

    Returns:
        (list) -- Returns the slice of array.
    """
    return array[number: len(array)] if helper.is_number(number) else array


def drop_right(array, number=1):
    """Creates a slice of array with n elements dropped from the end.

    Arguments:
        array {list} -- The array to query.

    Keyword Arguments:
        number {int} -- The number of elements to drop. (default: {1})

    Returns:
        (list) -- Returns the slice of array.
    """
    if helper.is_number(number) is True and len(array) < number:
        return []
    return array[0: len(array) - number] if helper.is_number(number) else array


def fill(array, value, start=0, end=None):
    """Fills elements of array with value from start up to, but not including, end.

    Arguments:
        array {list} -- The array to fill.
        value {*} -- The value to fill array with.

    Keyword Arguments:
        start {int} -- The start position. (default: {0})
        end {*} -- The end position. (default: {None})

    Returns:
        (list) -- Returns array
    """
    if helper.is_number(start):
        if end is None:
            end = len(array)

        if helper.is_number(end):
            for index, _ in enumerate(array):
                if index >= start and index < end:
                    array[index] = value
        else:
            return array
    return array


def index_of(array, value=None, fromIndex=0):
    """Gets the index at which the first occurrence of value is found in array using SameValueZero for equality comparisons. If fromIndex is negative, it's used as the offset from the end of array.

    Arguments:
        array {list} -- The array to inspect

    Keyword Arguments:
        value {*} -- The value to search for (default: {None})
        fromIndex {int} -- The index to search from (default: {0})

    Returns:
        (number) -- Returns the index of the matched value, else -1.
    """
    result = None
    fromIndex = fromIndex if helper.is_number(fromIndex) else 0
    for index, item in enumerate(array):
        if index >= fromIndex and item == value:
            result = index
            break

    return result if result is not None else -1


def initial(array):
    """Gets all but the last element of array

    Arguments:
        array {list} -- The array to query

    Returns:
        (list) -- Returns the slice of array
    """
    return [item for index, item in enumerate(array) if index != len(array) - 1] if isinstance(
        array, list) else []


def pull(array, *args):
    """Removes all given values from array using SameValueZero for equality comparisons

    Arguments:
        array {list} -- The array to modify
        [values](...*): -- The values to remove

    Returns:
        (list) -- Returns array
    """
    return [i for i in array if i not in args]
