# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  traverse.py
@Time    :  2022/5/27 1:50 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from functools import wraps
from statistics import stdev, fmean as mean
from time import perf_counter


def bind_run_many_times(times=1, logger=None):
    """
    设置函数运行次数
    Args:
        times: 运行次数
        logger: 日志开关
    Returns: 没有捕获错误，出错误就中断运行，可以配合handle_exception装饰器不管是否错误都运行n次。
    Examples:
        >>> import time
        >>> @bind_run_many_times(5)
        ... def test_run_many_times_():
        ...     print('hello world!')
        ...     time.sleep(0.2)
        >>> test_run_many_times_()
    """

    def _run_many_times(func):
        @wraps(func)
        def __run_many_times(*args, **kwargs):
            for i in range(times):
                msg = '当前是第 {} 次运行[ {} ]函数'.format(i + 1, func.__name__)
                if logger:
                    logger.info(msg)
                else:
                    print(msg)
                func(*args, **kwargs)

        return __run_many_times

    return _run_many_times
