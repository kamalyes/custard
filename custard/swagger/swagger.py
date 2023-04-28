# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  swagger.py
@Time    :  2022/7/18 10:16
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import copy
import json
import re
import urllib.parse
import uuid


class Swagger2:
    def __init__(self, source, deep=5):
        self.source = source
        self.deep = deep

        self.__scheme = self.schemes[0]
        self.__host = self.source.get("host") or "localhost"

    def __property__(self, prop):
        if isinstance(prop, dict):
            _type = prop.get("type")
            _format = prop.get("format")
            _example = prop.get("example")
            if _example:
                prop = _example
            elif _type == "integer":
                prop = 0
            elif _type == "number":
                prop = 1.75
            elif _type == "boolean":
                prop = True
            elif _type == "string":
                if _format in [None, "byte", "binary", "password"]:
                    prop = "string"
                elif _format == "date":
                    prop = "1970-01-01"
                elif _format == "date-time":
                    prop = "1970-01-01 00:00:00"
            elif _type == "file":
                prop = "file.txt"
            elif _type == "array":
                prop = []

        return prop

    @property
    def schemes(self):
        return self.source.get("schemes") or ["http"]

    @property
    def scheme(self):
        return self.__scheme

    @scheme.setter
    def scheme(self, value):
        self.__scheme = value

    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self, value):
        self.__host = value

    @property
    def base_path(self):
        return self.source.get("base_path") or "/"

    @property
    def models(self):
        ref_results = {}

        definitions = copy.deepcopy(self.source.get("definitions"))
        for _ in range(self.deep):
            for key in list(definitions.keys()):
                properties = definitions[key].get("properties")
                if properties:
                    ref_keys = re.findall(r'"#/definitions/(.+?)"', json.dumps(properties, ensure_ascii=False))
                    if ref_keys and len(ref_keys) > 0:
                        if set(ref_results.keys()).issuperset(set(ref_keys)):
                            for prop_name, prop in properties.items():
                                ref_key = prop.get("$ref")
                                if ref_key:
                                    properties[prop_name] = ref_results.get(ref_key.split("/").pop())
                                else:
                                    properties[prop_name] = self.__property__(prop)
                            ref_results.update({key: properties})
                            del definitions[key]
                    else:
                        for prop_name, prop in properties.items():
                            properties[prop_name] = self.__property__(prop)
                        ref_results.update({key: properties})
                        del definitions[key]
                else:
                    ref_results.update({key: {}})
                    del definitions[key]
            # 无模型停止递归
            if len(definitions) == 0:
                break
        # if len(definitions) > 0:
        #     raise IncompleteModelError('The model is incomplete. Please adjust the deep value of the swagger object.')
        return ref_results

    @property
    def apis(self):
        models = self.models

        api_results = []

        for path, forms in self.source.get("paths").items():
            for method, form in forms.items():
                # 接口名称
                name = form.get("summary")
                # 内容类型
                content_type = form.get("consumes") or [""]
                content_type = content_type[0]
                # 接口路径
                _path = (self.base_path + path).replace("//", "/")
                # 拼接后的URL
                url = urllib.parse.urlunparse((self.scheme, self.host, _path, None, None, None))
                _api = {
                    "id": uuid.uuid4().hex,
                    "name": name,
                    "method": method,
                    "path": _path,
                    "url": url,
                    "headers": {"Content-Type": content_type},
                    "paths": {},
                    "query": {},
                    "json": {},
                    "form": {},
                    "formData": {},
                }
                # 参数提取
                parameters = form.get("parameters")
                if parameters:
                    for param in parameters:
                        _in = param.get("in")
                        param_name = param.get("name")
                        param_value = self.__property__(param)

                        if isinstance(param_value, dict):
                            schema = param_value.get("schema")
                            if schema and schema.get("type") == "array":
                                param_value = []
                            else:
                                ref_key = re.search(r'"#/definitions/(.+?)"', json.dumps(schema, ensure_ascii=False))
                                if ref_key:
                                    param_value = models.get(ref_key.group(1))

                        if _in == "header":
                            _api.get("headers").update({param_name: param_value})
                        elif _in == "path":
                            _api.get("paths").update({param_name: param_value})
                        elif _in == "query":
                            _api.get("query").update({param_name: param_value})
                        elif _in == "body":
                            _api.update({"json": param_value})
                        elif _in == "formData":
                            if "multipart/form-data" in content_type:
                                _api.get("formData").update({param_name: param_value})
                            else:
                                _api.get("form").update({param_name: param_value})

                api_results.append(_api)
        return api_results
