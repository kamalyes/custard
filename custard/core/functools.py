# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  __init__.py
@Time    :  2022/5/27 12:09 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  常用装饰器
"""

import json
import logging
import sys
import threading
import time
import traceback
from functools import wraps

logger = logging.getLogger(__name__)


class ExcContextManager:
    def __init__(self, verbose=100, nr_exc=True):
        """
        用上下文管理器捕获异常,可对代码片段进行错误捕捉,比装饰器更细腻
        Args:
            verbose: 打印错误的深度,对应traceback对象的limit,为正整数
            nr_exc:
        """
        self._verbose = verbose
        self._nr_exc = nr_exc

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        exc_str = str(exc_type) + "  :  " + str(exc_val)
        exc_str_color = "\033[0;30;45m%s\033[0m" % exc_str
        if self._nr_exc and exc_tb is not None:
            msg = "\n".join(traceback.format_tb(exc_tb)[: self._verbose]) + exc_str_color
            print(msg)
        return self._nr_exc  # __exit__方法必须return True才会不重新抛出错误


def handle_exception(retry_times=0, error_detail_level=0, is_throw_error=False, time_sleep=0, opt_logger=False):
    """
    捕获函数错误的装饰器,重试并打印日志
    Args:
        retry_times: 重试次数
        error_detail_level: 为0打印exception提示,为1打印3层深度的错误堆栈,为2打印所有深度层次的错误堆栈
        is_throw_error: 在达到最大次数时候是否重新抛出错误
        time_sleep: 休眠时间
        opt_logger: 是否打印日志
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
        detail = "error_detail_level参数必须设置为0 、1 、2"
        raise Exception(detail)

    def _handle_exception(func):
        @wraps(func)
        def __handle_exception(*args, **kwargs):
            for i in range(0, retry_times + 1):
                try:
                    result = func(*args, **kwargs)
                    if i:
                        info_msg = f'{"# " * 40}\n调用成功,调用方法--> [  {func.__name__}  ] 第  {i + 1}  次重试成功'
                        logger.info(opt_logger, info_msg)
                    return result

                except Exception as e:
                    error_info = ""
                    if error_detail_level == 0:
                        error_info = "错误类型是:" + str(e.__class__) + "  " + str(e)
                    elif error_detail_level == 1:
                        error_info = "错误类型是:" + str(e.__class__) + "  " + traceback.format_exc(limit=3)
                    elif error_detail_level == 2:
                        error_info = "错误类型是:" + str(e.__class__) + "  " + traceback.format_exc()
                    err_msg = f'{"-" * 40}\n记录错误日志,调用方法--> [  {func.__name__}  ] 第  {i + 1}  次错误重试, {error_info}'
                    if opt_logger:
                        logger.error(err_msg)
                    if i == retry_times and is_throw_error:  # 达到最大错误次数后,重新抛出错误
                        raise e
                time.sleep(time_sleep)
            return None

        return __handle_exception

    return _handle_exception


def keep_circulating(
    time_sleep=0.001,
    exit_if_function_run_succeed=True,
    is_display_detail_exception=True,
    block=True,
    daemon=False,
    opt_logger=False,
):
    """
    间隔一段时间,一直循环运行某个方法的装饰器
    Args:
        time_sleep: 循环的间隔时间
        exit_if_function_run_succeed: 如果成功了就退出循环
        is_display_detail_exception:  是否显示细节异常
        block: 是否阻塞主主线程,False时候开启一个新的线程运行while 1。
        daemon: 如果使用线程,那么是否使用守护线程,使这个while 1有机会自动结束。
        opt_logger: 是否打印日志
    Returns:
    Examples:
        >>> @keep_circulating(3, block=False)
        ... def test_keep_circulating(index = 0):
        ...     if isinstance(index, str):
        ...        pass
        ...     else:
        ...         for index in range(5):
        ...             if index <2:
        ...                 print("每隔3秒,一直打印   " + time.strftime('%H:%M:%S'))
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
                        msg = (
                            func.__name__ + "   运行出错\n " + traceback.format_exc(limit=10)
                            if is_display_detail_exception
                            else str(e)
                        )
                        if opt_logger:
                            logger.info(msg)
                    finally:
                        time.sleep(time_sleep)
                return None

            if block:
                return ___keep_circulating()
            else:
                threading.Thread(target=___keep_circulating, daemon=daemon).start()
                return None

        return __keep_circulating

    return _keep_circulating


def where_is_it_called(func):
    """
    记录函数被什么文件的哪一行代码所调用,非常犀利黑科技的装饰器
    """

    @wraps(func)
    def _where_is_it_called(*args, **kwargs):
        # 获取被调用函数名称
        func_name = func.__name__
        # 什么函数调用了此函数
        which_fun_call_this = sys._getframe(1).f_code.co_name  # NOQA

        # 获取被调用函数在被调用时所处代码行数
        line = sys._getframe().f_back.f_lineno

        # 获取被调用函数所在模块文件名
        file_name = sys._getframe(1).f_code.co_filename

        msg = (
            f"文件[{func.__code__.co_filename}]的第[{func.__code__.co_firstlineno}]行"
            f"即模块 [{func.__module__}] 中的方法 [{func_name}] "
            f"正在被文件 [{file_name}] 中的方法 [{which_fun_call_this}] 中的"
            f"第 [{line}] 行处调用,传入的参数为[{args},{kwargs}]"
        )
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            result_raw = result
            t_spend = round(time.time() - start_time, 2)
            if isinstance(result, dict):
                result = json.dumps(result)
            if len(str(result)) > 200:
                result = str(result)[0:200]
            msg = "执行函数[{}]消耗的时间是{}秒,返回的结果是 --> ".format(func_name, t_spend) + str(result)
            print(msg)
            return result_raw
        except Exception as e:
            debug_msg = "执行函数{},发生错误".format(func_name)
            print(debug_msg, e)
            raise e

    return _where_is_it_called


def bind_run_many_times(times=1, opt_logger=False):
    """
    设置函数运行次数
    Args:
        times: 运行次数
        opt_logger: 日志开关
    Returns: 没有捕获错误,出错误就中断运行,可以配合handle_exception装饰器不管是否错误都运行n次。
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
                msg = "当前是第 {} 次运行[ {} ]函数".format(i + 1, func.__name__)
                if opt_logger:
                    logger.info(msg)
                func(*args, **kwargs)

        return __run_many_times

    return _run_many_times


