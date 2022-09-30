# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  useragent.py
@Time    :  2022/5/27 1:50 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from custard.core.useragent import (firefox, safari, internet_explorer, opera)
from custard.core.useragent import (linux_platform_token, mac_platform_token, win_platform_token,
                                    android_platform_token)

print(firefox())
print(safari())
print(internet_explorer())
print(opera())
print(linux_platform_token())
print(mac_platform_token())
print(win_platform_token())
print(android_platform_token())
