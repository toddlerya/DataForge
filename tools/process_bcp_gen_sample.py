#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/25 17:02 
# @Author   : guoqun X2590
# @FileName : process_bcp_gen_sample.py
# @Project  : DataForge
import json
import pathlib

from utils.file import get_files_and_folders, load_json_from_file

raw_bcp_path = pathlib.Path(r"F:\GITLAB\DataForge\manual_gen_testdata\raw_bcp")


def get_bcp_col_by_index(index: int, data_slice: list[list[str]]) -> [str]:
    """

    Args:
        index:
        data_slice:

    Returns:

    """
    fake_quan_wen_url_prefix = "http://127.0.0.1:9999/index/"
    data: list[str] = []
    for record in data_slice:
        item = record[index]
        if item.startswith("attach"):
            item = fake_quan_wen_url_prefix + item
        data.append(item)
    return data


def gen_sample_data(gab_json_data: dict, bcp_sample_data: list[list], output_sample_json: pathlib.Path):
    """
    生成样例数据
    Args:
        gab_json_data:
        bcp_sample_data:
        output_sample_json:

    Returns:

    """
    print(f"gen sample data: {output_sample_json}")
    struct_data = []
    for index, item in enumerate(gab_json_data["DATA"]["ITEM"]):
        attr = item["_attributes"]
        struct_data.append({
            "ename": attr.get("eng"),
            "cname": attr.get("chn"),
            "sample": get_bcp_col_by_index(index=index, data_slice=bcp_sample_data)
        })
    print(json.dumps(struct_data, ensure_ascii=False))
    with open(output_sample_json, mode="w", encoding="utf-8") as w:
        json.dump(struct_data, w, ensure_ascii=False)


def run():
    fake_bcp_sample_data = pathlib.Path(r"F:\GITLAB\DataForge\output\fake_sample_data")
    _, table_dirs = get_files_and_folders(directory=str(raw_bcp_path.absolute()))
    for table_dir in table_dirs:
        table_dir_path = pathlib.Path(table_dir)
        print(f"table_dir: {table_dir_path.name}")
        files, _ = get_files_and_folders(directory=table_dir)
        # print(f"files: {files}")
        for each_file in files:
            gab_json_data = dict()
            each_file_path = pathlib.Path(each_file)
            if each_file_path.name == "gab.json":
                print(f"gab json: {each_file}")
                msg, gab_json_data = load_json_from_file(json_file_path=str(each_file_path.absolute()))
            if each_file_path.suffix == ".bcp":
                print(f"bcp sample: {each_file}")
                with open(each_file_path.absolute(), mode="r", encoding="utf-8") as bcp_reader:
                    raw_bcp_sample_lines = bcp_reader.readlines()
                    bcp_sample_slice = [line.split("\t") for line in raw_bcp_sample_lines]
                    if len(bcp_sample_slice) > 3:
                        bcp_sample_slice = bcp_sample_slice[:3]
                    print(f"bcp_sample_slice: {bcp_sample_slice}")
            if bcp_sample_slice and gab_json_data:
                output_sample_json_file = fake_bcp_sample_data.joinpath(f"{table_dir_path.name}.json")
                gen_sample_data(gab_json_data=gab_json_data, bcp_sample_data=bcp_sample_slice,
                                output_sample_json=output_sample_json_file)


if __name__ == '__main__':
    run()
