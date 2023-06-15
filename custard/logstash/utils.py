# -*- coding:utf-8 -*-
# !/usr/bin/env python3
"""
@File    :  utils.py
@Time    :  2023/6/15 19:55
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from __future__ import print_function

from datetime import datetime
from importlib import import_module
from itertools import chain, islice
import sys
import traceback


# ----------------------------------------------------------------------
def ichunked(seq, chunk_size):
    """Yields items from an iterator in iterable chunks.
    https://stackoverflow.com/a/8998040
    """
    iterable = iter(seq)
    while True:
        chunk_iterable = islice(iterable, chunk_size)
        try:
            element = next(chunk_iterable)
        except StopIteration:
            return
        yield list(chain((element,), chunk_iterable))


# ----------------------------------------------------------------------
def safe_log_via_print(log_level, message, *args, **kwargs):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp}: {log_level}: {message}"
    print(log_message % args, file=sys.stderr)
    # print stack trace if available
    exc_info = kwargs.get("exc_info", None)
    if (exc_info or log_level == "exception") and not isinstance(exc_info, tuple):
        exc_info = sys.exc_info()
        stack_trace = "".join(traceback.format_exception(*exc_info))
        print(stack_trace, file=sys.stderr)


# ----------------------------------------------------------------------
def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.

    (stolen from Django)
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as exc:
        raise ImportError(f"{dotted_path} does not look like a module path") from exc

    module = import_module(module_path)
    try:
        return getattr(module, class_name)
    except AttributeError as exc:
        raise ImportError(f'Module "{module_path}" does not define a "{class_name}" attribute/class') from exc