class BatchTask:
    @staticmethod
    def list_jobs(func_name, context):
        """
        批量任务处理
        Args:
            func_name:
            context:
        Returns:
        Examples:
            >>> examples = [False, True, 1]
            >>> def test_status(**kwargs):
            ...     return kwargs["example"] is True
            >>> def test_list_jobs(example):
            ...     return  test_status(example=example)
            >>> BatchTask.list_jobs(test_list_jobs, examples)
        """
        accord, no_accord = [], []
        if not isinstance(context, list):
            context = [context]
        for index in context:
            if func_name.__call__(index):
                accord.append(index)
            else:
                no_accord.append(index)
        return True if no_accord == [] else (accord, no_accord)


def sync_redis_lock(key, client, lock_time_out, opt_logger=False):
    """
    redis分布式锁装饰器
    todo:锁的超时时间需要考虑任务函数执行时间,
    任务函数执行时间可能会越来越长,
    如果函数执行时间超出锁设置时间可能会存在执行多次情况
    redis命令
        以redis的key为锁名,value为超时时间
        get 获取对应key的value
        setnx 设置一个str类型.key存在不执行,返回0(受影响行数).key不存在插入一条数据,返回1
        gest 为一个str类型设置一个新的value并返回之前的value
    原理:
        设置锁:任务函数执行之前先设置锁,并添加超时时间(当前时间戳+超时时间),需要把任务执行时间考虑进去
        设置锁失败:查询锁的value是否小于当前时间,小于(锁还没超时),大于(锁超时)
        锁超时:(不可直接删除锁,如果多个进程都删除了锁,会同时获得锁),gest设置锁的新值(可能多个进程设置锁的新值,但只有一进程gest的返回值,小于当前时间戳,此进程才能执行任务)
    Args:
        key:
        client:
        lock_time_out:
        opt_logger:

    Returns:
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 当前时间
            now_time = int(time.time())
            # 获取并设置锁(value为当前时间+超时时间) 成功返回1,失败返回0
            lock = client.setnx(key, now_time + lock_time_out)
            if opt_logger:
                logger.info("Now Time: %s" % now_time, "lock: %s" % lock)
            if lock == 1:
                func(*args, **kwargs)
                if opt_logger:
                    logger.info("创建锁任务结束")
                client.delete(key)
                if opt_logger:
                    logger.info("删除锁任务结束")
            else:
                # 锁存在,查看锁是否超时
                lock_set_time = int(client.get(key))
                # 锁超时
                if now_time > lock_set_time:
                    # 重新设置锁(不能直接删除,可能出现多个进程同时检查到锁超时都获取到锁的情况)
                    # gest设置新值返回旧值
                    old_lock_time = int(client.gest(key, now_time + lock_time_out))
                    if opt_logger:
                        logger.info("old_lock_time", type(old_lock_time), old_lock_time)
                    # 如果目前时间小于旧锁时间,表示有别的进程获取到了锁.放弃执行任务,反之执行任务
                    if now_time > old_lock_time:
                        if opt_logger:
                            logger.info("锁超时开始任务")
                        func(*args, **kwargs)
                        if opt_logger:
                            logger.info("锁超时结束任务")
                        client.delete(key)
                        if opt_logger:
                            logger.info("锁超时删除锁")

            if opt_logger:
                logger.info("没有执行任务")

        return wrapper

    return decorator


def synchronized_lock(func):
    """
    线程锁装饰器,可以加在单例模式上
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


def singleton_lock(cls):
    """
    单例模式装饰器,新加入线程锁,更牢固的单例模式
    主要解决多线程如100线程同时实例化情况下可能会出现三例四例的情况,实测。
    Args:
        cls:
    Returns:
    """
    _instance = {}
    singleton_lock.__lock = threading.Lock()

    @wraps(cls)
    def _singleton(*args, **kwargs):
        with singleton_lock.__lock:
            if cls not in _instance:
                _instance[cls] = cls(*args, **kwargs)
            return _instance[cls]

    return _singleton
