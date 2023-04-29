# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  exceptions.py
@Time    :  2022/5/15 10:37 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""

__all__ = ("FunctionTimedOut", "RETRY_SAME_TIMEOUT")

RETRY_SAME_TIMEOUT = "RETRY_SAME_TIMEOUT"


class TimeOutError(Exception):
    """
    An operation timed out
    """


class FunctionTimedOut(Exception):
    def __init__(
        self,
        msg="",
        timed_out_after=None,
        timed_out_function=None,
        timed_out_args=None,
        timed_out_kwargs=None,
    ):
        """
        Args:
            msg:
            timed_out_after:
            timed_out_function:
            timed_out_args:
            timed_out_kwargs:
        """
        self.timed_out_after = timed_out_after
        self.timed_out_function = timed_out_function
        self.timed_out_args = timed_out_args
        self.timed_out_kwargs = timed_out_kwargs

        if not msg:
            msg = self.get_msg()

        BaseException.__init__(self, msg)

        self.msg = msg

    def get_msg(self):
        if self.timed_out_function is not None:
            timed_out_func_name = self.timed_out_function.__name__
        else:
            timed_out_func_name = "Unknown Function"
        timed_out_after_str = "%f" % (self.timed_out_after,) if self.timed_out_after is not None else "Unknown"

        return "Function %s (args=%s) (kwargs=%s) timed out after %s seconds.\n" % (
            timed_out_func_name,
            repr(self.timed_out_args),
            repr(self.timed_out_kwargs),
            timed_out_after_str,
        )
