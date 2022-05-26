# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  context.py
@Time    :  2022/5/27 1:26 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import traceback


class ExcContextManager:
    def __init__(self, verbose=100, donot_raise__exception=True):
        """
        用上下文管理器捕获异常，可对代码片段进行错误捕捉，比装饰器更细腻
        Args:
            verbose: 打印错误的深度,对应traceback对象的limit，为正整数
            donot_raise__exception: 打印错误的深度,对应traceback对象的limit，为正整数
        """
        self._verbose = verbose
        self._donot_raise__exception = donot_raise__exception

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        exc_str = str(exc_type) + '  :  ' + str(exc_val)
        exc_str_color = '\033[0;30;45m%s\033[0m' % exc_str
        if self._donot_raise__exception:
            if exc_tb is not None:
                msg = f'\n'.join(traceback.format_tb(exc_tb)[:self._verbose]) + exc_str_color
                print(msg)
        return self._donot_raise__exception  # __exit__方法必须retuen True才会不重新抛出错误
