#!/usr/bin/env python
# coding: utf-8
# @File    :   file.py
# @Time    :   2023/11/6 18:52
# @Author  :   guo qun X2590
# @Desc    :   None

import base64
import csv
import datetime
import glob
import hashlib
import json
import os
import pathlib
import shutil
import tarfile
from typing import Tuple, Union, TextIO
from xml.etree import ElementTree

from ruamel.yaml import YAML
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from utils.log import logger
from utils.time import timestamp2_datetime


@logger.catch
def create_dir(dir_path: str, parents: bool = True) -> Tuple[bool, str]:
    """
    创建文件夹

    Args:
        dir_path (str): 文件夹路径
        parents (bool, optional): 是否创建父文件夹. Defaults to True.
    """
    path_obj = pathlib.Path(dir_path)
    if not path_obj.is_dir():
        try:
            path_obj.mkdir(parents=parents, exist_ok=True)
        except Exception as err:
            return False, f"创建目录失败: {dir_path}, 报错信息: {err}"
        else:
            return True, "ok"
    else:
        return True, "exist"


@logger.catch
def load_yaml_from_file(yaml_file_path: str) -> tuple[str, dict]:
    """
    读取yaml文件解析为dict

    Args:
        yaml_file_path (str): yaml文件路径

    Returns:
        tuple[str, dict]: 读取解析成功, message="ok"
    """
    message = "ok"
    try:
        with open(yaml_file_path, mode="r", encoding="utf-8") as r:
            try:
                yaml = YAML(typ="base")
                # 避免ruamel自动将时间日期字符串转为datetime对象，
                config = yaml.load(r)
                return message, config
            except Exception as err:
                message = f"载入yaml数据失败: {yaml_file_path} 错误信息: {err}"
                return message, {}
    except Exception as err:
        message = f"打开yaml文件{yaml_file_path}失败: {err}"
        return message, {}


@logger.catch
def load_json_from_file(json_file_path: str):
    """
    读取json文件解析为dict

    Args:
        json_file_path (str): json文件路径
    """
    message = "ok"
    try:
        with open(json_file_path, mode="r", encoding="utf-8") as r:
            try:
                json_data = json.load(r)
                return message, json_data
            except Exception as err:
                message = f"载入json数据失败: {json_file_path} 错误信息: {err}"
                return message, {}
    except Exception as err:
        message = f"打开json文件{json_file_path}失败: {err}"
        return message, {}


@logger.catch
def read_json_lines_from_file(json_line_file: str):
    """
    从json_line文件读取数据
    :param json_line_file:
    :return:
    """
    exist_status, exist_message = verify_path_exist(json_line_file)
    if exist_status is False:
        logger.error(exist_message)
    try:
        with open(json_line_file, mode="r", encoding="utf-8") as r:
            for line in r:
                yield line
    except Exception as err:
        logger.error(f"打开文件异常: FILE: {json_line_file} ERROR: {err}")
        yield None


@logger.catch
def load_xml_from_file(xml_file_path: str):
    """
    读取xml文件
    :param xml_file_path:
    :return:
    """
    message = "ok"
    try:
        tree = ElementTree.parse(xml_file_path)
        root = tree.getroot()
    except ElementTree.ParseError as err:
        message = f"解析xmk文件{xml_file_path}失败: {err}"
        return message, None
    else:
        return message, root


@logger.catch
def move(src, dst):
    """
    移动文件或文件夹，默认覆盖策略

    Args:
        src (str): 源路径
        dst (str): 目的路径
    """
    msg = "ok"
    if pathlib.Path(src).exists():
        try:
            shutil.move(src=src, dst=dst)
        except Exception as err:
            msg = f"移动失败! src: {src}, dst: {dst}, 报错信息: {err}"
            return False, msg
        else:
            return True, msg
    else:
        msg = f"未发现文件或目录, 请确认源目标是否正确: {src}"
        return False, msg


@logger.catch
def copy(src, dst):
    """
    拷贝文件或文件夹，默认覆盖策略

    Args:
        src (str): 源路径
        dst (str): 目的路径
    """
    msg = "ok"
    if pathlib.Path(src).exists():
        try:
            shutil.copy(src=src, dst=dst)
        except Exception as err:
            msg = f"拷贝失败! src: {src}, dst: {dst}, 报错信息: {err}"
            return False, msg
        else:
            return True, msg
    else:
        msg = f"未发现文件或目录, 请确认源目标是否正确: {src}"
        return False, msg


