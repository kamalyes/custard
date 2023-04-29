# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  parse.py
@Time    :  2020/9/25 19:55
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import argparse
import json
import warnings
from http.cookies import SimpleCookie
from shlex import split
from urllib.parse import urlparse

from w3lib.http import basic_auth_header

from custard.core.processor import DataKitHelper


class CurlParser(argparse.ArgumentParser, DataKitHelper):
    def error(self, message):
        error_msg = "There was an error parsing the curl command: {}".format(message)
        raise ValueError(error_msg)


# 自定义解析的内容
curl_parser = CurlParser()
curl_parser.add_argument("url")
curl_parser.add_argument("-H", "--header", dest="headers", action="append")
curl_parser.add_argument("-X", "--request", dest="method", default="get")
curl_parser.add_argument("-d", "--data-raw", dest="data", default=None)
curl_parser.add_argument("-f", "--form", "--data-urlencode", dest="form", action="append")
curl_parser.add_argument("-u", "--user", dest="auth")

safe_to_ignore_arguments = [
    ["--location"],
    ["--compressed"],
    # `--compressed` argument is not safe to ignore, but it's included here
    # because the `HttpCompressionMiddleware` is enabled by default
    ["-s", "--silent"],
    ["-v", "--verbose"],
    ["-#", "--progress-bar"],
]
for argument in safe_to_ignore_arguments:
    curl_parser.add_argument(*argument, action="store_true")


def curl_to_request_kwargs(curl_command, ignore_unknown_options=True):
    """Convert a cURL command syntax to Request kwargs.
    :param str curl_command: string containing the curl command
    :param bool ignore_unknown_options: If true, only a warning is emitted when
    cURL options are unknown. Otherwise raises an error. (default: True)
    :return: dictionary of Request kwargs
    """
    curl_args = split(curl_command)
    if curl_args[0] != "curl":
        raise ValueError('A curl command must start with "curl"')
    parsed_args, argv = curl_parser.parse_known_args(curl_args[1:])
    if argv:
        msg = "Unrecognized options: {}".format(", ".join(argv))
        if ignore_unknown_options:
            warnings.warn(msg)
        else:
            raise ValueError(msg)
    url = parsed_args.url
    # curl automatically prepends 'http' if the scheme is missing, but Request
    # needs the scheme to work
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = "http://" + url
    result = {"method": parsed_args.method.upper(), "url": url}
    headers, forms, cookies, content_type = [], [], {}, "application/json"
    for header in parsed_args.headers or ():
        name, val = header.split(":", 1)
        name = name.strip()
        val = val.strip()
        name_title = name.title()
        if name_title == "Content-Type":
            content_type = val
        if name_title == "Cookie":
            for name, morsel in SimpleCookie(val).items():
                cookies[name] = morsel.value
        else:
            headers.append((name, val))
    for form in parsed_args.form or ():
        name, val = form.split("=", 1)
        name = name.strip('"')
        val = val.strip('"')
        forms.append((name, val))
    if parsed_args.auth:
        user, password = parsed_args.auth.split(":", 1)
        headers.append(("Authorization", basic_auth_header(user, password)))
    if headers:
        result["headers"] = headers
    if cookies:
        result["cookies"] = cookies
    if parsed_args.data:
        body_ = DataKitHelper.safely_json_loads(parsed_args.data)
        result["body"] = body_
    if forms:
        if content_type == "application/x-www-form-urlencoded":
            result["data-urlencode"] = forms
        else:
            result["form"] = forms
    # print("---parsed_curl_dumps---", json.dumps(result))
    return result


if __name__ == "__main__":
    get_command = """
                  curl --location --request GET '{{baseUrl}}/api/v1/ps/get?l=22&kj=5' \
                  --header 'ab: 11' \
                  --header 'fg: dfg' \
                  --header "Content-Type: text/plain" \
                  --data-raw '{"s": 0}'
                """
    form_command = """
                curl --location --request POST 'https://xxx/index?act=util&op=inital_checked_staff' \
                --header 'Cookie: PHPSESSID=v93jf5ecmgct5lf2fohe9v6p9s' \
                --form 'member_id="106767"' \
                --form 'key="URJoSEz2Fb8NwzNNGfplbYlolW7wph19UiqdLNkhlq4tdmbV98R9IwB3CyhPSrik"'
                """
    data_urlencode_command = """
                curl --location --request POST 'https://xxx/index?act=util&op=inital_checked_staff' \
                --header 'Cookie: PHPSESSID=v93jf5ecmgct5lf2fohe9v6p9s' \
                --header 'Content-Type: application/x-www-form-urlencoded'
                --data-urlencode 'member_id="106767"' \
                --data-urlencode 'key="URJoSEz2Fb8NwzNNGfplbYlolW7wph19UiqdLNkhlq4tdmbV98R9IwB3CyhPSrik"'
                """
    post_command = """
                curl --location --request POST 'https://xxx?act=util&op=test_staff&api_key=URJoSyhPSrik' \
                --header 'Content-Type: application/json' \
                --header 'Cookie: PHPSESSID=9ec54h4skg93n667bu4gl4jq37; XDEBUG_SESSION=1' \
                --data-raw '{
                    "str": "ABC的235678",
                    "number": 13273298163,
                    "dict": {"dict-1":"dict123","dict-2":"dict567"},
                    "array": [{"list-1":"list123","list-2":"list567"}],
                    "boolean": true,
                    "undefined": null
                }'"""
    get_ = curl_to_request_kwargs(get_command)
    form_ = curl_to_request_kwargs(form_command)
    post_ = curl_to_request_kwargs(post_command)
    data_urlencode_ = curl_to_request_kwargs(data_urlencode_command)
