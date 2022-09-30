# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  __init__.py
@Time    :  2022/5/27 12:09 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from six import text_type

from .decode import unidecode
from .factory import MockHelper
from .kerberos import Kerberos
from .processor import DataHand, HtmlHand, JsonHand
from .regular import RegEx
from .snowflake import generator
from .system import System
from .useragent import firefox, safari, internet_explorer, opera
from .xprint import xprint
