# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  record.py
@Time    :  2022/5/15 10:37 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import time
import traceback
from functools import wraps


def args_to_str(*args, **kwargs):
    """
    args 转换为 str
    Args:
        *args:
        **kwargs:
    Returns:
    """
    str1 = ", ".join(str(i) for i in args)
    kv = []
    for k, v in kwargs.items():
        kv.append(f"{k}={v}")
    str2 = ", ".join(kv)
    if kwargs and args:
        return f"{str1}, {str2}"
    if args:
        return str1
    if kwargs:
        return str2
    return ''


def handle_exception(retry_times=0, error_detail_level=0, is_throw_error=False, time_sleep=0, logger=None):
    """
    捕获函数错误的装饰器,重试并打印日志
    Args:
        retry_times: 重试次数
        error_detail_level: 为0打印exception提示，为1打印3层深度的错误堆栈，为2打印所有深度层次的错误堆栈
        is_throw_error: 在达到最大次数时候是否重新抛出错误
        time_sleep: 休眠时间
        logger:
    Returns:
    Examples:
        >>> from custard.function import bind_run_many_times
        >>> import json
        >>> import time
        >>> @bind_run_many_times(3)
        ... @handle_exception(2, 1)
        ... def test_superposition():
        ...    json.loads('a', ac='ds')
        >>> test_superposition()

        >>> @handle_exception(2)
        ... def test_handle_exception():
        ...     pass
        >>> test_handle_exception()
    """
    if error_detail_level not in [0, 1, 2]:
        raise Exception('error_detail_level参数必须设置为0 、1 、2')

    def _handle_exception(func):
        @wraps(func)
        def __handle_exception(*args, **keyargs):
            for i in range(0, retry_times + 1):
                try:
                    result = func(*args, **keyargs)
                    if i:
                        info_msg = f'{"# " * 40}\n调用成功，调用方法--> [  {func.__name__}  ] 第  {i + 1}  次重试成功'
                        if logger:
                            logger.info(info_msg)
                        else:
                            print(info_msg)
                    return result

                except Exception as e:
                    error_info = ''
                    if error_detail_level == 0:
                        error_info = '错误类型是：' + str(e.__class__) + '  ' + str(e)
                    elif error_detail_level == 1:
                        error_info = '错误类型是：' + str(e.__class__) + '  ' + traceback.format_exc(limit=3)
                    elif error_detail_level == 2:
                        error_info = '错误类型是：' + str(e.__class__) + '  ' + traceback.format_exc()
                    err_msg = f'{"-" * 40}\n记录错误日志，调用方法--> [  {func.__name__}  ] 第  {i + 1}  次错误重试， {error_info}'
                    if logger:
                        logger.info(err_msg)
                    else:
                        print(err_msg)
                    if i == retry_times and is_throw_error:  # 达到最大错误次数后，重新抛出错误
                        raise e
                time.sleep(time_sleep)

        return __handle_exception

    return _handle_exception
