# -*- coding:utf-8 -*-
# !/usr/bin/env python3
"""
@File    :  useragent.py
@Time    :  2022/5/27 1:50 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from custard.core.useragent import (
    android_platform_token,
    firefox,
    internet_explorer,
    linux_platform_token,
    mac_platform_token,
    opera,
    safari,
    win_platform_token,
)

print(firefox())
print(safari())
print(internet_explorer())
print(opera())
print(linux_platform_token())
print(mac_platform_token())
print(win_platform_token())
print(android_platform_token())
