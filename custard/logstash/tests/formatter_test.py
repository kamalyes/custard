# -*- coding:utf-8 -*-
# !/usr/bin/env python3
"""
@File    :  formatter_test.py
@Time    :  2023/6/15 19:55
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from logging import FileHandler, makeLogRecord
import os
import sys
import unittest

from custard.logstash.formatter import LogstashFormatter


# pylint: disable=protected-access


class ExceptionCatchingFileHandler(FileHandler):
    def __init__(self, *args, **kwargs):
        FileHandler.__init__(self, *args, **kwargs)
        self.exception = None

    def handleError(self, record):
        self.exception = sys.exc_info()


class LogstashFormatterTest(unittest.TestCase):
    def test_format(self):
        file_handler = ExceptionCatchingFileHandler(os.devnull)
        file_handler.setFormatter(LogstashFormatter(ensure_ascii=False))
        file_handler.emit(makeLogRecord({"msg": "тест"}))
        file_handler.close()

        self.assertIsNone(file_handler.exception)

    def test_format_timestamp_no_millisecond(self):
        formatter = LogstashFormatter()
        # 2023-01-30 07:05:35
        test_time_simple = 1675062335
        result = formatter._format_timestamp(test_time_simple)
        self.assertEqual(result, "2023-01-30T07:05:35.000Z")

    def test_format_timestamp_millisecond(self):
        formatter = LogstashFormatter()
        # 2023-01-30 07:05:35.025000
        test_time_millisecond = 1675062335.025000
        result = formatter._format_timestamp(test_time_millisecond)
        self.assertEqual(result, "2023-01-30T07:05:35.025Z")

    def test_format_timestamp_microsecond_1(self):
        formatter = LogstashFormatter()
        # 2023-01-30 07:05:35.000025
        test_time_microsecond1 = 1675062335.000025
        result = formatter._format_timestamp(test_time_microsecond1)
        self.assertEqual(result, "2023-01-30T07:05:35.000Z")

    def test_format_timestamp_microsecond_2(self):
        formatter = LogstashFormatter()
        # 2023-01-30 07:05:35.025757
        test_time_microsecond2 = 1675062335.025757
        result = formatter._format_timestamp(test_time_microsecond2)
        self.assertEqual(result, "2023-01-30T07:05:35.025Z")


if __name__ == "__main__":
    unittest.main()
