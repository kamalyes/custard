# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  regex.py
@Time    :  2021/10/22 20:16
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  正则匹配
"""

import re
from typing import Any


class RegEx:
    @staticmethod
    def match_email(target: Any) -> bool:
        """
        效验邮箱格式
        Args:
            target:
        Returns:
        Example::
            >>> RegEx.match_email("test@163.com")
            >>> RegEx.match_email("test163.com")
        """
        return (
            True
            if re.match(
                "^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)",
                str(target),
            )
            else False
        )

    @staticmethod
    def match_chinese(target: Any) -> bool:
        """
        效验是否包含中文
        Args:
            target:
        Returns:
        Example::
            >>> RegEx.match_chinese("QSCVHI12356")
            >>> RegEx.match_chinese("哈哈哈")
        """
        return True if re.match(r".*?([\u4E00-\u9FA5])", str(target)) else False

    @staticmethod
    def match_double_byte_str(target: Any) -> bool:
        """
        效验是否存在双字节
        Args:
            target:
        Returns:
        Example::
            >>> RegEx.match_double_byte_str("哈哈哈")
            >>> RegEx.match_double_byte_str("QSCVHI12356")
            >>> RegEx.match_double_byte_str("QSCVHI12356哈哈哈")
        """
        return True if re.match(r".*?([^x00-xff])", str(target)) else False

    @staticmethod
    def weak_pwd(target: Any) -> bool:
        """
        效验密码是否为弱密码 (最低要求数字、英文、符合各一个、长度限制：7~20)
        Args:
            target:
        Returns:
        Example::
            >>> RegEx.weak_pwd(None)
            >>> RegEx.weak_pwd("QSCVHI12356@")
        """
        return (
            True
            if re.match(
                r"^(?:(?=.*[0-9].*)(?=.*[A-Za-z].*)(?=.*[\W].*))[\W0-9A-Za-z]{7,20}",
                str(target),
            )
               is None
            else False
        )

    @staticmethod
    def match_mobile(target: Any) -> bool:
        """
        效验手机号格式
        Args:
            target:
        Returns:
        Example::
            >>> RegEx.match_mobile("008618311006933")
            >>> RegEx.match_mobile("+8617888829981")
            >>> RegEx.match_mobile("19119255552")
        """
        rule = "^(?:(?:\\+|00)86)?1(?:(?:3[\\d])|(?:4[5-79])|(?:5[0-35-9])|(?:6[5-7])|(?:7[0-8])|(?:8[\\d])|(?:9[189]))\\d{8}"
        return True if re.match(rule, str(target)) else False

    @staticmethod
    def match_ipv4(target: Any) -> bool:
        """
        效验ipv4格式
        Args:
            target:
        Returns:
        Example::
            >>> RegEx.match_ipv4("127.16.0.0 is not ipv4")
            >>> RegEx.match_ipv4("127.16.0.0")
        """
        rule = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        return True if re.match(rule, str(target)) else False

    @staticmethod
    def match_str_length(target: Any, min_length=15, max_length=17) -> bool:
        """
        效验数字长度是否在区间值内
        Args:
            target:
            min_length:
            max_length:
        Returns:
        Example::
            >>> print(RegEx.match_str_length(17))
            >>> print(RegEx.match_str_length(12355678901235567))
        """
        rule = "^\\d{%s,%s}" % (min_length, max_length)
        return True if re.match(rule, str(target)) else False

    @staticmethod
    def match_username(target, min_length=7, max_length=20):
        """
        效验用户名格式 (必须由英文开头、长度限制：7~20)
        Args:
            target:
            min_length:
            max_length:
        Returns:
        Example::
            >>> print(RegEx.match_username("QS356"))
            >>> print(RegEx.match_username("QSCVHI12356"))
        """
        rule = r"^(?=.*[A-Za-z])[a-zA-Z0-9]{%s,%s}" % (min_length, max_length)
        return True if re.match(rule, str(target)) else False

    @staticmethod
    def match_valid_url(target):
        """
        效验url
        :param target:
        :return:
        Example::
            >>> print(RegEx.match_valid_url("https://www.baidu.com"))
            >>> print(RegEx.match_valid_url("127.0.0.1:8000"))
            >>> print(RegEx.match_valid_url("https://www.sweets.cn:8080"))
        """
        rule = r"^(((ht|f)tps?):\/\/)?[\w-]+(\.[\w-]+)+([\w.@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?$"
        return True if re.match(rule, str(target)) else False

    @staticmethod
    def match_trail_type(target, method=None):
        """
        效验尾缀格式
        :param target:
        :param method:
        :return:
        Example::
            >>> print(RegEx.match_trail_type(".bat"))
            >>> print(RegEx.match_trail_type(".image"))
            >>> print(RegEx.match_trail_type(".png", "image"))
        """
        image = ".*(\.png|\.jpg|\.jpeg|\.gif|\.mov)$"
        video = ".*(\.mp4|\.avi|\.mkv|\.flv|\.vob)$"
        exe = ".*(\.exe|\.sh|\.bat)$"
        docs = ".*(\.md|\.xls|\.xlsx|\.word|\.pdf)$"
        if method == "image":
            rule = image
        elif method == "video":
            rule = video
        elif method == "docs":
            rule = docs
        else:
            rule = exe
        return True if re.match(rule, str(target).lower()) else False
