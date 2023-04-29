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
import logging
import random
import re
import string
from typing import List
from urllib.parse import quote

import pypinyin
from faker import Faker
from requests.exceptions import InvalidURL
from urllib3.exceptions import LocationParseError
from urllib3.util import parse_url
from custard.core.processor import DataKitHelper

from custard.time.moment import Moment
from custard.utils.id_cards import IdNumber

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
            return "".join(pypinyin.lazy_pinyin(hans=hans, style=pypinyin.Style.FIRST_LETTER))
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
            for _i in range(0, max_num_):
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
        # 注意: 这里我们生成的是0-9a-za-z的列表,当然你也可以指定这个list,这里很灵活
        # 比如: code_list = ['p','y','t','h','o','n'] # python的字母
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
        return [random.choice(string.digits + string.ascii_letters) for i in range(num_length)]

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
    def rand_int_number(min_value: int = 0, max_value: int = 9999, step: int = 1) -> int:
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
            raise AssertionError("调用随机整数失败,范围参数或精度有误!\n小数范围精度")
        num = random.uniform(start_num, end_num) if start_num <= end_num else random.uniform(end_num, start_num)
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
            ),
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
        随机生成字符(英文+数字
        Args:
            length:

        Returns:

        Examples:
            >>> MockHelper.rand_sample(10)

        """
        return "".join([random.choice(string.ascii_letters + string.digits) for i in range(length)])

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
    def rand_pwd(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True):
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
            exec('_var = {method}("{target_key}")'.format(method=method, target_key=MockHelper.cite(target_key)))
            var = locals()["_var"]
            return var.decode() if isinstance(var, bytes) else var
        else:
            raise ModuleNotFoundError("暂时仅支持:%s" % (", ".join(func_list)))

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
                _param = [eval(x) if x.strip().isdigit() else x for x in value.split(",")]
                if len(_param) >= 1 and "" not in _param:
                    return func.__call__(*_param)
                elif "" in _param:
                    return func.__call__()  # 没有带参数的
                return None
            return None
        elif own_vars:
            vars_ = MockHelper.get_user_vars(own_vars.group().strip("{}"))
            return MockHelper.cite(vars_)
        elif extract_vars:
            return MockHelper.get_encrypt_vars(extract_vars.group())
        elif rand_no_vars:
            return func_dict[rand_no_vars.group().strip("${rand_}")].__call__()
        elif lock_vars:
            _lock_param = [eval(x) if x.strip().isdigit() else x for x in lock_vars.group().strip("$enc_()").split(",")]
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
                        dict_map[key][i] = MockHelper.comb_data(dict_map=dict_map[key][i])
                elif isinstance(dict_map[key], dict):
                    dict_map[key] = MockHelper.comb_data(dict_map=dict_map[key])
                else:
                    dict_map[key] = MockHelper.cite(dict_map[key])
            return dict_map
        return None


class AutoVivification(dict):
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
        return value


class MsHelper(DataKitHelper):
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
                return cls.safely_json_loads(data)
            except json.decoder.JSONDecodeError as decoder_err:
                raise Exception(decoder_err)
        if isinstance(data, dict):
            return data
        return None

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
                    source_data = cls.json2vars(target_data=value, source_data=source_data, replace=replace)
        elif isinstance(target_data, list):
            for index in range(len(target_data)):
                target_data_ = target_data[index]
                # 启用该行数据不会去重,有多少条就产生多少
                # source_data = cls.json2vars(target_data=target_data_, source_data=source_data, replace=replace)
                # 以下方式会去重
                return cls.json2vars(target_data=target_data_, source_data=source_data, replace=replace)
        return source_data
