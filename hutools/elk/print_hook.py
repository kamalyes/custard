# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@file    :  print_hook.py
@time    :  2021/8/5 5:21 pm
@author  :  YuYanQing
@version :  1.0
@contact :  mryu168@163.com
@license :  (c)copyright 2022-2026
@desc    :  不直接给print打补丁，自己重新赋值
"""

import multiprocessing
import sys
import time
import traceback
import elk_config_default

print_raw = print

WORD_COLOR = 37


def stdout_write(msg: str):
    sys.stdout.write(msg)
    sys.stdout.flush()


def stderr_write(msg: str):
    sys.stderr.write(msg)
    sys.stderr.flush()


def xprint(*args, sep=' ', end='\n', file=None, flush=True):
    """
    超流弊的print补丁
    Args:
        *args:
        sep:
        end:
        file:
        flush:
    Returns:
    """
    args = (str(arg) for arg in args)  # REMIND 防止是数字不能被join
    if file == sys.stderr:
        stderr_write(sep.join(args))  # 如 threading 模块第926行，打印线程错误，希望保持原始的红色错误方式，不希望转成蓝色。
    elif file in [sys.stdout, None]:
        # 获取被调用函数在被调用时所处代码行数
        line = sys._getframe().f_back.f_lineno
        # 获取被调用函数所在模块文件名
        file_name = sys._getframe(1).f_code.co_filename
        if elk_config_default.DEFAULT_USE_COLOR_HANDLER:
            if elk_config_default.DISPLAY_BACKGROUND_COLOR_IN_CONSOLE:
                stdout_write(
                    f'\033[0;34m{time.strftime("%H:%M:%S")}  "{file_name}:{line}"   '
                    f'\033[0;{WORD_COLOR};44m{sep.join(args)}\033[0m{end} \033[0m')  # 36  93 96 94
            else:
                stdout_write(
                    f'\033[0;{WORD_COLOR};34m{time.strftime("%H:%M:%S")}  "{file_name}:{line}"   '
                    f'{sep.join(args)} {end} \033[0m')  # 36  93 96 94
        else:
            stdout_write(
                f'{time.strftime("%H:%M:%S")}  "{file_name}:{line}"  '
                f' {sep.join(args)} {end}')  # 36  93 96 94
    else:
        print_raw(*args, sep=sep, end=end, file=file)


def print_exception(etype, value, tb, limit=None, file=None, chain=True):
    """
    避免每行有两个可跳转的，导致第二个可跳转的不被ide识别。
    主要是针对print_exception，logging.exception里面会调用这个函数。

    :param etype:
    :param value:
    :param tb:
    :param limit:
    :param file:
    :param chain:
    :return:
    """
    if file is None:
        file = sys.stderr
    for line in traceback.TracebackException(
            type(value), value, tb, limit=limit).format(chain=chain):
        # print(line, file=file, end="")
        if file != sys.stderr:
            stderr_write(f'{line} \n')
        else:
            stdout_write(f'{line} \n')


def patch_print():
    """
    Python有几个namespace，分别是locals/globals/builtin
    其中定义在函数内声明的变量属于locals，而模块内定义的函数属于globals。
    https://codeday.me/bug/20180929/266673.html   python – 为什么__builtins__既是模块又是dict
    :return:
    """
    try:
        __builtins__.print = xprint
    except AttributeError:
        __builtins__['print'] = xprint


def common_print(*args, sep=' ', end='\n', file=None):
    args = (str(arg) for arg in args)
    args = (str(arg) for arg in args)  # REMIND 防止是数字不能被join
    if file == sys.stderr:
        stderr_write(sep.join(args) + end)  # 如 threading 模块第926行，打印线程错误，希望保持原始的红色错误方式，不希望转成蓝色。
    else:
        stdout_write(sep.join(args) + end)


def reverse_patch_print():
    """
    提供一个反猴子补丁，恢复print原状
    :return:
    """

    try:
        __builtins__.print = print_raw
    except AttributeError:
        __builtins__['print'] = print_raw


def is_main_process():
    return multiprocessing.process.current_process().name == 'MainProcess'


def only_print_on_main_process(*args, sep=' ', end='\n', file=None, flush=True):
    # 获取被调用函数在被调用时所处代码行数
    if is_main_process():
        args = (str(arg) for arg in args)  # REMIND 防止是数字不能被join
        if file == sys.stderr:
            stderr_write(sep.join(args))  # 如 threading 模块第926行，打印线程错误，希望保持原始的红色错误方式，不希望转成蓝色。
        elif file in [sys.stdout, None]:
            # 获取被调用函数在被调用时所处代码行数
            line = sys._getframe().f_back.f_lineno
            # 获取被调用函数所在模块文件名
            file_name = sys._getframe(1).f_code.co_filename
            if elk_config_default.DEFAULT_USE_COLOR_HANDLER:
                if elk_config_default.DISPLAY_BACKGROUND_COLOR_IN_CONSOLE:
                    stdout_write(
                        f'\033[0;34m{time.strftime("%H:%M:%S")}  "{file_name}:{line}"   '
                        f'\033[0;{WORD_COLOR};44m{sep.join(args)}\033[0m{end} \033[0m')  # 36  93 96 94
                else:
                    stdout_write(
                        f'\033[0;{WORD_COLOR};34m{time.strftime("%H:%M:%S")}  '
                        f'"{file_name}:{line}"   {sep.join(args)} {end} \033[0m')  # 36  93 96 94
            else:
                stdout_write(
                    f'{time.strftime("%H:%M:%S")}  "{file_name}:{line}"   {sep.join(args)} {end}')  # 36  93 96 94
        else:
            print_raw(*args, sep=sep, end=end, file=file)


if __name__ == '__main__':
    print('before patch')
    patch_print()
    print(0)
    xprint(123, 'abc')
    print(456, 'def')
    print('http://www.baidu.com')

    reverse_patch_print()
    common_print('hi')

    try:
        1 / 0
    except Exception as e:
        xprint(e)
