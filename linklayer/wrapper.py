# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  wrapper.py
@Time    :  2021/7/5 11:37 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  语法糖（装饰器模块）
"""
import json
import sys
import threading
import time
import traceback
import unittest
from functools import wraps


def run_many_times(times=1):
    """
    把函数运行times次的装饰器
    Args:
        times: 运行次数
    Returns: 没有捕获错误，出错误就中断运行，可以配合handle_exception装饰器不管是否错误都运行n次。
    Example::
        >>> @run_many_times(5)
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
                print(msg)
                func(*args, **kwargs)

        return __run_many_times

    return _run_many_times


def handle_exception(retry_times=0, error_detail_level=0, is_throw_error=False, time_sleep=0):
    """
    捕获函数错误的装饰器,重试并打印日志
    Args:
        retry_times: 重试次数
        error_detail_level: 为0打印exception提示，为1打印3层深度的错误堆栈，为2打印所有深度层次的错误堆栈
        is_throw_error: 在达到最大次数时候是否重新抛出错误
        time_sleep: 休眠时间
    Returns:
    Example::
        >>> @run_many_times(3)
        ... @handle_exception(2, 1)
        ... def test_superposition():
        ...    import json
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
                    print(err_msg)
                    if i == retry_times and is_throw_error:  # 达到最大错误次数后，重新抛出错误
                        raise e
                time.sleep(time_sleep)

        return __handle_exception

    return _handle_exception


def keep_circulating(time_sleep=0.001, exit_if_function_run_succeed=True, is_display_detail_exception=True,
                     block=True, daemon=False):
    """
    间隔一段时间，一直循环运行某个方法的装饰器
    Args:
        time_sleep: 循环的间隔时间
        exit_if_function_run_succeed: 如果成功了就退出循环
        is_display_detail_exception:  是否显示细节异常
        block: 是否阻塞主主线程，False时候开启一个新的线程运行while 1。
        daemon: 如果使用线程，那么是否使用守护线程，使这个while 1有机会自动结束。
    Returns:
    Example::
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
                        print(msg)
                    finally:
                        time.sleep(time_sleep)

            if block:
                return ___keep_circulating()
            else:
                threading.Thread(target=___keep_circulating, daemon=daemon).start()

        return __keep_circulating

    return _keep_circulating


def count_time(model):
    """
    给目标函数加上计算运行时间统计
    :param model:
    :return:
    Example::
        >>> @count_time("（自定义模块名）")
        ... def test_count_time(num=100):
        ...     return sum([x for x in range(num + 1)])
        >>> test_count_time(5)
    """

    def _count_time(func):
        @wraps(func)
        def __count_time(*args, **kwargs):
            start_time = time.time()
            # 定义result接收函数返回值，并且在装饰函数最后返回回去
            resutl = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            if elapsed_time < 3:
                msg = ("%s-总耗时：%s(正常范围内)" % (model, elapsed_time))
            elif elapsed_time > 5 and elapsed_time < 15:
                msg = ("%s-总耗时：%s(需要注意)" % (model, elapsed_time))
            else:
                msg = ("%s-总耗时：%s(超时)" % (model, elapsed_time))
            print(msg)
            return resutl

        return __count_time

    return _count_time


def synchronized(func):
    """
    线程锁装饰器，可以加在单例模式上
    Args:
        func:
    Returns:
    """
    func.__lock__ = threading.Lock()

    @wraps(func)
    def lock_func(*args, **kwargs):
        with func.__lock__:
            return func(*args, **kwargs)

    return lock_func


def singleton(cls):
    """
    单例模式装饰器,新加入线程锁，更牢固的单例模式，主要解决多线程如100线程同时实例化情况下可能会出现三例四例的情况,实测。
    Args:
        cls:
    Returns:
    """
    _instance = {}
    singleton.__lock = threading.Lock()

    @wraps(cls)
    def _singleton(*args, **kwargs):
        with singleton.__lock:
            if cls not in _instance:
                _instance[cls] = cls(*args, **kwargs)
            return _instance[cls]

    return _singleton


class ExceptionContextManager:
    """
    用上下文管理器捕获异常，可对代码片段进行错误捕捉，比装饰器更细腻
    """

    def __init__(self, verbose=100, donot_raise__exception=True):
        """

        Args:
            verbose: 打印错误的深度,对应traceback对象的limit，为正整数
            donot_raise__exception: 打印错误的深度,对应traceback对象的limit，为正整数
        """
        self._verbose = verbose
        self._donot_raise__exception = donot_raise__exception

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # print(exc_val)
        # print(traceback.format_exc())
        exc_str = str(exc_type) + '  :  ' + str(exc_val)
        exc_str_color = '\033[0;30;45m%s\033[0m' % exc_str
        if self._donot_raise__exception:
            if exc_tb is not None:
                msg = f'\n'.join(traceback.format_tb(exc_tb)[:self._verbose]) + exc_str_color
                print(msg)
        return self._donot_raise__exception  # __exit__方法必须retuen True才会不重新抛出错误


class TimerContextManager(object):
    """
    用上下文管理器计时，可对代码片段计时
    """

    def __init__(self, is_print_log=True):
        self._is_print_log = is_print_log
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
            print(msg)


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
            t0 = time.time()
            result = func(*args, **kwargs)
            result_raw = result
            t_spend = round(time.time() - t0, 2)
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


class _Test(unittest.TestCase):
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
    def test_timer_context(self):
        """
        测试上下文，对代码片段进行计时
        """
        with TimerContextManager(is_print_log=True):
            print('测试这里面的代码片段的时间。')
            time.sleep(2)

    @unittest.skip
    def test_exception_context_manager(self):
        def f1():
            1 + '2'

        def run():
            f1()

        with ExceptionContextManager() as ec:
            run()

    @unittest.skip
    def test_superposition(self):
        """测试多次运行和异常重试,测试装饰器叠加"""

        @run_many_times(3)
        @handle_exception(2, 1)
        def f():
            import json
            json.loads('a', ac='ds')

        f()

    @unittest.skip
    def test_handle_exception(self):
        """测试异常重试装饰器"""
        import requests

        @handle_exception(2)
        def f3():
            pass
            requests.get('dsdsdsd')

        f3()

    @unittest.skip
    def test_run_many_times(self):
        """测试运行5次"""

        @run_many_times(5)
        def f1():
            print('hello')
            time.sleep(1)

        f1()

    @unittest.skip
    def test_singleton(self):
        """测试单例模式的装饰器"""

        @singleton
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

    def test_count_time(self):
        @count_time("（自定义模块名）")
        def add(num=100):
            """
            计算 0~num 累加值，默认num=100
            """
            time.sleep(1)
            return sum([x for x in range(num + 1)])

        add(5)


if __name__ == '__main__':
    unittest.main()
