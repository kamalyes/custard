# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  kerberos.py
@Time    :  2020/9/25 19:55
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  keys distributing center (密钥分配中心)
"""
import base64
import hashlib
from datetime import datetime, timedelta
from hashlib import sha1

import jwt


class Kerberos:
    @staticmethod
    def jwt_encode(secret_key, target_value, seconds):
        """
        jwt加密
        Args:
            secret_key:
            target_value:
            seconds:
        Returns:
        Examples:
            >>> JWT_SECRET_KEY = '1235678AC51Y55'
            >>> token = Kerberos.jwt_encode(secret_key=JWT_SECRET_KEY,
            ... target_value={"key1": "value1"}, seconds=0)
            >>> print(token)
            >>> import time
            >>> time.sleep(1)
            >>> print(Kerberos.jwt_decode(secret_key=JWT_SECRET_KEY, target_value=token))
        """
        return jwt.encode(
            {
                "target_value": target_value,
                "iat": datetime.utcnow() + timedelta(seconds=seconds),
                "exp": datetime.utcnow(),
            },
            secret_key,
            algorithm="HS256",
        )

    @staticmethod
    def jwt_decode(secret_key, target_value):
        """
        jwt 解密
        Args:
            secret_key:
            target_value:
        Returns:
        """
        return jwt.decode(target_value, secret_key, algorithms="HS256")

    @staticmethod
    def base64_encode(key: str):
        """
        base64 算法加密
        Args:
            key: 加密后的字符
        Returns:
        Examples:
            >>> print(Kerberos.base64_encode("Abc@1235678"))
        """
        return base64.b64encode(key.encode())

    @staticmethod
    def base64_decode(binary: str):
        """
        base64 算法解密
        Args:
            binary: 需要转成2进制格式才可以转换,所以我们这里再手动转换一下
        Returns:
        Examples:
            >>> print(Kerberos.base64_decode("QWJjQDEyMzU2Nzg="))
        """
        missing_padding = 4 - len(binary) % 4
        if missing_padding:
            binary += "=" * missing_padding
        return base64.b64decode(binary)

    @staticmethod
    def md5_encode(decode_msg: str):
        """
        md5 算法加密
        Args:
            decode_msg: 需加密的字符串
        Returns:
        Examples:
            >>> print(Kerberos.md5_encode("1235678"))
        """
        return hashlib.md5(str(decode_msg).encode(encoding="utf-8")).hexdigest()

    @staticmethod
    def sha1_decode(decode_msg: str):
        """
        哈希算法加密
        Args:
            decode_msg: 需加密的字符串
        Returns:
        Examples:
            >>> print(Kerberos.sha1_decode("Hello Word sha1Encrypt"))
        """
        return sha1(decode_msg.encode("utf-8")).hexdigest()
