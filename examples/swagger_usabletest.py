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
import threading
import unittest
import warnings
from urllib import parse
import requests
from custard.swagger import utils, swagger_parse
from custard.core.factory import MsHelper
from simplejson import JSONDecodeError
from custard.time import TimerContextManager, calc_time


class APITestCase(unittest.TestCase):
    default_file = './file.txt'
    result_path = 'result/接口鉴权报告'

    @classmethod
    def setUpClass(cls, run_host=None):
        warnings.simplefilter('ignore', ResourceWarning)
        # 准备测试资源
        if not os.path.exists(cls.default_file):
            with open(cls.default_file, mode='w') as f:
                f.write('Hello world!')
        if not os.path.exists(cls.result_path):
          os.makedirs(cls.result_path)
        cls.run_host = run_host
        cls.swagger_host = "https://localhost:7777"
        cls.swagger_path = "/swagger/doc.json"
        cls.service_list = ["order-api", "product-api", "customer-api", "pay_echo", "mall", "personalized-api", "boss"]

    @classmethod
    def tearDownClass(cls):
        # 清理测试资源
        if os.path.exists(cls.default_file):
            os.remove(cls.default_file)

    @classmethod
    @calc_time()
    def init_env(cls, service):
        """
        初始化环境 (解析swagger、创建md报告)
        Args:
            service: 服务名称
        """
        alias = "服务全量接口鉴权扫描"
        file_name = os.path.join(cls.result_path, f"{service}-{alias}.md")
        swagger_url = f"{parse.urljoin(cls.swagger_host,service)}{cls.swagger_path}"
        print(f'start {service} threads')
        try:
          swagger_data = swagger_parse(swagger_url, verify=False)
        except JSONDecodeError as json_dc_err:
          raise Warning(f"请检查Swagger地址: {swagger_url}是否正确")
        else:
          with open(file_name, "w", encoding="utf-8") as file:
              table_title = f"# {service}{alias}\n"
              table_header = f"|url|method|status_code|headers|params|json|response_text|\n"
              table_style = f"|:------:|:------:|:------:|:------:|:------:|:------:|:------:|\n"
              file.write(f"{table_title}{table_header}{table_style}")
        return file_name, swagger_data
          
    @classmethod
    def thread_scan_api(cls, request, file_name, semaphore):
        """
        给主进程加锁
        Args:
            request: 请求数据
            file_name: 文件名
            semaphore: 进程号
        """
        semaphore.acquire()  # 加锁
        with open(file_name, "a+", encoding="utf-8") as file:
          url = request.get('url')  # 请求地址
          if cls.run_host is not None:
            path = parse.urlparse(url)
            url = cls.run_host + path.path
          method = request.get('method')  # 请求方法
          headers = request.get('headers')  # 请求头
          paths = request.get('paths')  # 路径参数
          params = request.get('query')  # 查询字串，即query string
          # 普通表单，即 Content-Type = application/x-www-form-urlencoded
          data = request.get('form')
          # 文件表单, 即 Content-Type = multipart/form-data
          formData = request.get('formData')
          # json格式的参数, 即 Content-Type = application/json
          payload = request.get('json')
          payload = MsHelper.__property__(payload)
          # 文件上传时建议用requests框架的请求头
          if headers.get('Content-Type') == 'multipart/form-data':
              del headers['Content-Type']
          # 路径参数格式化
          url = utils.path_format(url, paths)
          # 文件表单参数格式化
          formData = utils.form_format(formData, cls.default_file)
          with open(file_name, "a+", encoding="utf-8") as file:
            try:
              # with TimerContextManager(is_print_log=True):
              res = requests.request(method=method,
                                    url=url,
                                    headers=headers,
                                    params=params,
                                    data=data,
                                    files=formData,
                                    json=payload,
                                    timeout=1,
                                    verify=False)
            except Exception as e:
              result = f'|`{url}`|`{method}`|`超时`|`{headers}`|`{params}`|`{payload}`|`<title>{str(e)[20:-30]}</title>`|'
            else:
              res_status_code = res.status_code
              res_text = str(res.text).strip()
              global_res_data = f'|`{url}`|`{method}`|`{res_status_code}`|`{headers}`|`{params}`|`{payload}`|'
              if res_status_code == 404:
                result = f'{global_res_data}`<title>404 Not Found</title>`|\n'
              else:
                if len(res_text) > 150 and res_status_code == 200:
                  curtail_length = 50
                  start = res_text[:curtail_length]
                  omit_length = len(res_text) - (curtail_length)
                  result = f'{global_res_data}`{start}....此处省略{omit_length}个字节.....`|\n'
                else:
                  result = f'{global_res_data}`{res_text}`|\n'
              file.write(result)
        semaphore.release()  # 释放
        
    def test_run(self):
      for service in self.service_list:  # 事件数
        file_name, swagger_data = self.init_env(service)
        requests_ = swagger_data.apis
        max_thread_ = lambda x: x if x<2000 else 2000
        thread_num = max_thread_(len(requests_))
        print(f"{service} total number of service apis: {len(requests_)}, thread_num: {thread_num}")
        for request in requests_:
          semaphore = threading.BoundedSemaphore(thread_num)  # 最多允许n个线程同时运行
          t = threading.Thread(target=self.thread_scan_api, args=(request, file_name, semaphore))
          t.start()
        while threading.active_count() != 1:
            pass
        else:
            print(f'----------{service} threads done-----------')

if __name__ == '__main__':
    unittest.main()
