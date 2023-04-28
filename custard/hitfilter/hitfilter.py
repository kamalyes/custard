# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  hitfilter.py
@Time    :  2022/5/20 2:52 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  过滤敏感词
"""
import os


class DFAFilter:
    """
    Filter Messages from keywords
    Use DFA to keep algorithm perform constantly
    >>> f = DFAFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    """

    def __init__(self):
        self.keyword_path = [f"{os.path.dirname(os.path.realpath(__file__))}/keywords"]
        self.keyword_chains = {}
        self.delimit = "\x00"

    def add(self, keyword):
        if not isinstance(keyword, str):
            keyword = keyword.decode("utf-8")
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
            if i == len(chars) - 1:
                level[self.delimit] = 0

    def parse(self, path=None):
        if path is not None:
            self.keyword_path.append(path)
        if isinstance(self.keyword_path, list):
            for index in self.keyword_path:
                with open(index, "r", encoding="utf-8") as file:
                    for keyword in file:
                        self.add(keyword.strip())
            return None
        else:
            return TypeError("文件路径不正确")

    def filter(self, message, repl="*"):
        if not isinstance(message, str):
            message = message.decode("utf-8")
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1

        return "".join(ret)

    def is_contain_sensitive_key_word(self, message):
        repl = "_-__-"
        dest_string = self.filter(message=message, repl=repl)
        if repl in dest_string:
            return True
        return False
