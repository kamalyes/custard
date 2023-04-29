# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  xprint
@Time    :  2022/6/3 5:05 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import sys
import time

print_raw = print


def stdout_write(msg: str):
    sys.stdout.write(msg)
    sys.stdout.flush()


def stderr_write(msg: str):
    sys.stderr.write(msg)
    sys.stderr.flush()


def reverse_patch_print():
    """
    提供一个反猴子补丁,恢复print原状
    :return:
    """

    try:
        __builtins__.print = print_raw
    except AttributeError:
        __builtins__["print"] = print_raw


def xprint(*args, sep=" ", end="\n", file=None, color=True):
    """
    超流弊的print补丁
    Args:
        *args:
        sep:
        end:
        file:
        color:
    Returns:
    Examples:
        >>> xprint("123")
    """
    args = (str(arg) for arg in args)  # REMIND 防止是数字不能被join
    if file == sys.stderr:
        stderr_write(sep.join(args))  # 如 threading 模块第926行,打印线程错误,希望保持原始的红色错误方式,不希望转成蓝色。
    elif file in [sys.stdout, None]:
        # 获取被调用函数在被调用时所处代码行数
        line = sys._getframe().f_back.f_lineno
        # 获取被调用函数所在模块文件名
        file_name = sys._getframe(1).f_code.co_filename
        single_space = "\t"
        if color:
            stdout_write(
                f'\033[35m{time.strftime("%H:%M:%S")}{single_space}"{file_name}:{line}"{single_space}'
                f"{sep.join(args)}{single_space}{end}\033[0m",
            )
        else:
            stdout_write(f'{time.strftime("%H:%M:%S")}\t"{file_name}:{line}"{single_space}{sep.join(args)}{end}')
    else:
        print_raw(*args, sep=sep, end=end, file=file)
