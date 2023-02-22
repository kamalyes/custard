# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  inspect.py
@Time    :  2020/9/25 19:55
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""

from typing import Optional
from .logger import logger
from .exc import TableNotFoundError
from .utils import MysqlUtil


class MySqlInspect:

    def __init__(self, source_schema: Optional[str], source_url: Optional[str],
                 source_user: Optional[str], source_password: Optional[str], source_port: Optional[int],
                 target_schema: Optional[str], target_url: Optional[str],
                 target_user: Optional[str], target_password: Optional[str], target_port: Optional[int]
                 ):
        """
        检查数据结构
        source： 参考、target：目标
        Args:
            source_schema:
            source_url:
            source_user:
            source_password:
            source_port:
            target_schema:
            target_url:
            target_user:
            target_password:
            target_port:
        """
        self.source_sqlclient = MysqlUtil(source_schema, source_url, source_user, source_password, source_port)
        self.target_sqlclient = MysqlUtil(target_schema, target_url, target_user, target_password, target_port)

    def inspect_table(self, is_execute):
        """
        和标准库对比检测是否缺少某些表
        :param is_execute:
        :return:
        """

        # 获得标准库中所有表
        source_tables = self.source_sqlclient.get_tables()

        # 获得目标数据库中的所有表
        target_tables = self.target_sqlclient.get_tables()
        target_names = [t_t['table_name'] for t_t in target_tables]

        losing_tables = []
        for s_t in source_tables:
            table_name = s_t['table_name']
            if table_name in target_names:
                self.inspect_column(table_name, is_execute)
            else:
                losing_tables.append(table_name)
                if is_execute:
                    sql = self.source_sqlclient.generate_create_sql(table_name)
                    self.target_sqlclient.create_table(sql, is_execute)

        if len(losing_tables) > 0:
            logger.info(f'\nthis schema does not have these tables:\n{losing_tables}')

    def inspect_column(self, table_name, is_execute=False):
        """
        和标准库中的表对比，查看某些字段是否不同，会打印这些字段，并生成修改字段的sql
        如果is_excuse设为true，则会更新这些字段
        Args:
            table_name:
            is_execute: 是否执行

        Returns:

        """

        losing_columns = []
        change_columns = []

        source_columns = self.source_sqlclient.get_columns(table_name)
        target_columns = self.target_sqlclient.get_columns(table_name)
        if not target_columns:
            if is_execute is False:
                raise TableNotFoundError("The target table does not exist")
            sql = self.source_sqlclient.generate_create_sql(table_name)
            self.target_sqlclient.create_table(sql, is_execute)
            logger.info("The table did not exist in the target library and was added successfully")
            return True
        target_col_names = [t_c['column_name'] for t_c in target_columns]
        for s_c in source_columns:
            column_name = s_c['column_name']
            # 是否缺少字段
            if column_name in target_col_names:
                # 字段是否相同，包含类型，长度，默认值，备注
                if s_c not in target_columns:
                    change_columns.append(column_name)
                    for d_t in target_columns:
                        if s_c['column_name'] == d_t['column_name']:
                            logger.info("# ", end="")
                            logger.info(s_c)
                            logger.info("# ", end="")
                            logger.info(d_t)
                    # 更新不同的字段
                    self.target_sqlclient.update_column(s_c, 'update', table_name, is_execute)
            else:
                losing_columns.append(column_name)
                # 新增缺失的字段
                self.target_sqlclient.update_column(s_c, 'add', table_name, is_execute)
        if len(losing_columns) > 0:
            msg = '\n# this table {0} does not have these columns:\n"# " + {1}' \
                .format(table_name, str(losing_columns))
            logger.info(msg)

        if len(change_columns) > 0:
            msg = '\n# this table {0} does not have these columns:\n"# " + {1}' \
                .format(table_name, str(change_columns))
            logger.info(msg)
