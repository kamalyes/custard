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
import codecs
import os
import typing
from json import JSONEncoder

from ..mock import mini_racer

MiniRacer = mini_racer.MiniRacer


class Mock:
    def __init__(self):
        self.__code = codecs.open(os.path.join(os.path.dirname(__file__), "mock.min.js"), encoding="utf-8").read()
        self.__ctx = MiniRacer()
        self.__ctx.eval(self.__code)

    def mock(
        self,
        template: typing.Union[dict, list, str],
        encoder=JSONEncoder,
        timeout=0,
        max_memory=0,
    ) -> typing.Union[dict, list, str]:
        """
        Mock from python object
        :param template: Mock template
        :param encoder: You can pass a custom JSON encoder by passing it in the encoder
        :param timeout: Limit run timeout, default no limit: timeout = 0(millisecond)
        :param max_memory: Limit max memory, default no limit: max_memory = 0
        :return: dict, list, str
        """
        return self.__ctx.call("Mock.mock", template, encoder=encoder, timeout=timeout, max_memory=max_memory)

    def mock_js(self, js_str: str, timeout=0, max_memory=0) -> typing.Union[dict, list, str]:
        """
        Mock form JSON string or JavaScript Object like-string
        :param js_str: Mock template
        :param timeout: Limit run timeout, default no limit: timeout = 0(millisecond)
        :param max_memory: Limit max memory, default no limit: max_memory = 0
        :return: dict, list, str
        """
        js = "Mock.mock({template})".format(template=js_str)
        return self.__ctx.eval(js, timeout, max_memory)


mocker = Mock()
