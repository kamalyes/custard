# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@file    :  helper.py
@time    :  2021/8/5 5:21 pm
@author  :  YuYanQing
@version :  1.0
@contact :  mryu168@163.com
@license :  (c)copyright 2022-2026
@desc    :  函数助手
"""
import random
import re
import string

from faker import Factory

from hutools.time.moment import Moment

fake = Factory().create("zh_CN")

default_elements = string.ascii_letters + string.digits


class Helper:
    @staticmethod
    def rand_mail(email_type=None, max_num=None, rad_count=None):
        """
        args:
            email_type: 邮箱类型
            max_num: 邮箱地址最大长度
            rad_count: 所生成的数量
        returns:
        Examples:
            >>> print(Helper.rand_mail(email_type="@qq.com", max_num=10, rad_count=5))
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
            # 每次转化后就丢弃temp、避免出现遍历追加['vjt000ho@qq.com',
            # 'vjt000ho0110fm0w@qq.com'............]
            temp.clear()
            email_list.append(temp_str + email_type_)
            count += 1
        return email_list

    @staticmethod
    def rand_verify_code(max_num: int, rad_count: int):
        """
        随机生成6位的验证码
        args:
            max_num: 最多可生成的长度
            rad_count: 需要生成的数量
        returns:
        Examples:
            >>> print(Helper.rand_verify_code(max_num=6, rad_count=1))
        """
        # 注意： 这里我们生成的是0-9a-za-z的列表，当然你也可以指定这个list，这里很灵活
        # 比如： code_list = ['p','y','t','h','o','n','t','a','b'] # pythontab的字母
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
            my_slice = random.sample(code_list, max_num)  # 从list中随机获取6个元素，作为一个片断返回
            verification_codes.append("".join(my_slice))  # list to string
            count += 1
        if rad_count > 1:
            return verification_codes
        else:
            return verification_codes[0]

    @staticmethod
    def rand_str_list(length):
        """
        生成给定长度的字符串，返回列表格式
        args:
            length:
        returns:
        Examples:
            >>> print(Helper.rand_str_list(length=5))
        """
        numbers = "".join(map(str, [i for i in range(10) if i != 4]))  # 数字
        init_chars = "".join(numbers)
        sample_list = random.sample(init_chars, length)
        return sample_list

    @staticmethod
    def rand_str(num_length):
        """
        从a-za-z0-9生成指定数量的随机字符
        args:
            num_length:
        returns:
        Examples:
            >>> print(str(Helper.rand_str(5)).title())
        """
        str_list = [
            random.choice(string.digits + string.ascii_letters)
            for i in range(num_length)
        ]
        random_str = "".join(str_list)
        return random_str

    @staticmethod
    def rand_mum(num_length):
        """
        9生成指定数量的随机数字
        args:
            num_length:
        returns:
        """
        str_list = [random.choice(string.digits) for i in range(num_length)]
        random_str = "".join(str_list)
        return random_str

    @staticmethod
    def randint_number(min_=1, max_=100):
        """
        随机生成整数
        Args:
            min_:
            max_:
        Returns:
        """
        pass

    @staticmethod
    def rand_float_number(data):
        """
        随机生成浮点数
        args:
            data:
        returns:
        """
        try:
            start_num, end_num, accuracy = data.split(",")
            start_num = int(start_num)
            end_num = int(end_num)
            accuracy = int(accuracy)
        except ValueError:
            raise AssertionError("调用随机整数失败，范围参数或精度有误！\n小数范围精度 %s" % data)
        if start_num <= end_num:
            num = random.uniform(start_num, end_num)
        else:
            num = random.uniform(end_num, start_num)
        return round(num, accuracy)

    @staticmethod
    def rand_time(layout):
        """
        随机生成时间
        :return:
        """
        return str(Moment.get_now_time(layout))

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
        :param days:
        :param seconds:
        :param microseconds:
        :param milliseconds:
        :param minutes:
        :param hours:
        :param weeks:
        :param custom:
        :return:
        """
        return str(
            Moment.compute_date(
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
    def rand_letters(length=10):
        """
        随机生成字母
        :param length:
        :return:
        """
        return "".join(fake.rand_letters(length=length))

    @staticmethod
    def rand_sample(elements=default_elements, length=10):
        """
        随机生成字符（英文+数字）
        :param elements:
        :param length:
        :return:
        """
        return "".join(fake.random_choices(elements=str(elements), length=length))

    @staticmethod
    def rand_mobile_number():
        """
        随机生成手机号
        :return:
        """
        return fake.phone_number()

    @staticmethod
    def rand_name():
        """
        随机生成名字
        :return:
        """
        return fake.name()

    @staticmethod
    def rand_address():
        """
        随机生成所在地址
        :return:
        """
        return fake.address()

    @staticmethod
    def rand_country():
        """
        随机生成国家名
        :return:
        """
        return fake.country()

    @staticmethod
    def rand_country_code():
        """
        随机生成国家代码
        :return:
        """
        return "".join(fake.country_code())

    @staticmethod
    def rand_city_name():
        """
        随机生成城市名
        :return:
        """
        return fake.city_name()

    @staticmethod
    def rand_city():
        """
        随机生成城市
        :return:
        """
        return fake.city()

    @staticmethod
    def rand_province():
        """
        随机生成省份
        :return:
        """
        return fake.province()

    @staticmethod
    def rand_email():
        """
        随机生成email
        :return:
        """
        return fake.email()

    @staticmethod
    def rand_ipv4():
        """
        随机生成ipv4地址
        :return:
        """
        return fake.ipv4()

    @staticmethod
    def rand_license_plate():
        """
        随机生成车牌号
        :return:
        """
        return fake.license_plate()

    @staticmethod
    def rand_color():
        """
        随机生成颜色
        :return:
        """
        return fake.rgb_color()

    @staticmethod
    def rand_safe_hex_color():
        """
        随机生成16进制的颜色
        :return:
        """
        return fake.safe_hex_color()

    @staticmethod
    def rand_color_name():
        """
        随机生成颜色名字
        :return:
        """
        return fake.color_name()

    @staticmethod
    def rand_company_name():
        """
        随机生成公司名
        :return:
        """
        return fake.company()

    @staticmethod
    def rand_job():
        """
        随机生成工作岗位
        :return:
        """
        return fake.job()

    @staticmethod
    def rand_pwd(
            length=10, special_chars=True, digits=True, upper_case=True, lower_case=True
    ):
        """
        随机生成密码
        :param lower_case:
        :param upper_case:
        :param digits:
        :param special_chars:
        :param length:
        :return:
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
        :return:
        """
        return fake.uuid4()

    @staticmethod
    def rand_sha1(raw_output=False):
        """
        随机生成sha1
        :return:
        """
        return fake.sha1(raw_output=raw_output)

    @staticmethod
    def rand_md5(raw_output=False):
        """
        随机生成md5
        :return:
        """
        return fake.md5(raw_output=raw_output)

    @staticmethod
    def rand_female():
        """
        随机生成女性名字
        :return:
        """
        return fake.name_female()

    @staticmethod
    def rand_male():
        """
        随机生成男性名字
        :return:
        """
        return fake.name_male()

    @staticmethod
    def rand_user_info(sex=None):
        """
        随机生成粗略的基本信息
        :return:
        """
        return fake.simple_profile(sex=sex)

    @staticmethod
    def rand_user_info_pro(fields=None, sex=None):
        """
        随机生成详细的基本信息
        :return:
        """
        return fake.profile(fields=fields, sex=sex)

    @staticmethod
    def rand_user_agent():
        """
        随机生成浏览器头user_agent
        :return:
        """
        return fake.user_agent()

    @staticmethod
    def get_user_vars(target_key=None):
        """
        组合静态跟动态变量
        :param target_key: 目标key
        :return:
        """
        return target_key

    @staticmethod
    def get_encrypt_vars(target_key=None):
        """
        获取提取后的参数
        :param target_key: 目标key
        :return:
        """
        return target_key

    @staticmethod
    def set_encrypt_vars(method, target_key):
        """
        给参数加密
        :param method: 加密风格 base64 md5 sha1
        :param target_key:
        :return:
        Examples:
            >>> print(Helper.set_encrypt_vars("base64_decode", "${randint_number}"))
            >>> print(Helper.set_encrypt_vars("base64_decode", "$var_test_001"))
            >>> print(Helper.set_encrypt_vars("base64_encode", "{{custom_null_var}}"))
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
                    method=method, target_key=Helper.cite(target_key)
                )
            )
            var = locals()["_var"]
            return var.decode() if isinstance(var, bytes) else var
        else:
            raise ModuleNotFoundError("暂时仅支持：%s" % (", ".join(func_list)))

    @staticmethod
    def cite(name: str):
        """
        函数助手，输出以下常用随机数，返回结果值。支持的函数详情见func_dict:
        :param name:  函数名，需要在func_dict存在的key值
        :return:  随机函数调用结果 or None
        Examples:
            >>> print(Helper.cite('${randint_number()}'))
            >>> print(Helper.cite('${randint_number(1,55)}'))
            >>> print(Helper.cite('${rand_letters(5)}'))
            >>> print(Helper.cite('${rand_sample(123567890,30)}'))
            >>> print(Helper.cite("${get_user_vars()}"))
            >>> print(Helper.cite("${get_user_vars(rand_pwd)}"))
            >>> print(Helper.cite("{{user_agent}}"))
            >>> print(Helper.cite("{{custom_none_var}}"))
            >>> print(Helper.cite("{{custom_null_var}}"))
            >>> print(Helper.cite("$var_test_001"))
            >>> print(Helper.cite('$enc_(base64_encode,base64参数加密)'))
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
            "int_number": Helper.randint_number,
            "float_number": Helper.rand_float_number,
            "time": Helper.rand_time,
            "compute_time": Helper.rand_compute_time,
            "letters": Helper.rand_letters,
            "sample": Helper.rand_sample,
            "mobile_number": Helper.rand_mobile_number,
            "name": Helper.rand_name,
            "address": Helper.rand_address,
            "country": Helper.rand_country,
            "country_code": Helper.rand_country_code,
            "city_name": Helper.rand_city_name,
            "city": Helper.rand_city,
            "province": Helper.rand_province,
            "email": Helper.rand_email,
            "ipv4": Helper.rand_ipv4,
            "license_plate": Helper.rand_license_plate,
            "color": Helper.rand_color,
            "rand_safe_hex_color": Helper.rand_safe_hex_color,
            "color_name": Helper.rand_color_name,
            "company_name": Helper.rand_company_name,
            "job": Helper.rand_job,
            "pwd": Helper.rand_pwd,
            "uuid4": Helper.rand_uuid4,
            "sha1": Helper.rand_sha1,
            "md5": Helper.rand_pwd,
            "female": Helper.rand_female,
            "male": Helper.rand_male,
            "user_info": Helper.rand_user_info,
            "user_info_pro": Helper.rand_user_info_pro,
            "user_agent": Helper.rand_user_agent,
            "user_vars": Helper.get_user_vars,
            "encrypt_vars": Helper.get_encrypt_vars,
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
            return Helper.cite(Helper.get_user_vars(own_vars.group().strip("{}")))
        elif extract_vars:
            return Helper.get_encrypt_vars(extract_vars.group())
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
                return Helper.set_encrypt_vars.__call__(*_lock_param)
        else:
            return name  # 函数名不存在返回原始值

    @staticmethod
    def comb_data(dict_map: dict) -> dict:
        """
        合并参数化数据
        :param dict_map: 初始data dict类型
        举例 {"product": {"brand_id": "${randint_number(1,2)}", "category_id": '${rand_float_number(1,2,3)}',"test": {"test": "${rand_sample(123567890abc,30)}"}}}
        转化后 {'product': {'brand_id': 7, 'category_id': 1.358, 'test': {'test': 'c071135252718592b58007a10093b6'}}}
        :return 转化后的数据 若无则返回原始值
        Examples:
            >>> print(Helper.comb_data({"product": {"brand_id": "{{int}}", "category_id": '${rand_float_number(1,2,3)}' }}))
            >>> print(Helper.comb_data({"create_time": "${rand_time(10timestamp)}"}))
            >>> print(Helper.comb_data({"key1":"$enc_(base64,base64参数加密)"}))
        """
        if isinstance(dict_map, dict):
            for key in list(dict_map.keys()):
                if isinstance(dict_map[key], list):
                    for i in range(len(dict_map[key])):
                        dict_map[key][i] = Helper.comb_data(dict_map=dict_map[key][i])
                elif isinstance(dict_map[key], dict):
                    dict_map[key] = Helper.comb_data(dict_map=dict_map[key])
                else:
                    dict_map[key] = Helper.cite(dict_map[key])
            return dict_map
        elif dict_map is None:  # fix：为空的时候raise 异常导致其它函数调用失败
            pass
