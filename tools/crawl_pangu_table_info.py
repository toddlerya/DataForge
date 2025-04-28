#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/24 17:27 
# @Author   : guoqun X2590
# @FileName : crawl_pangu_table_info.py
# @Project  : DataForge


# https://172.21.4.42:11018/catalog/catalog/query/getEntityDetail?entityId=1355

import pathlib
import requests
import json

import urllib3
from urllib3.exceptions import InsecureRequestWarning

from tools.pang_config import pangu_headers

urllib3.disable_warnings(InsecureRequestWarning)


def crawl(entity_id: str):
    """
    根据entity_id采集盘古元数据信息
    Args:
        entity_id:
    Returns:

    """
    url = f"https://172.21.4.42:11018/catalog/catalog/query/getEntityDetail"
    payload = {"entityId": entity_id}

    r = requests.get(url=url, params=payload, headers=pangu_headers, verify=False)
    if r.status_code != 200:
        raise r.raise_for_status()
    resp_json = r.json()
    return resp_json


if __name__ == '__main__':
    from tools.table_meta_info_clear import clear
    from tools.pang_config import bash_path
    from tools.crawl_dict_info import get_dict_values_by_keyword

    # table_entity_info获取方式 select id, name, ename from base_entity_info where positionid = 3 -- positionid=3: ORC;
    # positionid=4: FRC and ename in ('ODS_BEIAN_MAINBODY_INFO', 'ODS_BEIAN_WEBSITE_INFO', 'ODS_BEIAN_APPINFO',
    # 'ODS_BEIAN_MIMIAPP_INFO', 'ODS_BEIAN_MARKETPLACE_INFO', 'ODS_BEIAN_SERVICE_PROVIDER_INFO',
    # 'ODS_BEIAN_SAFETY_ASSESSMENT', 'ODS_BEIAN_ACCESS_WEBSITE', 'ODS_BEIAN_ACCESS_APP', 'ODS_BEIAN_ACCESS_MINIAPP',
    # 'ODS_BEIAN_ACCESS_DATAVERIFICATION', 'ODS_BEIAN_APPLICANT_INFO');
    table_entity_info = [
        {
            "id": 3514,
            "name": "主体信息",
            "ename": "ODS_BEIAN_MAINBODY_INFO"
        },
        {
            "id": 3515,
            "name": "网站信息",
            "ename": "ODS_BEIAN_WEBSITE_INFO"
        },
        {
            "id": 3516,
            "name": "APP信息",
            "ename": "ODS_BEIAN_APPINFO"
        },
        {
            "id": 3517,
            "name": "小程序信息",
            "ename": "ODS_BEIAN_MIMIAPP_INFO"
        },
        {
            "id": 3518,
            "name": "应用市场信息",
            "ename": "ODS_BEIAN_MARKETPLACE_INFO"
        },
        {
            "id": 3519,
            "name": "服务商信息",
            "ename": "ODS_BEIAN_SERVICE_PROVIDER_INFO"
        },
        {
            "id": 3520,
            "name": "安全评估信息",
            "ename": "ODS_BEIAN_SAFETY_ASSESSMENT"
        },
        {
            "id": 3521,
            "name": "接入网站信息",
            "ename": "ODS_BEIAN_ACCESS_WEBSITE"
        },
        {
            "id": 3522,
            "name": "接入APP信息",
            "ename": "ODS_BEIAN_ACCESS_APP"
        },
        {
            "id": 3523,
            "name": "接入小程序信息",
            "ename": "ODS_BEIAN_ACCESS_MINIAPP"
        },
        {
            "id": 3524,
            "name": "接入数据核验信息",
            "ename": "ODS_BEIAN_ACCESS_DATAVERIFICATION"
        },
        {
            "id": 3525,
            "name": "申请人信息",
            "ename": "ODS_BEIAN_APPLICANT_INFO"
        }
    ]
    fhwa_dict_code_data = dict()
    for item in table_entity_info:
        print(item)
        data = crawl(entity_id=item.get("id"))
        if data.get("status", 0) != 200:
            print(data)
            continue
        # 存储字段信息
        save_data_file = bash_path.joinpath("export_data", "pangu", "bxf", f'{item.get("ename")}.json')
        with open(save_data_file, mode="w",
                  encoding="utf-8") as w:
            json.dump(data, w, ensure_ascii=False)
        clear_data_file = bash_path.joinpath("output", "pangu", "bxf", f'{item.get("ename")}.json')
        clear(input_file=save_data_file, output_file=clear_data_file)
        # 获取表字段涉及的字典信息
        for field in data.get("data", {}).get("fieldInfoList", [{}]):
            field_dic: str = field.get("dic", "").strip()
            if field_dic != "":
                fhwa_dict_result = get_dict_values_by_keyword(keyword=field_dic)
                fhwa_dict_code = fhwa_dict_result.get("fhwa_code", "")
                with open(bash_path.joinpath("export_data", "pangu", "dict_code", f"{field_dic}_{fhwa_dict_code}.json"),
                          mode="w",
                          encoding="utf-8") as dict_w:
                    json.dump(fhwa_dict_result, dict_w, ensure_ascii=False)
                with open(bash_path.joinpath("output", "pangu", "dict_code", f"{field_dic}_{fhwa_dict_code}.json"),
                          mode="w", encoding="utf-8") as dict_w_brief:
                    json.dump(fhwa_dict_result.get("brief_data", {}), dict_w_brief, ensure_ascii=False)