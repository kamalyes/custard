# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  utils.py
@Time    :  2022/7/18 10:16
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import re
import string


def path_format(url, params):
    t = string.Template(re.subn(r'{(\w+)}', r'${\1}', url)[0])
    return t.safe_substitute(params)


def form_format(data: dict):
    _data = dict()
    for k, v in data.items():
        if v == 'file.txt':
            v = (k, open('file.txt', mode='rb'))
        else:
            v = (None, v)
        _data.update({k: v})

    return _data
