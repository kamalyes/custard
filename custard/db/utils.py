# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  utils.py
@Time    :  2020/9/25 19:55
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from typing import Optional

import pymysql

from .logger import logger
from .exc import TableTypeError


class MysqlUtil:

    def __init__(self, schema: Optional[str], url: Optional[str],
                 user: Optional[str], password: Optional[str], port: Optional[int]):
        self.__schema = schema
        self.__url = url
        self.__user = user
        self.__password = password
        self.__port = port
        self.__config = {
            'host': self.__url,
            'port': self.__port,
            'user': self.__user,
            'password': self.__password,
            'db': self.__schema,
            'charset': 'utf8',
            'cursorclass': pymysql.cursors.DictCursor,
        }

    def get_connection(self):
        return pymysql.connect(**self.__config)

    def execute(self, sql, params=None):
        conn = self.get_connection()
        count = 0

        try:
            with conn.cursor() as cursor:
                count = cursor.execute(sql, params)
            conn.commit()
        except Exception as ex:
            conn.rollback()
            logger.error(ex)
        finally:
            conn.close()
        return count

    def query_one(self, sql):
        conn = self.get_connection()

        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()
        return result

    def query_multi(self, sql, params=None):
        conn = self.get_connection()

        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchall()
        return result

    def get_tables(self):
        sql = 'select table_name, engine, table_collation, table_comment from information_schema.tables where ' \
              'table_schema = %s and table_type = \'{0}\''.format('BASE TABLE')
        params = self.__schema
        return self.query_multi(sql, params)

    def get_columns(self, table_name):
        sql = 'select column_name, is_nullable, column_key, ' \
              'column_default, column_comment, column_type ' \
              'from information_schema.columns where table_schema = %s and table_name = %s'
        params = (self.__schema, table_name)
        return self.query_multi(sql, params)

    def update_column(self, column, modify_type, table_name, is_execute):
        column_key = column['column_key']
        column_name = column['column_name']
        is_nullable = column['is_nullable']
        column_type = column['column_type']
        column_default = column['column_default']
        column_comment = column['column_comment']

        sql = 'alter table {0} '.format(table_name)
        if 'add' == modify_type:
            sql += 'add column {column} '.format(column=column_name)
        elif 'update' == modify_type:
            sql += 'change column {column} {column} '.format(column=column_name)
        else:
            sql += 'drop column {column}'.format(column=column_name)

        if 'drop' != modify_type:
            sql += '{column_type} '.format(column_type=column_type)

            if 'YES' == is_nullable:
                sql += 'null '
            else:
                sql += 'not null '

            if column_default is not None:
                if len(column_default) > 0:
                    sql += 'default {default} '.format(default=column_default)
                elif column_default.isspace():
                    sql += 'default \' \' '
                elif len(column_default) < 1:
                    sql += 'default \'\' '

            if column_comment is not None:
                if len(column_comment) > 0:
                    sql += 'comment "{comment}" '.format(comment=column_comment)
                elif column_comment.isspace():
                    sql += 'comment \' \' '
                elif len(column_comment) < 1:
                    sql += 'comment \'\' '

        logger.info(sql + ";\n")
        if is_execute:
            self.execute(sql)

        if column_key == "PRI":
            sql = f'alter table {table_name} add primary key ({column_name})'
            self.execute(sql)
        elif column_key == "MUL":
            raise TableTypeError("The table has foreign keys and cannot be modified manually")

    def generate_create_sql(self, table_name):
        sql = 'show create table {0}'.format(table_name)
        result = self.query_one(sql)
        return result['Create Table']

    def create_table(self, sql, is_execute):
        logger.info(sql + ";\n")
        if is_execute:
            self.execute(sql)
