# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  thread_lock.py
@Time    :  2022/5/15 10:37 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import threading
from functools import wraps


def synchronized_lock(func):
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


def singleton_lock(cls):
    """
    单例模式装饰器,新加入线程锁，更牢固的单例模式，主要解决多线程如100线程同时实例化情况下可能会出现三例四例的情况,实测。
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
