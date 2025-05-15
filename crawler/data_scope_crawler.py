#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/13 15:28 
# @Author   : guoqun X2590
# @FileName : data_scope_crawler.py
# @Project  : DataForge

from typing import List, Dict
import requests
from loguru import logger

import urllib3
from urllib3.exceptions import InsecureRequestWarning

from crawler.config import bdp_cookie, data_scope_resource_url, data_scope_resource_detail_url
from database_models.schema import TableRawFieldSchema, TableMetaDataSchema
from database_models.sys_enum import MetaDataSource

urllib3.disable_warnings(InsecureRequestWarning)


class DataScopeCrawler:
    def __init__(self, resource_url: str, detail_url: str, cookie: str, resource_count: int = 200):
        self.data_scope_resource_url = resource_url
        self.data_scope_resource_detail_url = detail_url
        self.resource_count = resource_count
        self.bdp_headers = {"Cookie": cookie}
        self.resource_elements = []

    @staticmethod
    def table_metadata_verify2model(table_metadata_fields: List[Dict], source: str) -> TableMetaDataSchema:
        """
        元数据校验转换
        Args:
            table_metadata_fields:
            source:

        Returns:

        """
        table_fields_slice = list()
        for field in table_metadata_fields:
            if source == MetaDataSource.data_scope:
                field_model = TableRawFieldSchema(
                    en_name=field.get("ename", ""),
                    cn_name=field.get("name", ""),
                    desc=field.get("description", ""),
                    field_type=field.get("fieldType", "").lower(),
                    dict_key=field.get("dictkey", "")
                )
                table_fields_slice.append(field_model)
        table_metadata_model = TableMetaDataSchema(table_fields=table_fields_slice)
        return table_metadata_model

    @staticmethod
    def fill_one_example2model(table_metadata_model: TableMetaDataSchema,
                               example_slice: List[Dict]) -> TableMetaDataSchema:
        """
        从给定的样例数据切片中获取样例数据填充模型对象
        Args:
            table_metadata_model:
            example_slice:

        Returns:

        """
        if example_slice is None:
            logger.warning(f"数据域没有样例数据: {table_metadata_model.table_en_name}")
            return table_metadata_model
        example_one_data = {}
        # 遍历每条数据
        for example in example_slice:
            # 遍历每个键值对
            for key, value in example.items():
                # 检查key和value都是非空
                if key and value:
                    # 补充数据
                    if key not in example_one_data:
                        example_one_data[key] = value
            # 如果所有需要的键都有了值，则中断循环
            if len(example_one_data) == len(table_metadata_model.table_fields):
                logger.debug(f"example_one_data: {example_one_data}")
                break
        for index, field in enumerate(table_metadata_model.table_fields):
            example_value = example_one_data.get(field.en_name, "")
            field.example = example_value
            table_metadata_model.table_fields[index] = field
        return table_metadata_model

    def crawl_resource(self):
        """
        获取数据域资源目录信息
        """
        payload = {
            "pageSize": self.resource_count,
            "pageNo": 1,
            "keyword": "",
            "condition": {
                "id": 3
            }
        }
        resp = requests.post(url=self.data_scope_resource_url, headers=self.bdp_headers, json=payload, verify=False)
        if resp.status_code != 200:
            logger.error(resp.raise_for_status())
            raise resp.raise_for_status()
        try:
            resp_json = resp.json()
            if resp_json.get("status") != 200:
                logger.error(f"数据域资源目录获取异常: resp_json.status={resp_json.get('status')}")
            data = resp_json.get("data", {})
            elements = data.get("elements", [])
            logger.info(f"数据域资源目录获取到{len(elements)}个资源")
            self.resource_elements = elements
        except Exception as err:
            logger.error(err)

    def crawl_detail(self, resource_id: str):
        """
        获取资源详情
        Args:
            resource_id:

        Returns:

        """
        payload = {
            "resourceId": resource_id
        }
        resp = requests.get(url=self.data_scope_resource_detail_url, headers=self.bdp_headers, params=payload,
                            verify=False)
        if resp.status_code != 200:
            logger.error(resp.raise_for_status())
            raise resp.raise_for_status()
        resp_json = resp.json()
        if resp_json.get("status") != 200:
            logger.error(
                f"数据域资源 [resourceId={resource_id}] 详情获取异常: resp_json.status={resp_json.get('status')}")

        data = resp_json.get("data", {})
        resource = data.get("resource", {})
        fields = data.get("fields", [])
        table_metadata_model = self.table_metadata_verify2model(table_metadata_fields=fields,
                                                                source=MetaDataSource.data_scope)
        # 补充表名称等元数据信息
        table_metadata_model.table_en_name = resource.get("ename", "")
        table_metadata_model.table_cn_name = resource.get("name", "")
        table_metadata_model.description = resource.get("description", "")
        table_metadata_model.position_type = resource.get("positionType", "")
        table_metadata_model.storage_type = resource.get("storageType", "")
        table_metadata_model.area_code = resource.get("areaCode", "")
        table_metadata_model.source = MetaDataSource.data_scope
        # 填充样例数据
        examples = data.get("example", [])
        logger.debug(f"raw table_metadata_model: {table_metadata_model.model_dump_json()}")
        table_metadata_model = self.fill_one_example2model(table_metadata_model=table_metadata_model,
                                                           example_slice=examples)
        logger.debug(f"filled table_metadata_model: {table_metadata_model.model_dump_json()}")

    def run(self):
        self.crawl_resource()
        for resource_element in self.resource_elements:
            resource_id = resource_element.get("id", "-1")
            self.crawl_detail(resource_id=resource_id)


if __name__ == '__main__':
    dsc = DataScopeCrawler(resource_url=data_scope_resource_url, detail_url=data_scope_resource_detail_url,
                           cookie=bdp_cookie)
    dsc.run()
