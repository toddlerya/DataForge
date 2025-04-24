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


def crawl(entity_id: str, cookie: str):
    """
    根据entity_id采集盘古元数据信息
    Args:
        entity_id:
        cookie:
    Returns:

    """
    url = f"https://172.21.4.42:11018/catalog/catalog/query/getEntityDetail"
    payload = {"entityId": entity_id}
    headers = {"Cookie": cookie}
    r = requests.get(url=url, params=payload, headers=headers, verify=False)
    if r.status_code != 200:
        raise r.raise_for_status()
    resp_json = r.json()
    return resp_json


if __name__ == '__main__':
    from tools.table_meta_info_clear import clear

    bash_path = pathlib.Path(r"F:\GITLAB\DataForge")
    cookie_data = "contextPath=/catalog; userToken=a4d587b8de914f50a4064ea25a72f66b; appToken=18a687bb7b9d4e4db6fb70bf99eb81e8; JSESSIONID=463E06C3DD672252069C91EB61629BE9; contextPath=/; citycode=330100; appId=pangu; topoptid=pangu; loginIp=10.0.23.57; loginMac=A4-BB-6D-43-BE-0D; JSESSIONID=49DADF6B91C261DA761666BEC2C988D8; userToken=a4d587b8de914f50a4064ea25a72f66b; appToken=18a687bb7b9d4e4db6fb70bf99eb81e8; sessiongovern=79A1E553E6334C24C7C1A58A522D8453"
    table_entity_info = [
        {
            "template_id": 3874,
            "name": "网站信息",
            "ename": "ODS_BEIAN_WEBSITE_INFO"
        },
        {
            "template_id": 3875,
            "name": "安全评估信息",
            "ename": "ODS_BEIAN_SAFETY_ASSESSMENT"
        },
        {
            "template_id": 3876,
            "name": "接入APP信息",
            "ename": "ODS_BEIAN_ACCESS_APP"
        },
        {
            "template_id": 3877,
            "name": "申请人信息",
            "ename": "ODS_BEIAN_APPLICANT_INFO"
        },
        {
            "template_id": 3878,
            "name": "服务商信息",
            "ename": "ODS_BEIAN_SERVICE_PROVIDER_INFO"
        },
        {
            "template_id": 3879,
            "name": "应用市场信息",
            "ename": "ODS_BEIAN_MARKETPLACE_INFO"
        },
        {
            "template_id": 3880,
            "name": "接入网站信息",
            "ename": "ODS_BEIAN_ACCESS_WEBSITE"
        },
        {
            "template_id": 3881,
            "name": "接入小程序信息",
            "ename": "ODS_BEIAN_ACCESS_MINIAPP"
        },
        {
            "template_id": 3882,
            "name": "接入数据核验信息",
            "ename": "ODS_BEIAN_ACCESS_DATAVERIFICATION"
        },
        {
            "template_id": 3883,
            "name": "主体信息",
            "ename": "ODS_BEIAN_MAINBODY_INFO"
        },
        {
            "template_id": 3884,
            "name": "APP信息",
            "ename": "ODS_BEIAN_APPINFO"
        },
        {
            "template_id": 3885,
            "name": "小程序信息",
            "ename": "ODS_BEIAN_MIMIAPP_INFO"
        }
    ]
    for item in table_entity_info:
        print(item)
        data = crawl(entity_id=item.get("template_id"), cookie=cookie_data)
        print(data)
        if data.get("status", 0) != 200:
            print(data)
            continue
        save_data_file = bash_path.joinpath("export_data", "pangu", "bxf", f'{item.get("ename")}.json')
        with open(save_data_file, mode="w",
                  encoding="utf-8") as w:
            json.dump(data, w, ensure_ascii=False)
        clear_data_file = bash_path.joinpath("output", "pangu", "bxf", f'{item.get("ename")}.json')
        clear(input_file=save_data_file, output_file=clear_data_file)
