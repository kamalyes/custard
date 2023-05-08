# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  system.py
@Time    :  2022/5/2 2:52 AM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import contextlib
import csv
import json
import logging
import os
import platform
import shutil
import subprocess
import zipfile

import yaml

from custard.core.processor import DataKitHelper

with contextlib.suppress(AttributeError):
    # PyYAML version >= 5.1
    yaml.warnings({"YAMLLoadWarning": False})


logger = logging.getLogger(__name__)


class SystemHand(DataKitHelper):
    @classmethod
    def shell(cls, command):
        output, errors = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).communicate()
        o = output.decode("utf-8")
        return o

    @classmethod
    def get_depend_libs(cls, file_path):
        """
        获取第三方依赖架包
        Args:
            file_path:
        Returns:
        Examples:
        """
        if cls.is_fdir(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.readlines()
                format_con = ""
                for con in set(content):
                    if "#" not in con:
                        format_con += "".join("`{}`\t".format(con.strip()))
            return format_con
        return None

    @classmethod
    def get_platform_info(cls):
        """
        获取服务运行系统的基础信息
        Returns:
        Examples:
            >>> print(SystemHand.get_platform_info())
        """
        return {
            "platform": platform.platform(),  # 获取操作系统名称及版本号
            "machine": platform.machine(),  # 计算机类型
            "node": platform.node(),  # 计算机的网络名称
            "processor": platform.processor(),  # 计算机处理器信息
            "architecture": platform.architecture(),  # 获取操作系统的位数
            "python_version": platform.python_version(),  # 获取操作系统版本号
        }

    @classmethod
    def get_pool_config(cls, work_spaces_path, target_key=None, environment="pro"):
        """
        获取驱动配置
        Args:
            work_spaces_path:
            environment:
            target_key:
        Returns:
        Examples:
            >>> print(SystemHand.get_pool_config(target_key="email"))
        """
        application_file = "application.yaml" if environment == "pro" else f"application-{environment}.yaml"
        application_file_path = os.path.join(work_spaces_path, application_file)
        if os.path.exists(application_file_path):
            temp_data = SystemHand.load_file(application_file_path)
            result = temp_data[target_key] if target_key else temp_data
            return result, application_file_path
        else:
            raise FileNotFoundError(f"未找到application配置文件,请检查以下路径是否正确:{application_file_path}")

    @classmethod
    def is_fdir(cls, fdir_path, safe_loads=False):
        """
        文件是否存在
        Args:
            fdir_path:
            safe_loads: False 安全模式下可自动创建文件: True
        Returns:
        Examples:
            >>> print(SystemHand.is_fdir(fdir_path="Not Fund"))
            >>> print(SystemHand.is_fdir(fdir_path="../inutility"))
            >>> print(SystemHand.is_fdir(fdir_path="../inutility", safe_loads=True))
        """
        isfile, isdir = os.path.isfile(fdir_path), os.path.isdir(fdir_path)
        if isfile or isdir:
            return True
        elif safe_loads is False:
            return False
        else:
            with open(fdir_path, "w", encoding="utf-8") as file:
                file.close()
            return SystemHand.is_fdir(fdir_path=fdir_path)

    @classmethod
    def load_file(cls, file_path=None, load_mode="yaml"):
        """
        加载文件
        Args:
            file_path: 文件路径
            load_mode: 加载方式
        Returns:
        """
        with open(file_path, "r", encoding="utf-8") as file:
            if load_mode == "yaml":
                return yaml.safe_load(file)
            elif load_mode == "json":
                try:
                    return json.load(file)
                except json.JSONDecodeError as ex:
                    raise TypeError("JSONDecodeError:\nfile: %s\nerror: %s" % (file_path, ex))
            elif load_mode in (".txt", ".py"):
                return file
            elif load_mode == "html":
                return DataKitHelper.format_html_string(file)
            elif load_mode == "csv":
                csv_content_list = []
                with open(file_path, encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        csv_content_list.append(row)
                return csv_content_list
            return None

    @classmethod
    def walk(cls, root_dir: str):
        """
        检索根目录,得到所有的子文件夹或子文件名
        Args:
            root_dir (str): _description_
        Examples:
            >>> root_dir = "../../custard"
            >>> SystemHand.walk(root_dir)
        """
        result = []
        dirs = [os.path.join(root_dir, index) for index in os.listdir(root_dir)]
        for index in dirs:
            for root, dirs, files in os.walk(index, topdown=False):
                file_path = [os.path.join(root, file).replace('\\', '/') for file in files]
                result += file_path
        return result

    @classmethod
    def get_current_path(cls):
        """
        获取当前文件路径
        Returns:
        Examples:
            >>> SystemHand.get_current_path()
        """
        return os.path.abspath(os.path.dirname(__file__))

    @classmethod
    def get_superior_dir(cls):
        """
        获取上级目录
        Returns:
        Examples:
            >>> SystemHand.get_superior_dir()
        """
        return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    @classmethod
    def get_dir_list(cls, file_path):
        """
        获取指定目录下所有的文件名并返回一个列表
        Args:
          file_path: 文件路径
        Returns:
        Examples:
            >>> SystemHand.get_dir_list()
        """
        current_files = os.listdir(file_path)
        all_files = []
        for file_name in current_files:
            full_file_name = os.path.join(file_path, file_name)
            all_files.append(full_file_name)
            if os.path.isdir(full_file_name):
                next_level_files = cls.get_dir_list(full_file_name)
                all_files.extend(next_level_files)
        return all_files

    @classmethod
    def tarfile(cls, file_path, method, target_path="./"):
        """
        打包文件为压缩包
        Args:
          file_path  被打包的文件路径
          target_path 目标存储的文件路径
          method    用于判断是打包单个文件还是遍历文件夹下所有的文件 single: 单个、 allie: 全部
        Returns:
        Examples:
        """
        ziplist = []
        zip_file = zipfile.ZipFile(target_path, "w")
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError("请检查file_path是否正确!")
            if method == "single":
                zip_file.write(file_path)
            if method == "allie":
                has_dir = not file_path.endswith(os.sep)
                if not has_dir:
                    raise FileNotFoundError("请检查file_path是否正确!")
                file_path = os.path.dirname(file_path)
                target_path = os.path.dirname(file_path) + os.sep + target_path
                if not os.path.exists(os.path.dirname(target_path)):
                    os.makedirs(os.path.dirname(target_path))
                # 多级目录读取
                for dirpath, _dirnames, filenames in os.walk(file_path):
                    for filename in filenames:
                        ziplist.append(os.path.join(dirpath, filename))
                for tar in ziplist:
                    zip_file.write(tar)
        except Exception as err:
            raise Exception(err)
        finally:
            zip_file.close()

    @classmethod
    def unzip(cls, method, file_path, target_path="./"):
        """
        解压多种类型的压缩包
        Args:
          method: 类型判断
          file_path: 需要解压的文件绝对路径
          zip_list: 获取压缩包内所有的文件
        Returns:

        Examples:
            >>> SystemHand.unzip(file_path="./tar.zip")
        """
        try:
            zip_file = zipfile.ZipFile(file_path)
            if method == "gzip":
                zip_file.extractall(path=target_path)
            elif method == "zip":
                zip_list = zip_file.namelist()
                for f in zip_list:
                    zip_file.extract(f, target_path)
            raise TypeError("Unknown method")
        except Exception as err:
            raise Exception(err)
        finally:
            zip_file.close()

    @classmethod
    def get_file_state(cls, file_path):
        """
        判断传入的文件状态
        Args:
          file_path: 需要解压的文件绝对路径
        Returns:
        Examples:
        """
        try:
            if os.access(file_path, os.F_OK):
                logger.info("%s:文件存在" % (file_path))
                if os.access(file_path, os.R_OK):
                    logger.info("%s:文件可读" % (file_path))
                else:
                    logger.error("%s:文件不支持可读" % (file_path))

                if os.access(file_path, os.W_OK):
                    logger.info("%s:文件可写" % (file_path))
                else:
                    logger.error("%s:文件不支持可写" % (file_path))

                if os.access(file_path, os.X_OK):
                    logger.info("%s:文件可执行" % (file_path))
                else:
                    logger.error("%s:文件不支持可执行" % (file_path))

                if os.path.isdir(file_path):
                    logger.info("%s:这是一个文件夹" % (file_path))
                else:
                    logger.info("%s:这是一个文件" % (file_path))
            else:
                logger.error("%s:文件不存在" % (file_path))
        except Exception as err:
            logger.error(err)
            raise Exception(err)

    @classmethod
    def copyfile(cls, file_path, target="./"):
        """
        复制文件
        Args:
          file_path: 需要解压的文件绝对路径
        Returns:
        Examples:
        """
        file_list = []
        if os.path.exists(file_path):
            if not os.path.exists(target):
                os.makedirs(target)
            # 多级目录读取
            for dirpath, _dirnames, filenames in os.walk(file_path):
                for filename in filenames:
                    file_list.append(os.path.join(dirpath, filename))
            for list in file_list:
                shutil.copy(list, target)
        else:
            logger.error("请检查file_path是否正确!")
        return target

    @classmethod
    def removefile(cls, file_path):
        """
        删除文件或文件夹
        Args:
          file_path: 需要解压的文件绝对路径
        Returns:
        Examples:
        """
        try:
            if os.path.exists(file_path):
                for root, dirs, files in os.walk(file_path, topdown=False):
                    # 先删除文件
                    for name in files:
                        os.remove(os.path.join(root, name))
                    # 再删除空目录
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                        # 再删除自己
                        os.rmdir(file_path)
            else:
                logger.error("请检查file_path是否正确!")
        except Exception as FileNotFoundError:
            logger.error(FileNotFoundError)

    @classmethod
    def makefile(cls, file_path):
        """
        递归创建多级文件夹
        Args:
          file_path: 需要解压的文件绝对路径
        Returns:
        Examples:
        """
        try:
            if not os.path.exists(file_path):
                os.makedirs(file_path, exist_ok=True)
                if os.path.exists(file_path):
                    logger.info("目录:%s 创建成功!!!" % (file_path))
            else:
                logger.error("%s已存在,跳过创建!" % (file_path))
        except Exception as FileNotFoundError:
            logger.error(FileNotFoundError)

    @classmethod
    def depth_scan_file(cls, catalog, file_type):
        """
        过滤xxx目录下所有的xx格式文件
        Args:
          catalog: 指定目录
          file_type 类型
        Returns:
        Examples:
        """
        file_list = os.listdir(catalog)
        yaml_files = []
        for index in range(len(file_list)):
            name, suffix = os.path.splitext(file_list[index])
            # 判断文件类型
            if suffix.replace(".", "").lower() == file_type:
                yaml_files.append("%s\\%s" % (catalog, file_list[index]))
        return yaml_files

    @classmethod
    def get_file_type(cls, file_path):
        """
        获取文件类型
        Args:
          file_path: 指定目录
        Returns:
        Examples:
        """
        if file_path is None or os.path.isfile(file_path) is False:
            raise FileNotFoundError("Please check whether the file path or file name exists")
        head, tail = os.path.split(file_path)
        name, suffix = os.path.splitext(tail)
        return suffix.lower()

    @classmethod
    def json_to_yaml(cls, json_file):
        """
        json文件格式转yaml
        """
        if json_file.endswith("json"):
            with open(json_file, "r") as pf:
                json_to_dict = cls.safely_json_loads(pf.read())
            yaml_file = json_file.replace(".json", ".yaml")
            with open(yaml_file, "w") as fp:
                yaml.safe_dump(json_to_dict, stream=fp, default_flow_style=False)
                return True
        return False

    @classmethod
    def yaml_to_json(cls, yaml_file):
        """
        yaml文件格式转json
        """
        if yaml_file.endswith("yaml"):
            with open(yaml_file, "r") as pf:
                load_data_ = yaml.load(pf, Loader=yaml.FullLoader)
                json_data_ = json.dumps(
                    load_data_,
                    sort_keys=False,
                    ensure_ascii=False,
                    indent=4,
                    separators=(",", ": "),
                )
            json_file = yaml_file.replace(".yaml", ".json")
            with open(json_file, "w") as fp:
                fp.write(json_data_)
                return True
        else:
            return False

    @classmethod
    def write_json(cls, data, json_path, method="w"):
        """
        把处理后的参数写入json文件
        :param res:
        :param json_path:
        :return:
        """
        if isinstance(data, (dict, list)):
            with open(json_path, method, encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=4)
                return True
        return False
