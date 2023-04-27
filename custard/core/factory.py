# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@file    :  factory.py
@time    :  2021/8/5 5:21 pm
@author  :  YuYanQing
@version :  1.0
@contact :  mryu168@163.com
@license :  (c)copyright 2022-2026
@desc    :  函数助手
"""
import json
import random
import re
import string
from typing import List, Dict
from urllib.parse import quote
import difflib
import hashlib
import json
import logging
from urllib.parse import unquote
import operator
from collections import Counter
from functools import reduce
from typing import Dict, Tuple
import pypinyin
from faker import Faker
from requests.exceptions import InvalidURL
from urllib3.exceptions import LocationParseError
from urllib3.util import parse_url
from custard.time.moment import Moment
from custard.utils.id_cards import IdNumber
from custard.core.system import System

fake = Faker(["zh_CN"])
logger = logging.getLogger(__name__)


class MockHelper:
    @staticmethod
    def rand_hans2pinyin(hans, style="A"):
        """
        汉字转拼音
        Args:
            hans: 汉字
            style: 返回首字母还是全拼, A:全拼; F:首字母
        Returns:
        Examples:
            >>> print(MockHelper.hans2pinyin("啊哈哈哈"))
            >>> print(MockHelper.hans2pinyin("啊哈哈哈", "F"))
        """

        if style.upper() == "F":
            return "".join(
                pypinyin.lazy_pinyin(hans=hans, style=pypinyin.Style.FIRST_LETTER)
            )
        else:
            return "".join(pypinyin.lazy_pinyin(hans=hans))

    @staticmethod
    def rand_id_card(random_sex):
        """
        随机生成有效身份证
        Args:
            random_sex: 性别
        Returns:
        Examples:
            >>> MockHelper.rand_id_card()
        """
        return IdNumber.get_id_card(random_sex)

    @staticmethod
    def rand_mail(email_type=None, max_num=None, rad_count=None):
        """
        Args:
            email_type: 邮箱类型
            max_num: 邮箱地址最大长度
            rad_count: 所生成的数量
        Returns:
        Examples:
            >>> MockHelper.rand_mail(email_type="@qq.com", max_num=10, rad_count=5)
        """
        temp = []
        count = 0
        email_list = []
        email_array = [
            "@126.com",
            "@163.com",
            "@sina.com",
            "@sohu.com",
            "@yahoo.com.cn",
            "@gmail.com",
            "@yahoo.com",
        ]
        email_type_ = random.choice(email_array) if email_type is None else email_type
        max_num_ = random.randint(5, 10) if max_num is None else max_num
        rad_count_ = 1 if rad_count is None else rad_count
        while count < rad_count_:
            for i in range(0, max_num_):
                status = random.randint(0, 1)
                if status == 0:
                    temp.append(random.choice(string.ascii_letters))
                else:
                    temp.append(str(random.randint(0, 1)))
            temp_str = "".join(temp)
            # 每次转化后就丢弃temp、避免出现遍历追加['vjt000ho@qq.com', 'vjt000ho0110fm0w@qq.com'............]
            temp.clear()
            email_list.append(temp_str + email_type_)
            count += 1
        return email_list

    @staticmethod
    def rand_verify_code(max_num: int, rad_count: int):
        """
        随机生成6位的验证码
        Args:
            max_num: 最多可生成的长度
            rad_count: 需要生成的数量
        Returns:
        Examples:
            >>> MockHelper.rand_verify_code(max_num=6, rad_count=1)
        """
        # 注意： 这里我们生成的是0-9a-za-z的列表,当然你也可以指定这个list,这里很灵活
        # 比如： code_list = ['p','y','t','h','o','n'] # python的字母
        count = 0
        verification_codes = []
        while count < rad_count:
            code_list = []
            for i in range(10):  # 0-9数字
                code_list.append(str(i))
            for i in range(65, 91):  # 对应从“a”到“z”的ascii码
                code_list.append(chr(i))
            for i in range(97, 123):  # 对应从“a”到“z”的ascii码
                code_list.append(chr(i))
            # 从list中随机获取6个元素,作为一个片断返回
            my_slice = random.sample(code_list, max_num)
            verification_codes.append("".join(my_slice))  # list to string
            count += 1
        if rad_count > 1:
            return verification_codes
        else:
            return verification_codes[0]

    @staticmethod
    def rand_str_list(length):
        """
        生成给定长度的字符串,返回列表格式
        Args:
            length:
        Returns:
        Examples:
            >>> MockHelper.rand_str_list(length=5)
        """
        init_chars = "".join("".join(map(str, [i for i in range(10) if i != 4])))  # 数字
        sample_list = random.sample(init_chars, length)
        return sample_list

    @staticmethod
    def rand_str(num_length):
        """
        从a-za-z0-9生成指定数量的随机字符
        Args:
            num_length:
        Returns:
        Examples:
            >>> MockHelper.rand_str(6)
        """
        return [
            random.choice(string.digits + string.ascii_letters)
            for i in range(num_length)
        ]

    @staticmethod
    def rand_mum(num_length):
        """
        9生成指定数量的随机数字
        Args:
            num_length:
        Returns:
        """
        return "".join([random.choice(string.digits) for i in range(num_length)])

    @staticmethod
    def rand_int_number(
        min_value: int = 0, max_value: int = 9999, step: int = 1
    ) -> int:
        """
        随机生成整数
        Args:
            min_value:
            max_value:
            step:
        Returns:
        Examples:
            >>> MockHelper.rand_int_number()
        """
        return random.randrange(min_value, max_value + 1, step)

    @staticmethod
    def rand_float_number(start_num=0, end_num=9, accuracy=1):
        """
        随机生成浮点数
        Args:
            start_num:
            end_num:
            accuracy:
        Returns:
        Examples:
            >>> MockHelper.rand_float_number(start_num=0, end_num=6, accuracy=3)
        """
        try:
            start_num = int(start_num)
            end_num = int(end_num)
            accuracy = int(accuracy)
        except ValueError:
            raise AssertionError("调用随机整数失败,范围参数或精度有误！\n小数范围精度")
        if start_num <= end_num:
            num = random.uniform(start_num, end_num)
        else:
            num = random.uniform(end_num, start_num)
        return round(num, accuracy)

    @staticmethod
    def rand_compute_time(
        days=0,
        seconds=0,
        microseconds=0,
        milliseconds=0,
        minutes=0,
        hours=0,
        weeks=0,
        custom=None,
    ):
        """
        随机生成偏移时间
        Args:
            days:
            seconds:
            microseconds:
            milliseconds:
            minutes:
            hours:
            weeks:
            custom:

        Returns:

        """
        return str(
            Moment.skew_date(
                days=days,
                seconds=seconds,
                microseconds=microseconds,
                milliseconds=milliseconds,
                minutes=minutes,
                hours=hours,
                weeks=weeks,
                custom=custom,
            )
        )

    @staticmethod
    def rand_lowercase_letter(length) -> str:
        """
        Generate a random lowercase ASCII letter (a-z).
        Args:
            length:

        Returns:

        Examples:
            >>> MockHelper.rand_lowercase_letter(10)
        """

        return "".join([random.choice(string.ascii_lowercase) for i in range(length)])

    @staticmethod
    def rand_uppercase_letter(length) -> str:
        """
        Generate a random uppercase ASCII letter (A-Z).
        Args:
            length:

        Returns:

        Examples:
            >>> MockHelper.rand_uppercase_letter(10)
        """
        return "".join([random.choice(string.ascii_uppercase) for i in range(length)])

    @staticmethod
    def rand_sample(length=10):
        """
        随机生成字符（英文+数字
        Args:
            length:

        Returns:

        Examples:
            >>> MockHelper.rand_sample(10)

        """
        return "".join(
            [random.choice(string.ascii_letters + string.digits) for i in range(length)]
        )

    @staticmethod
    def rand_mobile_number(length: int):
        """
        随机生成手机号
        Returns:
        Examples:
            >>> MockHelper.rand_mobile_number(1)
        """
        phone_prefixes = [
            134,
            135,
            136,
            137,
            138,
            139,
            147,
            150,
            151,
            152,
            157,
            158,
            159,
            182,
            187,
            188,
            130,
            131,
            132,
            145,
            155,
            156,
            185,
            186,
            145,
            133,
            153,
            180,
            181,
            189,
        ]
        rand_phone_prefix = phone_prefixes[random.randint(0, len(phone_prefixes))]
        return [f"{rand_phone_prefix}{MockHelper.rand_mum(8)}" for i in range(length)]

    @staticmethod
    def rand_name():
        """
        随机生成名字
        Returns:
        Examples:
            >>> MockHelper.rand_name()
        """
        return fake.name()

    @staticmethod
    def rand_address():
        """
        随机生成所在地址
        Returns:
        Examples:
            >>> MockHelper.rand_address()
        """
        return fake.address()

    @staticmethod
    def rand_country():
        """
        随机生成国家名
        Returns:
        Examples:
            >>> MockHelper.rand_country()
        """
        return fake.country()

    @staticmethod
    def rand_country_code():
        """
        随机生成国家代码
        Returns:
        Examples:
            >>> MockHelper.rand_country_code()
        """
        return "".join(fake.country_code())

    @staticmethod
    def rand_city_name():
        """
        随机生成城市名
        Returns:
        Examples:
            >>> MockHelper.rand_city_name()
        """
        return fake.city_name()

    @staticmethod
    def rand_city():
        """
        随机生成城市
        Returns:
        Examples:
            >>> MockHelper.rand_city()
        """
        return fake.city()

    @staticmethod
    def rand_province():
        """
        随机生成省份
        Returns:
        Examples:
            >>> MockHelper.rand_province()
        """
        return fake.province()

    @staticmethod
    def rand_email():
        """
        随机生成email
        Returns:
        Examples:
            >>> MockHelper.rand_email()
        """
        return fake.email()

    @staticmethod
    def rand_ipv4():
        """
        随机生成ipv4地址
        Returns:
        Examples:
            >>> MockHelper.rand_ipv4()
        """
        return fake.ipv4()

    @staticmethod
    def rand_license_plate():
        """
        随机生成车牌号
        Returns:
        Examples:
            >>> MockHelper.rand_license_plate()
        """
        return fake.license_plate()

    @staticmethod
    def rand_color():
        """
        随机生成颜色
        Returns:
        Examples:
            >>> MockHelper.rand_color()
        """
        return fake.rgb_color()

    @staticmethod
    def rand_safe_hex_color():
        """
        随机生成16进制的颜色
        Returns:
        Examples:
            >>> MockHelper.rand_safe_hex_color()
        """
        return fake.safe_hex_color()

    @staticmethod
    def rand_color_name():
        """
        随机生成颜色名字
        Returns:
        Examples:
            >>> MockHelper.rand_color_name()
        """
        return fake.color_name()

    @staticmethod
    def rand_company_name():
        """
        随机生成公司名
        Returns:
        Examples:
            >>> MockHelper.rand_company_name()
        """
        return fake.company()

    @staticmethod
    def rand_job():
        """
        随机生成工作岗位
        Returns:
        Examples:
            >>> MockHelper.rand_job()
        """
        return fake.job()

    @staticmethod
    def rand_pwd(
        length=10, special_chars=True, digits=True, upper_case=True, lower_case=True
    ):
        """
        随机生成密码
        lower_case:
        upper_case:
        digits:
        special_chars:
        length:
        Returns:
        """
        return fake.password(
            length=length,
            special_chars=special_chars,
            digits=digits,
            upper_case=upper_case,
            lower_case=lower_case,
        )

    @staticmethod
    def rand_uuid4():
        """
        随机生成uuid
        Returns:
        Examples:
            >>> MockHelper.rand_uuid4()
        """
        return fake.uuid4()

    @staticmethod
    def rand_sha1(raw_output=False):
        """
        随机生成sha1
        Returns:
        Examples:
            >>> MockHelper.rand_sha1()
        """
        return fake.sha1(raw_output=raw_output)

    @staticmethod
    def rand_md5(raw_output=False):
        """
        随机生成md5
        Args:
            raw_output:

        Returns:

        Examples:
            >>> MockHelper.rand_md5()
        """
        return fake.md5(raw_output=raw_output)

    @staticmethod
    def rand_female():
        """
        随机生成女性名字
        Returns:

        Examples:
            >>> MockHelper.rand_female()
        """
        return fake.name_female()

    @staticmethod
    def rand_male():
        """
        随机生成男性名字
        Returns:
        Examples:
            >>> MockHelper.rand_male()
        """
        return fake.name_male()

    @staticmethod
    def rand_user_info(sex=None):
        """
        随机生成粗略的基本信息
        Args:
            sex:

        Returns:

        Examples:
            >>> MockHelper.rand_user_info()
        """
        return fake.simple_profile(sex=sex)

    @staticmethod
    def rand_user_info_pro(fields=None, sex=None):
        """
        随机生成详细的基本信息
        Args:
            fields:
            sex:

        Returns:

        Examples:
            >>> MockHelper.rand_user_info_pro()
        """
        return fake.profile(fields=fields, sex=sex)

    @staticmethod
    def rand_user_agent():
        """
        随机生成浏览器头user_agent
        Returns:

        Examples:
            >>> MockHelper.rand_user_agent()
        """
        return fake.user_agent()

    @staticmethod
    def get_user_vars(target_key=None):
        """
        组合静态跟动态变量
        Args:
            target_key: 目标key

        Returns:

        Examples:
            >>> MockHelper.get_user_vars()
        """
        return target_key

    @staticmethod
    def get_encrypt_vars(target_key=None):
        """
        获取提取后的参数
        Args:
            target_key: 目标key
        Returns:
        Examples:
            >>> MockHelper.get_encrypt_vars()
        """
        return target_key

    @staticmethod
    def set_encrypt_vars(method, target_key):
        """
        给参数加密
        Args:
            method: 加密风格 base64 md5 sha1
            target_key:

        Returns:
        Examples:
            >>> MockHelper.set_encrypt_vars("base64_decode", "${randint_number}")
            >>> MockHelper.set_encrypt_vars("base64_decode", "$var_test_001")
            >>> MockHelper.set_encrypt_vars("base64_encode", "{{custom_null_var}}")
        """
        func_list = [
            "base64_encode",
            "base64_decode",
            "md5_encode",
            "sha1_decode",
            "jwt_decode",
            "jwt_encode",
        ]
        if method in func_list:
            exec(
                '_var = {method}("{target_key}")'.format(
                    method=method, target_key=MockHelper.cite(target_key)
                )
            )
            var = locals()["_var"]
            return var.decode() if isinstance(var, bytes) else var
        else:
            raise ModuleNotFoundError("暂时仅支持：%s" % (", ".join(func_list)))

    @staticmethod
    def cite(name: str):
        """
        函数助手,输出以下常用随机数,返回结果值。支持的函数详情见func_dict:
        Args:
            name:  函数名,需要在func_dict存在的key值
        Returns:  随机函数调用结果 or None
        Examples:
            >>> MockHelper.cite('${rand_int_number()}')
            >>> MockHelper.cite('${rand_int_number(1,55)}')
            >>> MockHelper.cite('${rand_lowercase_letter(5)}')
            >>> MockHelper.cite('${rand_sample(1235)}')
            >>> MockHelper.cite("${get_user_vars()}")
            >>> MockHelper.cite("${get_user_vars(rand_pwd)}")
            >>> MockHelper.cite("${rand_user_agent()}")
            >>> MockHelper.cite("{{custom_none_var}}")
            >>> MockHelper.cite("{{custom_null_var}}")
            >>> MockHelper.cite("$var_test_001")
            >>> MockHelper.cite('$enc_(base64_encode,base64参数加密)')
        """
        # fix: file "d:\program files\python37\lib\re.py", line 173, in match
        # return _compile(pattern, flags).match(string)
        # typeerror: expected string or bytes-like object
        rand_vars = re.match("\\$\\{rand_(.*)\\((.*)\\)\\}", str(name))  # 带参数
        rand_no_vars = re.match("\\$\\{rand_(.*)\\}", str(name))  # 无参数
        dynamic_vars = re.match("\\$\\{get(.*)\\((.*)\\)\\}", str(name))  # 动态自定义
        own_vars = re.match("\\{\\{(.*)\\}\\}", str(name))  # 动态自定义
        extract_vars = re.match("\\$var_(.*)", str(name).upper())  # 后置提取参数
        lock_vars = re.match("\\$enc_(.*)", str(name))  # 带参数
        pattern = rand_vars if rand_vars is not None else dynamic_vars
        func_dict = {
            "mum": MockHelper.rand_mum,
            "hans2pinyin": MockHelper.rand_hans2pinyin,
            "id_card": MockHelper.rand_id_card,
            "mail": MockHelper.rand_mail,
            "int_number": MockHelper.rand_int_number,
            "float_number": MockHelper.rand_float_number,
            "compute_time": MockHelper.rand_compute_time,
            "lowercase_letter": MockHelper.rand_lowercase_letter,
            "uppercase_letter": MockHelper.rand_uppercase_letter,
            "sample": MockHelper.rand_sample,
            "mobile_number": MockHelper.rand_mobile_number,
            "name": MockHelper.rand_name,
            "address": MockHelper.rand_address,
            "country": MockHelper.rand_country,
            "country_code": MockHelper.rand_country_code,
            "city_name": MockHelper.rand_city_name,
            "city": MockHelper.rand_city,
            "province": MockHelper.rand_province,
            "email": MockHelper.rand_email,
            "ipv4": MockHelper.rand_ipv4,
            "license_plate": MockHelper.rand_license_plate,
            "color": MockHelper.rand_color,
            "rand_safe_hex_color": MockHelper.rand_safe_hex_color,
            "color_name": MockHelper.rand_color_name,
            "company_name": MockHelper.rand_company_name,
            "job": MockHelper.rand_job,
            "pwd": MockHelper.rand_pwd,
            "uuid4": MockHelper.rand_uuid4,
            "sha1": MockHelper.rand_sha1,
            "md5": MockHelper.rand_pwd,
            "female": MockHelper.rand_female,
            "male": MockHelper.rand_male,
            "user_info": MockHelper.rand_user_info,
            "user_info_pro": MockHelper.rand_user_info_pro,
            "user_agent": MockHelper.rand_user_agent,
            "user_vars": MockHelper.get_user_vars,
            "encrypt_vars": MockHelper.get_encrypt_vars,
        }
        if pattern is not None:
            key, value = pattern.groups()
            if func_dict.get(key):
                func = func_dict[key]
                _param = [
                    eval(x) if x.strip().isdigit() else x for x in value.split(",")
                ]
                if len(_param) >= 1 and "" not in _param:
                    return func.__call__(*_param)
                elif "" in _param:
                    return func.__call__()  # 没有带参数的
        elif own_vars:
            return MockHelper.cite(
                MockHelper.get_user_vars(own_vars.group().strip("{}"))
            )
        elif extract_vars:
            return MockHelper.get_encrypt_vars(extract_vars.group())
        elif rand_no_vars:
            return func_dict[rand_no_vars.group().strip("${rand_}")].__call__()
        elif lock_vars:
            _lock_param = [
                eval(x) if x.strip().isdigit() else x
                for x in lock_vars.group().strip("$enc_()").split(",")
            ]
            if len(_lock_param) < 2:
                raise IndexError(_lock_param)
            else:
                return MockHelper.set_encrypt_vars.__call__(*_lock_param)
        else:
            return name  # 函数名不存在返回原始值

    @staticmethod
    def comb_data(dict_map: dict) -> dict:
        """
        合并参数化数据
        Args:
            dict_map: 初始data dict类型

        Returns: 转化后的数据 若无则返回原始值

        Examples:
            >>> MockHelper.comb_data({"product": {"brand_id": "{{int}}", "category_id": '${rand_float_number(1,2,3)}'}})
            >>> MockHelper.comb_data({"now_time": "${rand_compute_time()}"})
            >>> MockHelper.comb_data({"key1":"$enc_(base64,base64参数加密)"})
        """
        if isinstance(dict_map, dict):
            for key in list(dict_map.keys()):
                if isinstance(dict_map[key], list):
                    for i in range(len(dict_map[key])):
                        dict_map[key][i] = MockHelper.comb_data(
                            dict_map=dict_map[key][i]
                        )
                elif isinstance(dict_map[key], dict):
                    dict_map[key] = MockHelper.comb_data(dict_map=dict_map[key])
                else:
                    dict_map[key] = MockHelper.cite(dict_map[key])
            return dict_map
        elif dict_map is None:  # fix：为空的时候raise 异常导致其它函数调用失败
            pass


class DataKitHelper:
    @classmethod
    def add_dicts(cls, *args: Tuple[Dict, ...]) -> Dict:
        """
        Adds two or more dicts together. Common keys will have their values added.

        Returns:
        Example:
            >>> t1 = {'a':1, 'b':2}
            >>> t2 = {'b':1, 'c':3}
            >>> t3 = {'d':5}
            >>> DataKit.add_dicts(t1, t2, t3)
            {'a': 1, 'c': 3, 'b': 3, 'd': 5}
        """

        counters = [Counter(arg) for arg in args]
        return dict(reduce(operator.add, counters))

    @classmethod
    def get_target_value(
        cls, dict_map: dict, separate: str = "$.", result: dict = None
    ):
        if result is None:
            result = dict()
        """
        递归获取所有的TargetValue
        :param dict_map: 初始data dict类型
        :param separate: 临时节点 str类型
        :param result:  用于存储所有遍历出来的结果 list集合
        :return: {xx,xx,xx} 以字典形式追加
        Example::
            >>> DataKit.get_target_value(dict_map={"TEST_001": "TEST_VALUE001","TEST_002": [{"TEST_VALUE002-001": "VALUE"}, {"TEST_VALUE002-002": "VALUE"}]})
        """
        if isinstance(dict_map, dict):
            for key, value in dict_map.items():
                temp = separate + key + "."
                # 若类型为list 后面还有一维或二位数组类型数据递归找
                if isinstance(value, list):
                    for i in range(len(value)):
                        cls.get_target_value(
                            dict_map=value[i], separate=temp + str(i) + "."
                        )
                # 若类型还是dict，继续遍历
                elif isinstance(value, dict):
                    cls.get_target_value(dict_map=value, separate=temp)
                # str或者int类型时就基本上判定为具体的xxx值
                elif str(value).isdigit():
                    result.update({separate + key: int(value)})
                elif isinstance(value, str):
                    result.update({separate + key: value})
            return result
        else:
            raise TypeError("传入的参数不是dict类型 %s" % (type(dict_map)))

    @classmethod
    def convert_type(cls, dict_map: dict, disable_data: list = []) -> dict:
        """
        将只有数字的键值给强转类型为int
        :param dict_map: 初始data dict类型
        :param disable: 不用处理的键值对
        Example::
            >>> DataKit.convert_type({'product': {'brand_id': None, 'category_id': '15888'}})
            >>> DataKit.convert_type({'product': {'brand_id': None, 'category_id': '15888'}},["category_id"])
        """
        if isinstance(dict_map, dict):
            for key in list(dict_map.keys()):
                if isinstance(dict_map[key], list):
                    for i in range(len(dict_map[key])):
                        dict_map[key][i] = cls.convert_type(
                            dict_map=dict_map[key][i], disable_data=disable_data
                        )
                elif isinstance(dict_map[key], dict):
                    dict_map[key] = cls.convert_type(
                        dict_map=dict_map[key], disable_data=disable_data
                    )
                elif str(dict_map[key]).isdigit() and str(key) not in disable_data:
                    dict_map[key] = int(dict_map[key])
                elif str(dict_map[key]) == "null":  # 统一处理str无法转化None
                    dict_map[key] = None
            return (
                json.dumps(dict_map, ensure_ascii=False)
                .replace('\\"', '"')
                .replace('"{', "{")
                .replace('}"', "}")
            )  # 临时打个补丁 后续若报错则需再次做兼容
        else:
            raise TypeError("传入的参数不是dict类型 %s" % (type(dict_map)))

    @classmethod
    def dict_to_from(cls, post_data):
        """
        字典转xwww-from格式
        :param post_data: dict {"a": 1, "b":2}
        :return: str: a=1&b=2
        """
        if isinstance(post_data, dict):
            return "&".join(
                ["{}={}".format(key, value) for key, value in post_data.items()]
            )
        else:
            return post_data

    @classmethod
    def form_to_dict(cls, post_data):
        """
        x-www-from格式转字典
        :param post_data (str): a=1&b=2
        :return dict: {"a":1, "b":2}
        """
        if isinstance(post_data, str):
            converted_dict = {}
            for k_v in post_data.split("&"):
                try:
                    key, value = k_v.split("=")
                except ValueError:
                    raise Exception(
                        "Invalid x_www_form_urlencoded data format: {}".format(
                            post_data
                        )
                    )
                converted_dict[key] = unquote(value)
            return converted_dict
        else:
            return post_data

    @classmethod
    def list_sub_dict(cls, origin_list):
        """
        list转dict
        :param origin_list: (list) [{"name": "v", "value": "1"},{"name": "w", "value": "2"}]
        :return: dict:{"v": "1", "w": "2"}
        """
        return {item["name"]: item.get("value") for item in origin_list}

    @classmethod
    def dict_capital_to_lower(cls, dict_map):
        """
        dict中的key转换小写
        :param dict_map:
        :return:
        """
        new_dict = {}
        for key in list(dict_map.keys()):
            new_dict[key.lower()] = dict_map[key]
        return new_dict

    @classmethod
    def capital_lower_to_dict(cls, dict_map):
        """
        dict中的key转换大写
        :param dict_map:
        :return:
        """
        new_dict = {}
        for key in list(dict_map.keys()):
            new_dict[key.upper()] = dict_map[key]
        return new_dict

    @classmethod
    def diffJson(cls, filename1, filename2, targetPath):
        """
        比较两个文件内容的md5值并输出到html文件中
        :param filename1:
        :param filename2:
        :param targetPath:
        :return:
        """
        file1Md5 = hashlib.md5.new(filename1.read()).digest()
        file2Md5 = hashlib.md5.new(filename2.read()).digest()
        if file1Md5 != file2Md5:
            text1_lines = System.load_file(filename1, "json")
            text2_lines = System.load_file(filename2, "json")
            d = difflib.HtmlDiff()
            # context=True时只显示差异的上下文，默认显示5行，由numlines参数控制，context=False显示全文，差异部分颜色高亮，默认为显示全文
            result = d.make_file(
                text1_lines, text2_lines, filename1, filename2, context=True
            )
            # 内容保存到result.html文件中
            try:
                with open(targetPath, "a", encoding="utf-8") as result_file:
                    result_file.write(result)
            except Exception as e:
                logger.error("写入文件失败:" + e)

    @classmethod
    def is_json_format(cls, raw_data):
        """
        用于判断一个字符串是否符合Json格式
        :param raw_data:
        :return:
        """
        if isinstance(raw_data, str):
            try:
                json.loads(raw_data, encoding="utf-8")
            except ValueError:
                return False
            else:
                return True
        else:
            return False

    @classmethod
    def json_to_dict(cls, data):
        """
        Json转字典
        :param data: 数据来源
        :return:
        """
        return json.loads(data)

    @classmethod
    def dict_to_json(
        cls, data, sort_keys=False, ensure_ascii=False, indent=4, separators=(",", ": ")
    ):
        """
        字典转Json
        :param data: 数据来源
        :return:
        """
        return json.dumps(
            data,
            ensure_ascii=ensure_ascii,
            sort_keys=sort_keys,
            indent=indent,
            separators=separators,
        )

    @classmethod
    def json_to_schema(cls, data, result=None):
        """
        json递归生成schema
        :param data:
        :param result:
        :return:
        Example::
            >>> data = {"code": 200, "message": "Success", "error": "",
            ... "ShopInfoList": [{"shop_id": "ML0057", "shop_name": "" }]}
            >>> DataKit.json_to_schema(data=data)
        """
        if result is None:
            result = list()
        if isinstance(data, dict):
            is_null = True
            result.append("{")
            result.append("'type': 'object',")
            result.append("'properties': {")
            for k, v in data.items():
                is_null = False
                result.append("'%s':" % k)
                cls.json_to_schema(v, result)
                result.append(",")
            if not is_null:
                result.pop()
            result.append("}")
            result.append("}")
        elif isinstance(data, list):
            result.append("{")
            result.append("'type': 'array',")
            result.append("'items': ")
            cls.json_to_schema(data[0], result)
            result.append("}")
        elif isinstance(data, int):
            result.append("{")
            result.append("'type': 'number'")
            result.append("}")
        elif isinstance(data, str):
            result.append("{")
            result.append("'type': 'string'")
            result.append("}")
        return json.dumps("".join(result), indent=4)


class AutoVivification(dict):
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
        return value


class MsHelper(object):
    GLOBAL_PAGE_INDEX = ["page_index", "pageindex"]
    GLOBAL_PAGE_SIZE = ["page_size", "pagesize"]

    @classmethod
    def __property__(cls, prop):
        """
        数据转换
        Args:
            prop:
        Returns:
        Examples:
            >>> props = [1,"abc",True,None,False]
            >>> for prop in props:
            ...    MsHelper.__property__(prop)
        """
        randint_val = random.randint(1, 1000)
        if isinstance(prop, bool):
            prop = "true" if prop else "false"
        if isinstance(prop, int):
            prop = randint_val
        elif isinstance(prop, float):
            prop = randint_val / 3.333
        elif prop is None:
            prop = "null"
        return prop

    @classmethod
    def obj_convert_dict(cls, data):
        """
        字典类型转换
        Args:
            data:
        Returns:
        """
        support_type = (list, float, int, tuple)
        type_err = TypeError("类型错误、仅支持dict")
        if isinstance(data, support_type):
            raise type_err
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.decoder.JSONDecodeError as decoder_err:
                raise Exception(decoder_err)
        if isinstance(data, dict):
            return data

    @classmethod
    def sub_kv(cls, data: List):
        """
        合并key value
        Args:
            data:
        Returns:
        Examples:
            >>> data_ = ["a1=5","a3=6"]
            >>> dint_data_ = ["a2=6","a2=6"]
            >>> MsHelper.sub_kv(data_)
            >>> MsHelper.sub_kv(dint_data_)
        """
        temp_dict = {}
        for index in range(len(data)):
            present = data[index]
            if "=" in present:
                pr_ = present.split("=")
                temp_dict.update({pr_[0]: pr_[1]})
            else:
                temp_dict.update({present: ""})
            # 相同数据跳出
            if index < len(data) - 1 and present == data[index + 1]:
                break
        return temp_dict

    @classmethod
    def url_to_json(cls, url):
        """
        form-data 转换为 Json
        Args:
            url:
        Returns:
        Examples:
            >>> form_data_ = ""
            >>> for index in range(10000):
            ...     form_data_ += f"&a{index}={index}"
            >>> url_ = f"http://localhost?{form_data_}"
            >>> output_ = MsHelper.url_to_json(url_)
            >>> print(output_)
        """
        try:
            scheme, auth, host, port, path, query, fragment = parse_url(url)
        except LocationParseError as e:
            raise InvalidURL(*e.args)
        output = {}
        if query:
            query_split = query.split("&")
            start = 0
            end = len(query_split) - 1
            while start <= end:
                spl_data = [query_split[start], query_split[end]]
                output = dict(output, **cls.sub_kv(spl_data))
                start += 1
                end -= 1
        return output

    @classmethod
    def json2form(cls, obj):
        """
        json转换为fromdata
        Args:
            obj:
        Returns:
        Examples:
            >>> have_array_obj_ = {"a":125678,"b":"ABCDEFG", "c":[{"c1":5}]}
            >>> have_dict_obj_ = {"a":125678,"b":"ABCDEFG", "c":{"c1":5}}
            >>> err_obj_ = {"a":125678,"b":"ABCDEFG", "c":[{"c1":5}],  "d":{"d1":5}}
            >>> obj_ = {"a":125678,"b":"%", "c":"=","d":"&", "e":""}
            >>> MsHelper.json2form(json.dumps(obj_))
            >>> MsHelper.json2form(json.dumps(have_array_obj_))
            >>> MsHelper.json2form(json.dumps(have_dict_obj_))
            >>> MsHelper.json2form(json.dumps(err_obj_))
        """
        output = ""
        data = cls.obj_convert_dict(obj)
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                raise TypeError("请核对参数及Content-Type是否规范")
            if isinstance(value, str):
                value = quote(value, "unicode")
            output += f"&{key}={value}"
        return output

    @classmethod
    def json2vars(cls, target_data, source_data="", replace=True):
        """
        json转为vars
        Args:
            target_data:
            source_data:
            replace:
        Returns:
        Examples:
            >>> data_ = { "code": 200, "message": None, "error": False, "details":[{"d1":True}], "total_count": 5}
            >>> result = MsHelper.json2vars(data_)
        """
        if isinstance(target_data, dict):
            for key, value in target_data.items():
                if not isinstance(value, (list, dict)):
                    if value is None:
                        value = "null"
                    elif isinstance(value, bool):
                        value = "true" if value else "false"
                    if replace:
                        paging = [cls.GLOBAL_PAGE_INDEX, cls.GLOBAL_PAGE_SIZE]
                        if key in cls.GLOBAL_PAGE_INDEX:
                            value = 1
                        elif key in cls.GLOBAL_PAGE_SIZE:
                            value = 10
                        if key not in paging:
                            value = cls.__property__(value)
                    source_data += f'vars.put("{key}","{value}");\n'
                else:
                    source_data = cls.json2vars(
                        target_data=value, source_data=source_data, replace=replace
                    )
        elif isinstance(target_data, list):
            for index in range(len(target_data)):
                target_data_ = target_data[index]
                # 启用该行数据不会去重,有多少条就产生多少
                # source_data = cls.json2vars(target_data=target_data_, source_data=source_data, replace=replace)
                # 以下方式会去重
                return cls.json2vars(
                    target_data=target_data_, source_data=source_data, replace=replace
                )
        return source_data
