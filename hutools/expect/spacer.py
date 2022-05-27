# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  spacer.py
@Time    :  2021/10/22 20:16
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  间断器
"""
import threading
import time
import traceback
from functools import wraps


def keep_circulating(time_sleep=0.001, exit_if_function_run_succeed=True, is_display_detail_exception=True,
                     block=True, daemon=False, logger=None):
    """
    间隔一段时间，一直循环运行某个方法的装饰器
    Args:
        time_sleep: 循环的间隔时间
        exit_if_function_run_succeed: 如果成功了就退出循环
        is_display_detail_exception:  是否显示细节异常
        block: 是否阻塞主主线程，False时候开启一个新的线程运行while 1。
        daemon: 如果使用线程，那么是否使用守护线程，使这个while 1有机会自动结束。
        logger:
    Returns:
    Examples:
        >>> @keep_circulating(3, block=False)
        ... def test_keep_circulating(index = 0):
        ...     if isinstance(index, str):
        ...        pass
        ...     else:
        ...         for index in range(5):
        ...             if index <2:
        ...                 print("每隔3秒，一直打印   " + time.strftime('%H:%M:%S'))
        ...             else:
        ...                 test_keep_circulating(index="test")
        ...             index += 1
        >>> test_keep_circulating()
    """

    def _keep_circulating(func):
        @wraps(func)
        def __keep_circulating(*args, **kwargs):

            def ___keep_circulating():
                while 1:
                    try:
                        result = func(*args, **kwargs)
                        if exit_if_function_run_succeed:
                            return result
                    except Exception as e:
                        msg = func.__name__ + '   运行出错\n ' + traceback.format_exc(
                            limit=10) if is_display_detail_exception else str(e)
                        if logger:
                            logger.info(msg)
                        else:
                            print(msg)
                    finally:
                        time.sleep(time_sleep)

            if block:
                return ___keep_circulating()
            else:
                threading.Thread(target=___keep_circulating, daemon=daemon).start()

        return __keep_circulating

    return _keep_circulating
