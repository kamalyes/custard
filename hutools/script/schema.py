# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  schema.py
@Time    :  2021/10/22 20:16
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""


class JsonToSchema:

    # 遍历列表
    @classmethod
    def get_object_data(cls, dict_data):
        # 外层dict
        schema_data = {}
        # 遍历字典中的key
        for dict_data_k in dict_data.keys():
            # 如果value是字符串/数字/布尔值/小数/None,则直接存入schema_data
            if type(dict_data[dict_data_k]) in (str, int, bool, float, list):
                if type(dict_data[dict_data_k]) is str:
                    schema_data[dict_data_k] = {"type": "string"}
                    continue
                if type(dict_data[dict_data_k]) is int:
                    schema_data[dict_data_k] = {"type": "integer"}
                    continue
                if type(dict_data[dict_data_k]) is bool:
                    schema_data[dict_data_k] = {"type": "boolean"}
                    continue
                if type(dict_data[dict_data_k]) is float:
                    schema_data[dict_data_k] = {"type": "number"}
                    continue

                if type(dict_data[dict_data_k]) is list:
                    schema_data[dict_data_k] = {"type": "array"}
                    continue
            # 空判断
            if dict_data[dict_data_k] is None:
                schema_data[dict_data_k] = {"type": "null"}
                continue
            elif type(dict_data[dict_data_k]) == dict:
                # dict格式则递归调用
                schema_temp = {"type": "object", 'properties': cls.get_object_data(dict_data[dict_data_k])}
                # 如果value为dict or list则使用key进行嵌套
                schema_data[dict_data_k] = schema_temp

            else:
                print(dict_data[dict_data_k] is None)
        return schema_data

    @staticmethod
    def get_schema(target_data):
        """
        获取schema
        Args:
            target_data:

        Returns:

        """
        return {'type': "object", 'properties': JsonToSchema.get_object_data(data)}


if __name__ == '__main__':
    data = {"success": True, "code": 10000, "message": "操作成功", "money": 6.66, "address": None,
            "data": {"": "tom", "dict_list": ["1566", 55]},
            "luckyNumber": [6, 8, 9]}
    schema = JsonToSchema.get_schema(target_data=data)
    print(f"{data}\n{schema}")
    import jsonschema

    jsonschema.validate(data, schema)
