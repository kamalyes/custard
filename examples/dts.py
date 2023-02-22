# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  dts.py
@Time    :  2022/5/27 12:09 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""

from custard.db import MySqlInspect
from custard.db  import MysqlUtil

is_execute = True

source_schema = "dts"
source_url = "localhost"
source_user = "root"
source_password = "PassWord@Mysql123"
source_port = 3306

target_schema = "dts_bak"
target_url = "localhost"
target_user = "root"
target_password = "PassWord@Redis123"
target_port = 3306

sql_inspect = MySqlInspect(source_schema, source_url, source_user, source_password, source_port,
                           target_schema, target_url, target_user, target_password, target_port)
sql_util = MysqlUtil(source_schema, source_url, source_user, source_password, source_port)
sql_util.get_columns("pika_sensitive_word")
sql_inspect.inspect_table(is_execute)
