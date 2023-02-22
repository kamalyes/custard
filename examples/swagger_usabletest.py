# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  swagger_usabletest.py
@Time    :  2022/7/18 11:55
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""

import os
import unittest
import warnings

import requests
import custard
from custard.swagger import utils


class APITestCase(unittest.TestCase):
    default_file = 'test_file.txt'

    @classmethod
    def setUpClass(cls):
        warnings.simplefilter('ignore', ResourceWarning)
        # 准备测试资源
        if not os.path.exists(cls.default_file):
            with open(cls.default_file, mode='w') as f:
                f.write('Hello world!')

        url = 'http://localhost/oss/swagger/doc.json'

        # cls.swagger = custard.swagger_parse(url, verify=False)
        cls.swagger = custard.swagger_parse(file="./doctor-api.json")

    @classmethod
    def tearDownClass(cls):
        # 清理测试资源
        if os.path.exists(cls.default_file):
            os.remove(cls.default_file)

    def test_apis(self):
        file_name = "aaa.md"
        with open (file_name, "w", encoding="utf-8") as file:
          file.write("url | method | headers | params | json | response_text\n|  :----:  | :----:  | :----:  | :----:  | :----:  |:----:  |\n")
        for api in self.swagger.apis:
            with self.subTest(api.get('name')) as st:
                try:
                    # 请求地址
                    url = api.get('url')
                    # 请求方法
                    method = api.get('method')
                    # 请求头
                    headers = api.get('headers')
                    # 路径参数
                    paths = api.get('paths')
                    # 查询字串，即query string
                    params = api.get('query')
                    # 普通表单，即 Content-Type = application/x-www-form-urlencoded
                    data = api.get('form')
                    # 文件表单, 即 Content-Type = multipart/form-data
                    formData = api.get('formData')

                    # json格式的参数, 即 Content-Type = application/json
                    payload = api.get('json')

                    # 文件上传时建议用requests框架的请求头
                    if headers.get('Content-Type') == 'multipart/form-data':
                        del headers['Content-Type']
                    # 路径参数格式化
                    url = utils.path_format(url, paths)

                    # 文件表单参数格式化
                    formData = utils.form_format(formData)

                    res = requests.request(method=method,
                                           url=url,
                                           headers=headers,
                                           params=params,
                                           data=data,
                                           files=formData,
                                           json=payload,
                                           timeout=1,
                                           verify=False)
                    self.assertTrue(res.ok)
                except Exception:
                  if 'Not Found' in res.text:
                    with open (file_name, "a+", encoding="utf-8") as file:
                      result = f'|{url} \t|\t  {method} \t|\t {headers} \t|\t {params} \t|\t {payload} \t|\t {res.text}|\n'
                      print(result)
                      file.write(result)


if __name__ == '__main__':
    unittest.main()
