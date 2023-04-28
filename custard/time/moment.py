# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  moment.py
@Time    :  2020/9/17 19:05
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  日期处理类库
"""

import datetime
import time


class Moment:
    @staticmethod
    def get_now_time(layout="%Y-%m-%d %H:%M:%S") -> str:
        """
        获取当前时间
        Args:
            layout: 10timestamp, 13timestamp,  else  时间类型
        Returns:
        Examples:
            >>> print(Moment.get_now_time("%Y-%m-%d %H:%M:%S"))
            >>> print(Moment.get_now_time("10timestamp"))
            >>> print(Moment.get_now_time("13timestamp"))
        """
        tim = datetime.datetime.now()
        temp = tim.strftime("%Y-%m-%d %H:%M:%S")
        # 获取10位时间戳
        if layout == "10timestamp":
            tim = int(time.mktime(time.strptime(temp, "%Y-%m-%d %H:%M:%S")))
        # 获取13位时间戳
        elif layout == "13timestamp":
            datetime_object = datetime.datetime.now()
            now_timetuple = datetime_object.timetuple()
            now_second = time.mktime(now_timetuple)
            tim = int(now_second * 1000 + datetime_object.microsecond / 1000)
        # 按传入格式获取时间
        else:
            tim = tim.strftime(layout)
        return tim

    @staticmethod
    def time_format(custom, time_format_str="%Y-%m-%d %H:%M:%S"):
        """
        降级格式化时间
        Args:
            custom:
            time_format_str:
        Returns:
        Examples:
            >>> print(Moment.time_format(custom="2022-03-30 11:05:2"))
        """
        try:
            today = datetime.datetime.strptime(custom, time_format_str)
            # 以下异常仅限于兼容目的 、开发返回的值不规范时使用、层层降级(若是还有问题就是真的格式有问题)
        except ValueError:
            blank_split = custom.split(" ")
            format_str = time_format_str[:-2] if len(blank_split) == 2 and len(custom) <= 13 else time_format_str[:-3]
            today = Moment.time_format(custom=custom, time_format_str=format_str)
        return today

    @staticmethod
    def skew_date(
        days=0,
        seconds=0,
        microseconds=0,
        milliseconds=0,
        minutes=0,
        hours=0,
        weeks=0,
        custom=None,
        time_format_str="%Y-%m-%d %H:%M:%S",
    ):
        """
        日期偏移
        Args:
            days:
            seconds:
            microseconds:
            milliseconds:
            minutes:
            hours:
            weeks:
            custom:
            time_format_str:
        Returns:
        Examples:
            >>> import random
            >>> custom_time = ["2022-03-1 11:15:15","2022-03-1 11:15",
            ... "2022-03-1 11","2022-03-1 ","2022-03-1"]
            >>> for index in custom_time:
            ...     Moment.skew_date(hours=random.randint(1,5), custom=index)
        """
        if custom is not None:
            today = Moment.time_format(custom=custom, time_format_str=time_format_str)
        else:
            today = datetime.datetime.now()
        return (today + datetime.timedelta(days, seconds, microseconds, milliseconds, minutes, hours, weeks)).strftime(
            time_format_str,
        )

    @staticmethod
    def timestamp_to_date(timestamp):
        """
        时间戳格式化为xxx年xx月xx日
        Args:
            timestamp:
        Returns:
        Examples:
            >>> print(Moment.timestamp_to_date(1603282677.5209892))
        """
        if not isinstance(timestamp, (int, float)):
            return None
        time_tuple = time.localtime(timestamp)
        specific_data = (
            str(time_tuple[0])
            + "-"
            + str(time_tuple[1])
            + "-"
            + str(time_tuple[2])
            + " "
            + str(time_tuple[3])
            + ":"
            + str(time_tuple[4])
            + ":"
            + str(time_tuple[5])
        )
        return specific_data

    @staticmethod
    def calc_time_diff(start, end):
        """
        中间时差时段计算
        Args:
            start: 开始日期
            end:   结束日期
        Returns:
        Examples:
            >>> print(Moment.calc_time_diff("2020-06-05", "2020-07-01"))
        """
        date_list = []
        begin_date = datetime.datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end, "%Y-%m-%d")
        while begin_date <= end_date:
            date_str = begin_date.strftime("%Y-%m-%d")
            date_list.append(date_str)
            begin_date += datetime.timedelta(days=1)
        return date_list

    @staticmethod
    def time_to_timestamp(format_time):
        """
        年月日时分秒转化为时间戳
        Args:
            format_time:
        Returns:
        Examples:
            >>> print(Moment.time_to_timestamp("2020-06-01 18:50:00"))
        """
        return int(time.mktime(time.strptime(format_time, "%Y-%m-%d %H:%M:%S")))

    @staticmethod
    def set_sleep_time(timestamp):
        """
        休眠xx时间
        Args:
            timestamp:
        Returns:
        """
        time.sleep(timestamp)

    @staticmethod
    def compare_time(time1, time2):
        """
        时间比较
        Args:
            time1:
            time2:
        Returns:
        """ """
        Examples:
            >>> print(Moment.compare_time("2021-08-23 17:11:37", "2021-08-22 17:11:37"))
        """
        time1 = datetime.datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
        time2 = datetime.datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")
        return time1 > time2