@logger.catch
def delete(path_str):
    """
    删除目标路径

    Args:
        path_str (str): 目标路径
    """
    msg = "ok"
    pathlib_obj = pathlib.Path(path_str)
    if pathlib_obj.exists():
        try:
            if pathlib_obj.is_dir():
                shutil.rmtree(path_str)
            elif pathlib_obj.is_file():
                os.remove(path_str)
        except Exception as err:
            msg = f"删除失败! {path_str}, 错误信息: {err}"
            return False, msg
        else:
            return True, msg
    else:
        msg = f"未发现文件或目录, 请确认目标是否正确: {path_str}"
        return False, msg


@logger.catch
def get_md5(object_data, is_file=False) -> tuple[bool, str]:
    """
    计算文件或字符串md5

    Args:
        object_data (str): 待计算的数据对象，可以是文件路径或字符串
        is_file (bool, optional): [description]. Defaults to False.

    Returns:
        (tuple): tuple containing:
            status (bool): 结果状态
            result (str): 结果内容
    """
    md5_obj = hashlib.md5()
    if is_file:
        if os.path.isfile(object_data):
            with open(object_data, "rb") as r:
                while True:
                    data = r.read(8096)
                    if not data:
                        break
                    md5_obj.update(data)
        else:
            return False, f"file not exist: {object_data}"
    else:
        md5_obj.update(object_data.encode("utf-8"))
    md5_str = md5_obj.hexdigest()
    return True, md5_str


@logger.catch
def get_base64(object_data, is_file=False):
    """
    获取文件或字符串的base64编码

    Args:
        object_data (str): 文件路径或字符串
        is_file (bool, optional): [description]. Defaults to False.

    Returns:
        (tuple): tuple containing:
            status (bool): 结果状态
            result (str): 结果内容
    """
    if is_file:
        if os.path.isfile(object_data):
            with open(object_data, "rb") as r:
                base64_str = base64.b64encode(r.read()).decode("ascii")
        else:
            return False, f"file not exist: {object_data}"
    else:
        base64_str = base64.b64encode(str.encode(object_data)).decode("ascii")
    return True, base64_str


@logger.catch
def base64_to_file(base64_str, dst_file_path):
    """
    把base64编码字符串反编码为文件存储

    Args:
        base64_str (str): base64字符串
        dst_file_path (str): 存储文件袋路径

    Returns:
        (tuple): tuple containing:
            status (bool): 结果状态
            result (str): 结果内容
    """
    if pathlib.Path(dst_file_path).exists():
        return False, f"存储文件路径已存在，请检查: {dst_file_path}"
    else:
        origin_data = base64.b64decode(base64_str)
        with open(dst_file_path, mode="wb") as w:
            w.write(origin_data)
        return True, "ok"


@logger.catch
def find_all_files(goal_path):
    """
    递归获取指定目录下的所有文件绝对路径，返回一个生成器

    Args:
        goal_path (str): 目标路径
    """
    for root, _, file_list in os.walk(goal_path):
        for f in file_list:
            yield pathlib.Path(root).joinpath(f).absolute()


@logger.catch
def search_in_path(root_path, goal_glob, recursive=True):
    """
    根据给定的通配符搜索符合要求的文件，返回一个生成器

    Args:
        root_path (str): 需要搜索的目标路径
        goal_glob (str): 目标文件袋通配符表达式
        recursive (bool, optional): 是否需要递归查找所有子目录. Defaults to True.
    """
    glob_str = str(pathlib.Path.joinpath(root_path, "**", goal_glob))
    result = glob.glob(glob_str, recursive=recursive)
    return (pathlib.Path(each).absolute() for each in result)


@logger.catch
def get_files_and_folders(directory) -> tuple[list, list]:
    """
    获取目录下的文件和文件夹

    Args:
        directory (str): 指定目录

    Returns:
        tuple(list, list): (files, folders)
    """
    files = []
    folders = []

    for entry in os.scandir(directory):
        if entry.is_file():
            files.append(entry.path)
        elif entry.is_dir():
            folders.append(entry.path)

    return files, folders


