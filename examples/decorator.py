# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  decorator.py
@Time    :  2022/5/27 12:09 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""

import random
import time
import unittest

from custard.expect import ExcContextManager
from custard.expect.record import handle_exception
from custard.expect.spacer import keep_circulating
from custard.function import bind_run_many_times, where_is_it_called
from custard.lock import singleton_lock
from custard.time import TimerContextManager, calc_time, bind_timeout


class _Test(unittest.TestCase):

    @unittest.skip
    @bind_timeout(timeout=0.5)
    def test_not_time_out(self):
        print("未超出限定的时间测试")
        time.sleep(0.2)

    @unittest.skip
    @bind_timeout(timeout=0.5)
    def test_time_out(self):
        print("超出限定的时间测试")
        time.sleep(0.6)

    @unittest.skip
    @calc_time()
    def test_calc_time(self):
        print("计算耗时测试")
        time.sleep(random.randint(1, 5))

    @unittest.skip
    @bind_run_many_times(5)
    def test_bind_run_many_times(self):
        pass

    @unittest.skip
    def test_where_is_it_called(self):
        """测试函数被调用的装饰器，被调用2次将会记录2次被调用的日志"""

        @where_is_it_called
        def f9(a, b):
            result = a + b
            print(result)
            time.sleep(0.1)
            return result

        f9(1, 2)

    @unittest.skip
    def test_timerContext(self):
        """
        测试上下文，对代码片段进行计时
        """
        with TimerContextManager(is_print_log=True):
            print('测试这里面的代码片段的时间。')
            time.sleep(2)

    @unittest.skip
    def test_exception_context_manager(self):
        def func_():
            1 + '2'

        def run():
            func_()

        with ExcContextManager() as ec:
            run()

    @unittest.skip
    def test_superposition(self):
        """测试多次运行和异常重试,测试装饰器叠加"""

        @bind_run_many_times(3)
        @handle_exception(2, 1)
        def func_():
            import json
            json.loads('a', ac='ds')

        func_()

    @unittest.skip
    def test_handle_exception(self):
        """测试异常重试装饰器"""

        @handle_exception(2)
        def func_3():
            isinstance(5, "ERROR")

        func_3()

    @unittest.skip
    def test_run_many_times(self):
        """测试运行5次"""

        @bind_run_many_times(5)
        def func_():
            print('hello')
            time.sleep(1)

        func_()

    @unittest.skip
    def test_singleton(self):
        """测试单例模式的装饰器"""

        @singleton_lock
        class A(object):
            def __init__(self, x):
                self.x = x

        a1 = A(3)
        a2 = A(4)
        self.assertEqual(id(a1), id(a2))
        print(a1.x, a2.x)

    @unittest.skip
    def test_keep_circulating(self):
        """测试间隔时间，循环运行"""

        @keep_circulating(3, block=False)
        def f6():
            print("每隔3秒，一直打印   " + time.strftime('%H:%M:%S'))

        f6()
        print('test block')

    @unittest.skip
    def test_calc_time(self):
        @calc_time("（自定义模块名）")
        def add(num=100):
            """
            计算 0~num 累加值，默认num=100
            """
            time.sleep(1)
            return sum([x for x in range(num + 1)])

        add(5)


if __name__ == '__main__':
    unittest.main()
