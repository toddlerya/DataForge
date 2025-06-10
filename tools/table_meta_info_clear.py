#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/11 11:23
# @Author   : guoqun X2590
# @FileName : table_meta_info_clear.py.py
# @Project  : AIUsage

import json
import pathlib


# https://172.21.4.42:11018/catalog/catalog/query/getEntityDetail?entityId=1355


def transform_entity_detail_info(raw_data: dict) -> list[dict]:
    """
    摘取所需的字段
    :param raw_data:
    :return:
    """
    format_data: list[dict] = list()
    raw_field_info_list: list[dict] = raw_data.get("data", {}).get("fieldInfoList", [])
    for item_field in raw_field_info_list:
        format_data.append(
            {
                "name": item_field.get("name", "").strip(),
                "ename": item_field.get("ename", "").strip(),
                # "desc": [item_field.get("desc", "").strip()
                #          if item_field.get("desc", "").strip() != item_field.get("name", "").strip() else ""][0]
                # "elementName": item_field.get("elementName", "").strip(),
                # "identifier": item_field.get("identifier", "").strip(),
                "desc": item_field.get("desc", "").strip(),
                # "fieldDir": item_field.get("fieldDir", "").strip(),
                # "fieldSen": item_field.get("fieldSen", "").strip(),
                "dic": item_field.get("dic", "").strip(),
            }
        )

    return format_data


def clear(input_file: pathlib, output_file: pathlib):
    with open(input_file, mode="r", encoding="utf-8") as r:
        raw_data = json.load(r)
        format_data = transform_entity_detail_info(raw_data)
        with open(output_file, mode="w", encoding="utf-8") as w:
            json.dump(format_data, w, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    io_pair = [
        {
            "input": "export_data/pangu/ODS_POL_EIV_DOMAIN_WHOIS.json",
            "output": "output/pangu/ODS_POL_EIV_DOMAIN_WHOIS.json",
        },
        {
            "input": "export_data/pangu/ADM_DOMAIN_WHOIS.json",
            "output": "output/pangu/ADM_DOMAIN_WHOIS.json",
        },
        {
            "input": "export_data/pangu/DWD_RES_NUL_LOG_VEH.json",
            "output": "output/pangu/DWD_RES_NUL_LOG_VEH.json",
        },
        {
            "input": "export_data/pangu/ADM_GRAPH_NODE_FLIGHT.json",
            "output": "output/pangu/ADM_GRAPH_NODE_FLIGHT.json",
        },
        {
            "input": "export_data/pangu/DWS_PER_RES_DAY_DCFLIGHT.json",
            "output": "output/pangu/DWS_PER_RES_DAY_DCFLIGHT.json",
        },
    ]
    bash_path = pathlib.Path(r"F:\GITLAB\DataForge")
    for item in io_pair:
        clear(
            input_file=bash_path.joinpath(item.get("input")),
            output_file=bash_path.joinpath(item.get("output")),
        )
