# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  dafunc.py
@Time    :  2022/5/15 10:37 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""

import copy
import sys
import time
import types
from functools import wraps
from typing import Any

from .exceptions import FunctionTimedOut
from .stoppable_thread import StoppableThread

__all__ = ("func_timeout", "bind_timeout", "calc_time", "FunctionTimedOut", "TimerContextManager", "StoppableThread")


def func_timeout(timeout, func, args=(), kwargs=None):
    """
    Args:
        timeout:
        func:
        args:
        kwargs:
    Returns:
    """
    if not kwargs:
        kwargs = {}
    if not args:
        args = ()

    ret = []
    exception = []
    is_stopped = False

    def funcwrap(args2, kwargs2):
        try:
            ret.append(func(*args2, **kwargs2))
        except FunctionTimedOut:
            pass
        except Exception as e:
            exc_info = sys.exc_info()
            if is_stopped is False:
                e.__traceback__ = exc_info[2].tb_next
                exception.append(e)

    thread = StoppableThread(target=funcwrap, args=(args, kwargs))
    thread.daemon = True

    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        is_stopped = True

        class FunctionTimedOutTempType(FunctionTimedOut):
            def __init__(self):
                return FunctionTimedOut.__init__(self, "", timeout, func, args, kwargs)

        stop_exception = type(
            "FunctionTimedOut" + str(hash("%d_%d_%d_%d" % (id(timeout), id(func), id(args), id(kwargs)))),
            FunctionTimedOutTempType.__bases__,
            dict(FunctionTimedOutTempType.__dict__),
        )
        thread.stop_thread(stop_exception)
        thread.join(min(0.1, timeout / 50.0))
        raise FunctionTimedOut("", timeout, func, args, kwargs)
    else:
        thread.join(0.5)

    if exception:
        raise exception[0] from None

    if ret:
        return ret[0]
    return None


def bind_timeout(timeout, allow_override=False):
    """
    Args:
        timeout:
        allow_override:
    Returns:
    """
    default_timeout = copy.copy(timeout)

    is_timeout_function = bool(
        issubclass(
            timeout.__class__,
            (
                types.FunctionType,
                types.MethodType,
                types.LambdaType,
                types.BuiltinFunctionType,
                types.BuiltinMethodType,
            ),
        ),
    )

    if not is_timeout_function and not issubclass(timeout.__class__, (float, int)):
        try:
            timeout = float(timeout)
        except ValueError:
            raise ValueError(
                " Passed type: < %s > is not of any of these, and cannot be converted to a float."
                % (timeout.__class__.__name__,),
            )

    if not allow_override and not is_timeout_function:

        def _function_decorator(func):
            return wraps(func)(lambda *args, **kwargs: func_timeout(default_timeout, func, args=args, kwargs=kwargs))

        return _function_decorator

    if not is_timeout_function:

        def _function_decorator(func):
            def _function_wrapper(*args, **kwargs):
                use_timeout = kwargs.pop("force_timeout") if "force_timeout" in kwargs else default_timeout

                return func_timeout(use_timeout, func, args=args, kwargs=kwargs)

            return wraps(func)(_function_wrapper)

        return _function_decorator

    timeout_function = timeout

    if allow_override:

        def _function_decorator(func):
            def _function_wrapper(*args, **kwargs):
                if "force_timeout" in kwargs:
                    use_timeout = kwargs.pop("force_timeout")
                else:
                    use_timeout = timeout_function(*args, **kwargs)

                return func_timeout(use_timeout, func, args=args, kwargs=kwargs)

            return wraps(func)(_function_wrapper)

        return _function_decorator

    def _function_decorator(func):
        def _function_wrapper(*args, **kwargs):
            use_timeout = timeout_function(*args, **kwargs)

            return func_timeout(use_timeout, func, args=args, kwargs=kwargs)

        return wraps(func)(_function_wrapper)

    return _function_decorator


class TimerContextManager(object):
    """
    用上下文管理器计时,可对代码片段计时
    """

    def __init__(self, is_print_log=True, logger=None):
        self._is_print_log = is_print_log
        self.logger = logger
        self.t_spend = None
        self._line = None
        self._file_name = None
        self.time_start = None

    def __enter__(self):
        self._line = sys._getframe().f_back.f_lineno  # 调用此方法的代码的函数
        self._file_name = sys._getframe(1).f_code.co_filename  # 哪个文件调了用此方法
        self.time_start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.t_spend = time.time() - self.time_start
        if self._is_print_log:
            msg = f'对下面代码片段进行计时:  \n执行"{self._file_name}:{self._line}" 用时 {round(self.t_spend, 2)} 秒'
            if self.logger:
                self.logger.info(msg)
            else:
                print(msg)


def calc_time(logger: Any = None):
    """
    统计给目标函数运行时间
    Args:
        logger:
    Returns:
    Examples:
        >>> @calc_time("(自定义模块名)")
        ... def test_calc_time(num=100):
        ...     return sum([x for x in range(num + 1)])
        >>> test_calc_time(5)
    """

    def _calc_time(func):
        @wraps(func)
        def __calc_time(*args, **kwargs):
            start_time = time.time()
            # 定义result接收函数返回值,并且在装饰函数最后返回回去
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            if logger:
                logger.info(f"{func.__name__} cost {elapsed_time:.4f} seconds")
            else:
                print(f"{func.__name__} cost {elapsed_time:.4f} seconds")
            return result

        return __calc_time

    return _calc_time
