# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  swagger_online_change.py
@Time    :  2022/7/18 10:16
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import json

import custard

url = 'http://xxxx/doctor-api/swagger/doc.json'

swagger = custard.swagger_parse(url)

print('转换接口：{}个'.format(len(swagger.apis)))

api_path = 'doctor-api.json'
with open(api_path, mode='w', encoding='utf8') as f:
    f.write(json.dumps(swagger.apis, indent=4, ensure_ascii=False))
