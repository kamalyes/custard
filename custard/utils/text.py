# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  text.py
@Time    :  2022/5/30 1:35 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import re
import unicodedata

from typing import Pattern

_re_pattern: Pattern = re.compile(r"[^\w\s-]", flags=re.U)
_re_pattern_allow_dots: Pattern = re.compile(r"[^\.\w\s-]", flags=re.U)
_re_spaces: Pattern = re.compile(r"[-\s]+", flags=re.U)


def slugify(value: str, allow_dots: bool = False, allow_unicode: bool = False) -> str:
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace. Modified to optionally allow dots.

    Adapted from Django 1.9
    """
    pattern: Pattern = _re_pattern_allow_dots if allow_dots else _re_pattern

    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
        value = pattern.sub("", value).strip().lower()
        return _re_spaces.sub("-", value)
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = pattern.sub("", value).strip().lower()
    return _re_spaces.sub("-", value)
