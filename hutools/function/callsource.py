# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  callsource.py
@Time    :  2022/5/27 1:50 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import json
import sys
import time
from functools import wraps


def where_is_it_called(func):
    """一个装饰器，被装饰的函数，如果被调用，将记录一条日志,记录函数被什么文件的哪一行代码所调用，非常犀利黑科技的装饰器"""

    @wraps(func)
    def _where_is_it_called(*args, **kwargs):
        # 获取被调用函数名称
        # func_name = sys._getframe().f_code.co_name
        func_name = func.__name__
        # 什么函数调用了此函数
        which_fun_call_this = sys._getframe(1).f_code.co_name  # NOQA

        # 获取被调用函数在被调用时所处代码行数
        line = sys._getframe().f_back.f_lineno

        # 获取被调用函数所在模块文件名
        file_name = sys._getframe(1).f_code.co_filename

        msg = (
            f'文件[{func.__code__.co_filename}]的第[{func.__code__.co_firstlineno}]行'
            f'即模块 [{func.__module__}] 中的方法 [{func_name}] '
            f'正在被文件 [{file_name}] 中的方法 [{which_fun_call_this}] 中的'
            f'第 [{line}] 行处调用，传入的参数为[{args},{kwargs}]')
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            result_raw = result
            t_spend = round(time.time() - start_time, 2)
            if isinstance(result, dict):
                result = json.dumps(result)
            if len(str(result)) > 200:
                result = str(result)[0:200] + '  。。。。。。  '
            msg = ('执行函数[{}]消耗的时间是{}秒，返回的结果是 --> '.format(func_name, t_spend) + str(result))
            print(msg)
            return result_raw
        except Exception as e:
            debug_msg = ('执行函数{}，发生错误'.format(func_name))
            print(debug_msg, e)
            raise e

    return _where_is_it_called