@logger.catch
def get_file_creation_date(file_path):
    """
    获取文件或目录的创建日期

    Args:
        file_path (str): 文件路径

    Returns:
        datetime: 日期对象
    """
    # 获取文件的状态信息
    stat = os.stat(file_path)
    # 获取文件的创建时间戳
    creation_timestamp = stat.st_ctime
    # 转换为可读的日期时间格式
    status, message, creation_date = timestamp2_datetime(creation_timestamp)
    return status, message, creation_date


@logger.catch
def verify_path_exist(path_str):
    """
    核实目录应当存在

    Args:
        path_str (str): 目录字符串
    """
    if pathlib.Path(path_str).exists():
        return True, "ok"
    else:
        msg = f"期望目录存在，但目录不存在: {path_str}"
        return False, msg


@logger.catch
def verify_path_not_exist(path_str):
    """
    核实目录应当不存在

    Args:
        path_str (str): 目录字符串
    """
    if pathlib.Path(path_str).exists():
        msg = f"期望目录不存在，但目录已存在: {path_str}"
        return False, msg
    else:
        return True, "ok"


@logger.catch
def verify_path_exist_multi(path_array):
    """
    批量核实目录应当存在

    Args:
        path_array (list): 路径数组

    Returns:
        (tuple): tuple containing:
            status (bool): 结果状态
            result (str): 结果内容
    """
    for each in path_array:
        status, msg = verify_path_exist(each)
        if status is False:
            return status, msg
    return True, "ok"


@logger.catch
def verify_path_not_exist_multi(path_array):
    """
    批量核实目录应当不存在

    Args:
        path_array (list): 路径数组

    Returns:
        (tuple): tuple containing:
            status (bool): 结果状态
            result (str): 结果内容
    """
    for each in path_array:
        status, msg = verify_path_not_exist(each)
        if status is False:
            return status, msg
    return True, "ok"


def split_path(path: str):
    """
    把一个目录字符串完全切分为每个部分
    :param path:
    :return:
    """
    parts = []
    while path != "":
        path, part = os.path.split(path)
        if part != "":
            parts.insert(0, part)
    return parts


@logger.catch
def targz_extract(targz_file, extract_path):
    """
    解压tar.gz压缩包

    Args:
        targz_file (str): tar.gz压缩包路径
        extract_path (str): 解压路径
    """
    try:
        with tarfile.open(targz_file) as f:
            f.extractall(extract_path)
    except Exception as err:
        return False, err
    else:
        return True, "ok"


@logger.catch
def targz_archive(dir_to_archive, archive_filename_path):
    try:
        # 创建tar.gz文件

        # 解压出现了 @PaxHeader 目录是由于在压缩过程中，使用了 pax 格式，而该格式包含了更多的元数据，如文件权限和时间戳等，从而导致在解压缩时出现了 @PaxHeader 目录。
        # 参见官方文档： https://docs.python.org/zh-cn/3/library/tarfile.html
        # tarfile.USTAR_FORMAT
        # POSIX.1-1988 (ustar) 格式。
        # tarfile.GNU_FORMAT
        # GNU tar 格式。
        # tarfile.PAX_FORMAT
        # POSIX.1-2001 (pax) 格式。
        # tarfile.DEFAULT_FORMAT
        # 用于创建归档的默认格式。 目前为 PAX_FORMAT。
        # 在 3.8 版更改: 新归档的默认格式已更改为 PAX_FORMAT 而不再是 GNU_FORMAT。
        with tarfile.open(
            archive_filename_path, mode="w:gz", format=tarfile.GNU_FORMAT
        ) as tar:
            # 并目录作为 archive_name
            archive_name = pathlib.Path(dir_to_archive).name
            tar.add(dir_to_archive, archive_name)
    except Exception as err:
        return False, err
    else:
        return True, "ok"


@logger.catch
def json2file(json_object: Union[list, dict], dst_file_path):
    """
    将json数据写入文件
    Args:
        json_object:
        dst_file_path:

    Returns:

    """
    try:
        with open(dst_file_path, mode="w", encoding="utf-8") as w:
            json.dump(json_object, fp=w, ensure_ascii=False)
    except Exception as err:
        return False, err
    else:
        return True, "ok"


