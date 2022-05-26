# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  redis_lock.py
@Time    :  2022/5/15 10:37 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""

import functools
import time


def sync_redis_lock(key, client, lock_time_out):
    """
    redis分布式锁装饰器
    todo:锁的超时时间需要考虑任务函数执行时间,任务函数执行时间可能会越来越长,如果函数执行时间超出锁设置时间可能会存在执行多次情况
    redis命令
        以redis的key为锁名,value为超时时间
        get 获取对应key的value
        setnx 设置一个str类型.key存在不执行,返回0(受影响行数).key不存在插入一条数据,返回1
        getset 为一个str类型设置一个新的value并返回之前的value
    原理：
        设置锁：任务函数执行之前先设置锁,并添加超时时间(当前时间戳+超时时间),需要把任务执行时间考虑进去
        设置锁失败：查询锁的value是否小于当前时间,小于(锁还没超时),大于(锁超时)
        锁超时：(不可直接删除锁,如果多个进程都删除了锁,会同时获得锁),getset设置锁的新值(可能多个进程设置锁的新值,但只有一进程getset的返回值,小于当前时间戳,此进程才能执行任务)
    Args:
        key:
        client:
        lock_time_out:

    Returns:
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 当前时间
            now_time = int(time.time())
            print(now_time)
            # 获取并设置锁(value为当前时间+超时时间) 成功返回1,失败返回0
            lock = client.setnx(key, now_time + lock_time_out)
            print(lock)
            if lock == 1:
                func(*args, **kwargs)
                print('创建锁结束任务')
                client.delete(key)
                print('删除锁')
            else:
                # 锁存在,查看锁是否超时
                lock_set_time = int(client.get(key))
                # 锁超时
                if now_time > lock_set_time:
                    # 重新设置锁(不能直接删除,可能出现多个进程同时检查到锁超时都获取到锁的情况)
                    # getset设置新值返回旧值
                    old_lock_time = int(client.getset(key, now_time + lock_time_out))
                    print('old_lock_time', type(old_lock_time), old_lock_time)
                    # 如果目前时间小于旧锁时间,表示有别的进程获取到了锁.放弃执行任务,反之执行任务
                    if now_time > old_lock_time:
                        print('锁超时开始任务')
                        func(*args, **kwargs)
                        print('锁超时结束任务')
                        client.delete(key)
                        print('锁超时删除锁')
            print('没有执行任务')

        return wrapper

    return decorator
