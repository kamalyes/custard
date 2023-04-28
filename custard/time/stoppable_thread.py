# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  stoppable_thread.py
@Time    :  2022/5/15 10:37 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import contextlib
import ctypes
import os
import threading

__all__ = ("StoppableThread", "JoinThread")


class StoppableThread(threading.Thread):
    def stop_thread(self, exception, repeat_every=2.0):
        if self.is_alive() is False:
            return True

        self._stderr = open(os.devnull, "w")

        join_thread = JoinThread(self, exception, repeat_every=repeat_every)
        join_thread._stderr = self._stderr
        join_thread.start()
        join_thread._stderr = self._stderr
        return None

    def stop(self, exception, repeat_every=2.0):
        return self.stop_thread(exception, repeat_every)


class JoinThread(threading.Thread):
    def __init__(self, other_thread, exception, repeat_every=2.0):
        threading.Thread.__init__(self)
        self.other_thread = other_thread
        self.exception = exception
        self.repeat_every = repeat_every
        self.daemon = True

    def run(self):
        self.other_thread._Thread__stderr = self._stderr
        if hasattr(self.other_thread, "_thread__stop"):
            self.other_thread._thread__stop()
        while self.other_thread.is_alive():
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(self.other_thread.ident),
                ctypes.py_object(self.exception),
            )
            self.other_thread.join(self.repeat_every)

        with contextlib.suppress(Exception):
            self._stderr.close()
