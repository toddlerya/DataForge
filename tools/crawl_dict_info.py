#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/25 11:39
# @Author   : guoqun X2590
# @FileName : crawl_dict_info.py
# @Project  : DataForge

import requests

import urllib3
from urllib3.exceptions import InsecureRequestWarning

from tools.pang_config import pangu_headers

urllib3.disable_warnings(InsecureRequestWarning)


def get_dict_fh_code_by_keyword(keyword: str) -> dict:
    """
    根据字典中文名称获取FHWA代号
    Args:
        keyword:

    Returns:

    """
    url = "https://172.21.4.42:11018/standard/standard/dictionary/list"
    if keyword == "主办单位性质-子级":
        keyword = "主办单位性质子分类"
    payload = {"keyword": keyword, "parentCode": -1}
    r = requests.get(url=url, params=payload, headers=pangu_headers, verify=False)
    if r.status_code != 200:
        raise r.raise_for_status()
    data = r.json()
    if data.get("status", 0) != 200:
        print(f"获取字典代码异常: {data}")
        return {}
    return data.get("data", [{}])[0]


def get_dict_values_by_keyword(keyword: str) -> dict:
    """
    根据字典名称获取字典值
    Args:
        keyword:

    Returns:

    """
    fhwa_code_data = get_dict_fh_code_by_keyword(keyword=keyword)
    if fhwa_code_data == {}:
        return {}

    url = "https://172.21.4.42:11018/standard/standard/dictionary/all"
    payload = {
        "id": fhwa_code_data.get("id"),
        "nlevel": fhwa_code_data.get("nlevel"),
        "code": fhwa_code_data.get("code"),
        "userDefine": 0,
        "pagesize": 10,
        "pageno": 1,
    }
    r = requests.get(url=url, params=payload, headers=pangu_headers, verify=False)
    if r.status_code != 200:
        raise r.raise_for_status()
    data = r.json()
    if data.get("status", 0) != 200:
        print(f"获取字典代码异常: {data}")
        return {}
    temp_result = data.get("data", {}).get("datas", [{}])
    brief_data = [{"name": ele.get("name"), "id": ele.get("id")} for ele in temp_result]
    result = {
        "fhwa_code": fhwa_code_data.get("id"),
        "brief_data": brief_data,
        "fhwa_code_data": fhwa_code_data,
        "raw_dict_data": data,
    }
    return result


if __name__ == "__main__":
    import json

    # fhwa_code = get_dict_fh_code_by_keyword(keyword="网站规模等级类型")
    # print(fhwa_code)
    __result = get_dict_values_by_keyword(keyword="网站主办单位性质代码")
    print(json.dumps(__result, ensure_ascii=False, indent=2))