@logger.catch
def save_jl_data2csv(json_line_data: list[dict], save_path: str = None):
    """
    保存json line数据到csv文件
    :param json_line_data:
    :param save_path:
    :return:
    """
    if len(json_line_data) >= 1:
        fieldnames = list(json_line_data[0].keys())
        with open(save_path, mode="w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            # 写入列名称
            writer.writeheader()
            # 写入数据
            writer.writerows(json_line_data)
    else:
        logger.warning(f"待存储到csv文件的json_line_data为空: save_path: {save_path}")


@logger.catch
def save_jl_data2xlsx(json_line_data: list[dict], save_path: str = None):
    """
    保存json line数据到xlsx文件
    :param json_line_data:
    :param save_path:
    :return:
    """
    if len(json_line_data) >= 1:
        fieldname_array = list(json_line_data[0].keys())
        workbook = Workbook()
        sheet = workbook.active
        # 写入列名称
        for col_num, fieldname in enumerate(fieldname_array, 1):
            sheet.cell(row=1, column=col_num, value=fieldname)
            sheet.column_dimensions[get_column_letter(col_num)].width = min(
                len(fieldname) * 2, 100
            )
        # 写入数据
        for row_num, row_data in enumerate(json_line_data, 2):
            for col_num, fieldname in enumerate(fieldname_array, 1):
                cell_value = row_data.get(fieldname, "")
                if (
                    isinstance(cell_value, dict)
                    or isinstance(cell_value, list)
                    or isinstance(cell_value, tuple)
                ):
                    # 输出的dict、list、tuple变为JSON，更容易阅读与格式化
                    try:
                        cell_value = json.dumps(cell_value, ensure_ascii=False)
                    except json.JSONDecodeError as err:
                        logger.warning(
                            f"save_jl_data2xlsx cell_value转为json异常: {err}"
                        )
                        cell_value = str(cell_value)
                sheet.cell(row=row_num, column=col_num, value=cell_value)
        workbook.save(save_path)
    else:
        logger.warning(f"待存储到csv文件的json_line_data为空: save_path: {save_path}")


@logger.catch
def save_dict2jl(json_data, save_path=None, save_file_obj=None, mode="w", code="utf-8"):
    """将字典存储为jl文件(即json line文件)

    :param json_data: 需要存储的数据
    :type json_data: List(dict) 或 dict
    :param save_path: (可选)文件保存路径
    :type save_path: str
    :param save_file_obj: object (可选)已经打开的写文本模式的文件对象
    :param mode: (可选)文件打开模式默认为w, 还可以用w+
    :type mode: str
    :param code: (可选)默认保存编码为utf-8
    :type code: str
    """
    if save_file_obj is None:
        with open(save_path, mode=mode, encoding=code) as w:
            __save_dict2jl(dict_data=json_data, w_obj=w)
    else:
        __save_dict2jl(dict_data=json_data, w_obj=save_file_obj)


@logger.catch
def __save_dict2jl(dict_data: Union[list, dict], w_obj: TextIO):
    """
    将字典存储为jl文件(jl就是json line)
    :param dict_data: dict或list(dict)
    :param w_obj: 文件保存句柄对象
    :return:
    """
    if isinstance(dict_data, dict):
        line = json.dumps(dict_data, ensure_ascii=False) + "\n"
        w_obj.write(line)
    elif isinstance(dict_data, list):
        for line in dict_data:
            if isinstance(line, dict):
                line = json.dumps(line, ensure_ascii=False) + "\n"
                try:
                    w_obj.write(line)
                except Exception as err:
                    logger.exception("无法写入文件: {}".format(err))
            else:
                logger.error(
                    "无法写入文件: {}，内容不是dict {!r}".format(w_obj.name, line)
                )
    else:
        logger.error("无法写入文件: {}，内容不是dict {}".format(w_obj.name, dict_data))


if __name__ == "__main__":
    res = split_path(
        r"HETU_TAOSHA-1.2.26-install-20241129\\HETU_TAOSHA-Onekey-install-1.2.26-allsystem-20241129\\HETU_TAOSHA-Onekey-install-1.2.26\\HETU_IAO_TAOSHA_MODELS-install-runtime-2.1.4-allsystem-20241129\\HETU_IAO_TAOSHA_MODELS-install-2.1.4\\package\\HETU_IAO_TAOSHA_LABEL_MODELS-install-runtime-2.1.4-allsystem-20241129\\HETU_IAO_TAOSHA_LABEL_MODELS-install-2.1.4\\models\\model_template_30001\\model_13352\\model_13352.xml"
    )
    print(res)
