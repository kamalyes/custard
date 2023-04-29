# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  processor.py
@Time    :  2022/5/1 8:21 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  数据处理器
"""
import base64
import difflib
import hashlib
import json
import logging
import operator
import re
import time
import xml.dom.minidom
import xml.etree.ElementTree
from collections import Counter
from functools import reduce
from itertools import zip_longest
from typing import Any, Dict, Tuple
from urllib.parse import unquote

from dicttoxml import dicttoxml
from six import binary_type, text_type

from custard.core.xml2dict import Xml2Dict

logger = logging.getLogger(__name__)


SINGLE_UPLOAD_LENGTH = 5 * 1024 * 1024 * 1024  # 单次上传文件最大为5GB
DEFAULT_CHUNK_SIZE = 1024 * 1024  # 计算MD5值时,文件单次读取的块大小为1MB


class DataKitHelper:
    @classmethod
    def sub_dict_value(cls, *args: Tuple[Dict, ...]) -> Dict:
        """
        Adds two or more dicts together. Common keys will have their values added.

        Returns:
        Example:
            >>> t1 = {'a':1, 'b':2}
            >>> t2 = {'b':1, 'c':3}
            >>> t3 = {'d':5}
            >>> DataKit.sub_dict_value(t1, t2, t3)
            {'a': 1, 'c': 3, 'b': 3, 'd': 5}
        """

        counters = [Counter(arg) for arg in args]
        return dict(reduce(operator.add, counters))

    @classmethod
    def get_target_value(cls, dict_map: dict, separate: str = "$.", result: dict = None):
        if result is None:
            result = {}
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
                        cls.get_target_value(dict_map=value[i], separate=temp + str(i) + ".")
                # 若类型还是dict,继续遍历
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
                        dict_map[key][i] = cls.convert_type(dict_map=dict_map[key][i], disable_data=disable_data)
                elif isinstance(dict_map[key], dict):
                    dict_map[key] = cls.convert_type(dict_map=dict_map[key], disable_data=disable_data)
                elif str(dict_map[key]).isdigit() and str(key) not in disable_data:
                    dict_map[key] = int(dict_map[key])
                elif str(dict_map[key]) == "null":  # 统一处理str无法转化None
                    dict_map[key] = None
            return dict_map
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
            return "&".join(["{}={}".format(key, value) for key, value in post_data.items()])
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
                    err = "Invalid x_www_form_urlencoded data format: {}".format(post_data)
                    raise Exception(err)
                converted_dict[key] = unquote(value)
            return converted_dict
        else:
            return post_data

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
            result = []
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

    @classmethod
    def args_to_str(*args, **kwargs):
        """
        args 转换为 str
        Args:
            *args:
            **kwargs:
        Returns:
        """
        str1 = ", ".join(str(i) for i in args)
        kv = []
        for k, v in kwargs.items():
            kv.append(f"{k}={v}")
        str2 = ", ".join(kv)
        if kwargs and args:
            return f"{str1}, {str2}"
        if args:
            return str1
        if kwargs:
            return str2
        return ""

    @classmethod
    def to_str(cls, variable):
        """非字符串转换为字符串"""
        if isinstance(variable, (text_type, binary_type)):
            return variable
        return str(variable)

    @classmethod
    def to_unicode(cls, variable):
        """将字符串转为unicode"""
        if isinstance(variable, binary_type):
            try:
                return variable.decode("utf-8")
            except UnicodeDecodeError:
                raise UnicodeDecodeError("your bytes strings can not be decoded in utf8, utf8 support only!")
        return variable

    @classmethod
    def to_bytes(cls, variable):
        """将字符串转为bytes"""
        if isinstance(variable, text_type):
            try:
                return variable.encode("utf-8")
            except UnicodeEncodeError:
                raise UnicodeEncodeError("your unicode strings can not encoded in utf8, utf8 support only!")
        return variable

    @classmethod
    def deep_dict_update(cls, main_dict: Dict[Any, Any], update_dict: Dict[Any, Any]) -> None:
        """
        字典更新
        Args:
            main_dict:
            update_dict:

        Returns:

        Examples:
            >>> main_dict = {"a":1, "b":2, "c":{"abc":123}}
            >>> update_dict = {"a":2, "b":5, "c":{"abc":1235678}}
            >>> print(DataKitHelper.deep_dict_update(main_dict, update_dict))

        """
        for key, value in update_dict.items():
            if key in main_dict and isinstance(main_dict[key], dict) and isinstance(value, dict):
                cls.deep_dict_update(main_dict[key], value)
            else:
                main_dict[key] = value
        return main_dict

    @classmethod
    def lower_dict_keys(cls, origin_dict: Dict):
        """
        convert keys in dict to lower case
        Args:
            origin_dict: mapping data structure

        Returns:
            dict: mapping with all keys lowered.

        Examples:
            >>> origin_dict = { "Name": "", "Request": "", "URL": "", "METHOD": "", "Headers": "", "Data": ""}
            >>> DataKitHelper.lower_dict_keys(origin_dict)
        """
        if not origin_dict or not isinstance(origin_dict, dict):
            return origin_dict

        return {str(key).lower(): value for key, value in origin_dict.items()}

    @classmethod
    def upper_dict_keys(cls, origin_dict: Dict):
        """
        convert keys in dict to lower case
        Args:
            origin_dict: mapping data structure

        Returns:
            dict: mapping with all keys lowered.

        Examples:
            >>> origin_dict = {'name': '', 'request': '', 'url': '', 'method': '', 'headers': '', 'data': ''}
            >>> DataKitHelper.upper_dict_keys(origin_dict)
        """
        if not origin_dict or not isinstance(origin_dict, dict):
            return origin_dict

        return {str(key).upper(): value for key, value in origin_dict.items()}

    @classmethod
    def omit_long_data(cls, body, omit_len=512):
        """omit too long str/bytes"""
        if not isinstance(body, (str, bytes)):
            return body

        body_len = len(body)
        if body_len <= omit_len:
            return body

        omitted_body = body[0:omit_len]

        appendix_str = f" ... OMITTED {body_len - omit_len} CHARACTORS ..."
        if isinstance(body, bytes):
            appendix_str = appendix_str.encode("utf-8")

        return omitted_body + appendix_str

    @classmethod
    def get_raw_md5(cls, data):
        """计算md5 md5的输入必须为bytes"""
        m2 = hashlib.md5(DataKitHelper.to_bytes(data))
        etag = '"' + str(m2.hexdigest()) + '"'
        return etag

    @classmethod
    def get_md5(cls, data):
        """
        计算 base64 md5 md5的输入必须为bytes
        Args:
            data:

        Returns:

        """
        m2 = hashlib.md5(cls.to_bytes(data))
        md5 = base64.standard_b64encode(m2.digest())
        return md5

    @classmethod
    def get_content_md5(cls, body):
        """计算任何输入流的md5值"""
        if isinstance(body, (text_type, binary_type)):
            return cls.get_md5(body)
        elif hasattr(body, "tell") and hasattr(body, "seek") and hasattr(body, "read"):
            file_position = body.tell()  # 记录文件当前位置
            # avoid OOM
            md5 = hashlib.md5()
            chunk = body.read(DEFAULT_CHUNK_SIZE)
            while chunk:
                md5.update(cls.to_bytes(chunk))
                chunk = body.read(DEFAULT_CHUNK_SIZE)
            md5_str = base64.standard_b64encode(md5.digest())
            try:
                body.seek(file_position)  # 恢复初始的文件位置
            except Exception:
                raise Exception("seek unsupported to calculate md5!")
            return md5_str
        else:
            raise Exception("unsupported body type to calculate md5!")

    @classmethod
    def dict_to_xml(cls, data):
        """V5使用xml格式,将输入的dict转换为xml"""
        doc = xml.dom.minidom.Document()
        root = doc.createElement("CompleteMultipartUpload")
        doc.appendChild(root)

        if "Part" not in data:
            raise Exception("Invalid Parameter, Part Is Required!")

        for i in data["Part"]:
            node_part = doc.createElement("Part")

            if "PartNumber" not in i:
                raise Exception("Invalid Parameter, PartNumber Is Required!")

            node_number = doc.createElement("PartNumber")
            node_number.appendChild(doc.createTextNode(str(i["PartNumber"])))

            if "ETag" not in i:
                raise Exception("Invalid Parameter, ETag Is Required!")

            node_etag = doc.createElement("ETag")
            node_etag.appendChild(doc.createTextNode(str(i["ETag"])))

            node_part.appendChild(node_number)
            node_part.appendChild(node_etag)
            root.appendChild(node_part)
        return doc.toxml("utf-8")

    @classmethod
    def xml_to_dict(cls, data, origin_str="", replace_str=""):
        """V5使用xml格式,将response中的xml转换为dict"""
        root = xml.etree.ElementTree.fromstring(data)
        xmldict = Xml2Dict(root)
        xmlstr = str(xmldict)
        if origin_str:
            xmlstr = xmlstr.replace(origin_str, replace_str)
        xmldict = eval(xmlstr)
        return xmldict

    @classmethod
    def get_id_from_xml(cls, data, name):
        """解析xml中的特定字段"""
        tree = xml.dom.minidom.parseString(data)
        root = tree.documentElement
        result = root.getElementsByTagName(name)
        # use childNodes to get a list, if has no child get itself
        return result[0].childNodes[0].nodeValue

    @classmethod
    def format_xml(cls, data, root, lst=[], parent_child=False):
        """将dict转换为xml, xml_config是一个bytes"""
        if parent_child:
            xml_config = dicttoxml(data, item_func=lambda x: x[:-1], custom_root=root, attr_type=False)
        else:
            xml_config = dicttoxml(data, item_func=lambda x: x, custom_root=root, attr_type=False)
        for i in lst:
            xml_config = xml_config.replace(cls.to_bytes(i + i), cls.to_bytes(i))
        return xml_config

    @classmethod
    def format_values(cls, data):
        """格式化headers和params中的values为bytes"""
        for i in data:
            data[i] = cls.to_bytes(data[i])
        return data

    @classmethod
    def is_json(cls, raw_data, encoding="utf-8"):
        """
        判断目标源是否为json类型
        Args:
            target_data:
        Returns:
        Examples:
            >>> list = ["1235678",{"key1":"value", "key2":"value"}]
            >>> DataKitHelper.is_json()
        """
        if isinstance(raw_data, str):
            try:
                json.loads(raw_data, encoding=encoding)
            except ValueError:
                return False
            return True
        else:
            return False

    @classmethod
    def duplicate(cls, iterable, keep=lambda x: x, key=lambda x: x, reverse=False):
        """
        保序去重
        Args:
            iterable: 去重的同时要对element做的操作
            keep: 使用哪一部分去重
            key: 是否反向去重
            reverse:
        Returns:
        Examples:
            >>> repetition_list = [3, 4, 5, 2, 4, 1]
            # 正序去重
            >>> print(DataKitHelper.duplicate(repetition_list))
            # 逆序去重
            >>> print(DataKitHelper.duplicate(repetition_list, reverse=True))
            # 指定规则去重
            >>> repetition_list = [{"a": 3, "b": 4}, {"a":3, "b": 5}]
            >>> print(DataKitHelper.duplicate(repetition_list, key=lambda x: x["a"]))
            # 去重后仅保留部分数据
            >>> print(DataKitHelper.duplicate(repetition_list, key=lambda x: x["a"], keep=lambda x: x["b"]))
        """
        result = []
        duplicator = []
        if reverse:
            iterable = reversed(iterable)
        for i in iterable:
            keep_field = keep(i)
            key_words = key(i)
            if key_words not in duplicator:
                result.append(keep_field)
                duplicator.append(key_words)
        return list(reversed(result)) if reverse else result

    @classmethod
    def chain_all(cls, iter):
        """
        连接多个序列或字典
        Args:
            iter:
        Returns:
        Examples:
            >>> print(DataKitHelper.chain_all([[1, 2], [1, 2]]))
            >>> print(DataKitHelper.chain_all([{"a": 1}, {"b": 2}]))
        """
        iter = list(iter)
        if not iter:
            return []
        if isinstance(iter[0], dict):
            result = {}
            for i in iter:
                result.update(i)
        else:
            result = reduce(lambda x, y: list(x) + list(y), iter)
        return result

    @classmethod
    def safely_json_loads(
        cls,
        value,
        object_hook: dict = None,
        parse_float=None,
        parse_int=None,
        parse_constant=None,
        object_pairs_hook=None,
        err_detail="解析JSON字符串并将其转换为Python字典失败",
    ):
        """
        返回安全的json类型
        Args:
            value (_type_): _description_
            object_hook (_type_, optional): _description_. Defaults to None.
            parse_float (_type_, optional): _description_. Defaults to None.
            parse_int (_type_, optional): _description_. Defaults to None.
            parse_constant (_type_, optional): _description_. Defaults to None.
            object_pairs_hook (_type_, optional): _description_. Defaults to None.
            err_detail (str, optional): _description_. Defaults to "解析JSON字符串并将其转换为Python字典失败".

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """
        try:
            value = json.loads(
                value,
                object_hook=object_hook,
                parse_float=parse_float,
                parse_int=parse_int,
                parse_constant=parse_constant,
                object_pairs_hook=object_pairs_hook,
            )
        except Exception as e:
            raise Exception(f"{err_detail}: {e}")
        return value

    @classmethod
    def safely_json_dumps(
        cls,
        obj,
        skipkeys=False,
        ensure_ascii=True,
        check_circular=True,
        allow_nan=True,
        indent=None,
        separators=None,
        default=None,
        sort_keys=False,
        err_detail="解析obj序列化为JSON格式字符串失败",
    ):
        try:
            value = json.dumps(
                obj,
                skipkeys=skipkeys,
                ensure_ascii=ensure_ascii,
                check_circular=check_circular,
                allow_nan=allow_nan,
                indent=indent,
                separators=separators,
                default=default,
                sort_keys=sort_keys,
            )
        except Exception as e:
            raise Exception(f"{err_detail}: {e}")
        return value

    @classmethod
    def format_html_string(cls, html):
        """
        格式化html, 去掉多余的字符,类,script等。
        Args:
            html:
        Returns:
        """
        trims = [
            (r"\n", ""),
            (r"\t", ""),
            (r"\r", ""),
            (r"  ", ""),
            (r"\u2018", "'"),
            (r"\u2019", "'"),
            (r"\ufeff", ""),
            (r"\u2022", ":"),
            (r"<([a-z][a-z0-9]*)\ [^>]*>", "<\\g<1>>"),
            (r"<\s*script[^>]*>[^<]*<\s*/\s*script\s*>", ""),
            (r"</?a.*?>", ""),
        ]
        return reduce(
            lambda string, replacement: re.sub(replacement[0], replacement[1], string),
            trims,
            html,
        )

    @classmethod
    def data_type_convert(cls, original, target_type):
        """
        数据类型转化
        Args:
            original:
            target_type:
        Returns:
        Examples:
            # 将两个相同长度的列表转换成字典
            >>> print(DataKitHelper.data_type_convert(original=(["key1","key2"],["value1","value2"]), target_type="dict"))
            # 将两个不同长度的列表转换成字典
            >>> print(DataKitHelper.data_type_convert(original=(["key1","key2","key3"],["value1","value2"]), target_type="dict"))
            # 将json转化为字典
            >>> print(DataKitHelper.data_type_convert(original='{"errcode": 401,"errs": "[POST]","data": null}', target_type="dict"))
            # 将dict转化为json
            >>> print(DataKitHelper.data_type_convert(original={'errcode': 401,'errs': 'POST','data': True}, target_type="json"))
            # 将字典列表转换为单个字典
            >>> print(DataKitHelper.data_type_convert(original=[{"errcode": 401},{"errs": "[POST]","data": True}], target_type="dict"))
        """
        if isinstance(original, dict) and target_type == "json":
            return json.dumps(original)
        elif isinstance(original, tuple) and target_type == "dict":
            is_equal_bool = len(original[0]) == len(original[1])
            if is_equal_bool:
                return dict(original)
            else:
                return dict(zip_longest(original[0], original[1]))
        elif isinstance(original, list) and target_type == "dict":
            temp = {}
            for index in original:
                temp.update(index)
            return temp
        elif cls.is_json(original) and target_type == "dict":
            return cls.safely_json_loads(original)
        return None

    @classmethod
    def parser(cls, keyword):
        """
        获取后续的字符对应前面出现过的字符的下标
        Args:
            keyword:
        Returns:
        Examples:
            >>> print(DataKitHelper.parser(keyword="55588ABCEACE"))
        """
        vals_mapping = {}
        indices_mapping = {}
        for index, i in enumerate(keyword):
            if i in vals_mapping:
                indices_mapping[index] = vals_mapping[i]
            else:
                indices_mapping[index] = None
                vals_mapping[i] = index
        return indices_mapping

    @classmethod
    def charged(cls, pay_num: int, money_num: list):
        """
        计算余额
        Args:
            pay_num:
            money_num:
        Returns:
        Examples:
            >>> print(DataKitHelper.charged(13, [1, 3, 5]))
        """
        if pay_num == 0:
            return 0
        return min(DataKitHelper.get_min(pay_num, money_num)) + 1

    @classmethod
    def get_min(cls, pay_num, money_num):
        """
        Args:
            pay_num:
            money_num:
        Returns:
        """
        for money in money_num:
            last_num = pay_num - money
            if last_num < 0:
                continue
            try:
                yield cls.charged(last_num, money_num)
            except ValueError:
                continue


class Snowflake:
    epoch = 1292978355588
    worker_id_bits = 5
    data_center_id_bits = 5
    max_worker_id = -1 ^ (-1 << worker_id_bits)
    max_data_center_id = -1 ^ (-1 << data_center_id_bits)
    sequence_bits = 12
    worker_id_shift = sequence_bits
    data_center_id_shift = sequence_bits + worker_id_bits
    timestamp_left_shift = sequence_bits + worker_id_bits + data_center_id_bits
    sequence_mask = -1 ^ (-1 << sequence_bits)

    @classmethod
    def snowflake_to_timestamp(cls, _id):
        _id = _id >> 22  # strip the lower 22 bits
        _id += cls.epoch  # adjust for twitter epoch
        _id = _id / 1000  # convert from milliseconds to seconds
        return _id

    @classmethod
    def generator(cls, worker_id, data_center_id, sleep=lambda x: time.sleep(x / 1000.0)):
        """
        生成器
        Args:
            worker_id (_type_): _description_
            data_center_id (_type_): _description_
            sleep (_type_, optional): _description_. Defaults to lambda x:time.sleep(x / 1000.0).
        Examples:
            >>> s = generator(1, 1)
            >>> for _i in range(1000000):
            ...     print(s.__next__())
        Yields:
            _type_: _description_
        """
        assert 0 <= worker_id <= cls.max_worker_id
        assert 0 <= data_center_id <= cls.max_data_center_id

        last_timestamp = -1
        sequence = 0

        while True:
            timestamp = int(time.time() * 1000)

            if last_timestamp > timestamp:
                print("clock is moving backwards. waiting until %i" % last_timestamp)
                sleep(last_timestamp - timestamp)
                continue

            if last_timestamp == timestamp:
                sequence = (sequence + 1) & cls.sequence_mask
                if sequence == 0:
                    print("sequence overrun")
                    sequence = -1 & cls.sequence_mask
                    sleep(1)
                    continue
            else:
                sequence = 0

            last_timestamp = timestamp
            yield (
                ((timestamp - cls.epoch) << cls.timestamp_left_shift)
                | (data_center_id << cls.data_center_id_shift)
                | (worker_id << cls.worker_id_shift)
                | sequence
            )
