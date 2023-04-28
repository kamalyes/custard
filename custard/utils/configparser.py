# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  area_code.py
@Time    :  2022/5/30 1:35 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  ini配置文件处理
"""

import configparser
import logging

logger = logging.getLogger(__name__)


class IniHandle:
    def __init__(self, filepath=None):
        self.conf = configparser.ConfigParser()
        self.conf.read(filepath, encoding="utf-8")

    def read(self, filepath=None):
        """
        打开指定的ini文件
        :param filepath:
        :return: <configparser.ConfigParser object at 0x0000015940785BA8>
        """
        try:
            conf = configparser.ConfigParser()
            conf.read(filepath, encoding="utf-8")
            return conf
        except Exception as FileNotFoundError:
            logger.error("文件读取失败,请检查%s是否存在,错误信息:%s" % (filepath, FileNotFoundError))

    def has_section(self, section, option=None):
        """
        检查节点
        :param section:
        :return:
        """
        try:
            if option is None:
                self.conf.has_section(section)
            else:
                self.conf.has_option(section, option)
        except Exception as e:
            logger.info("无此节点,错误信息%s" % (e))

    def section(self):
        """
        获取ini文件下所有的section值
        :return:  all_section
        """
        return self.conf.sections()

    def options(self, section):
        """
        获取指定section的所有option的Key
        :return:
        """
        if self.conf.has_section(section):
            return self.conf.options(section)
        else:
            raise ValueError(section)

    def sect_option(self, section):
        """
        获取指定section下的option的键值对
        :return: List形式的 [('a', 'b'),('aa', 'bb')]
        """
        if self.conf.has_section(section):
            return self.conf.items(section)
        return None

    def get(self, node, key):
        """
        获取指定section下option的value值
        :param filepath 需要读取的文件
        :param node 父类节点
        :param key  所需要查询内容的单一key
        :return: result 返回对应key的value值
        """
        return self.conf.get(node, key)

    def opt_all(self):
        """
        打印配置文件所有的值(该方法并不是很常用)
        :return:
        """
        for section in self.section():
            logger.info("[" + section + "]")
            for K, V in self.conf.items(section):
                logger.info(K + "=" + V)

    def sections_to_dict(self):
        """
        读取所有section到字典中
        :return:
        """
        res_1, res_2 = {}, {}
        sections = self.conf.sections()
        for sec in sections:
            for key, val in self.conf.items(sec):
                res_2[key] = val
            res_1[sec] = res_2.copy()
            res_2.clear()
        return res_1

    def remove_option(self, section, key=None):
        """
        删除一个 section中的一个item(以键值KEY为标识)
        :param section:
        :param key:
        :return:
        """
        if key is None:
            self.has_section(section)
            self.conf.remove_section(section)
        else:
            self.has_section(section, key)
            self.conf.remove_option(section, key)

    def add_section(self, section):
        """
        添加一个section
        :param section:
        :return:
        """
        self.conf.add_section(section)

    def set(self, section, key, value):
        """
        往section添加key和value
        :param section:
        :param key:
        :param value:
        :return:
        """
        self.conf.set(section, key, value)
