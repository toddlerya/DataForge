#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/13 15:28
# @Author   : guoqun X2590
# @FileName : data_scope_crawler.py
# @Project  : DataForge
import json
from typing import List, Dict
import requests
from loguru import logger

import urllib3
from urllib3.exceptions import InsecureRequestWarning

from config import (
    data_scope_cookie,
    data_scope_resource_url,
    data_scope_resource_detail_url,
)
from database_models.schema import (
    TableRawFieldSchema,
    TableMetaDataSchema,
    TableExampleSchema,
)
from database_models.sys_enum import MetaDataSource
from database_models.models import TableMetaDataInfo
from utils.db import Database
from utils.file import get_md5
from cruds.table_metadata import table_metadata_save
from cruds.table_example import table_example_save
from crawler.common import table_metadata_verify2model, fill_one_example2model

urllib3.disable_warnings(InsecureRequestWarning)


class DataScopeCrawler:
    def __init__(
            self,
            inner_db: Database,
            resource_url: str,
            detail_url: str,
            cookie: str,
            resource_count: int = 2000,
    ):
        self.data_scope_resource_url = resource_url
        self.data_scope_resource_detail_url = detail_url
        self.resource_count = resource_count
        self.bdp_headers = {"Cookie": cookie}
        self.resource_elements = []
        self.inner_db = inner_db

    def crawl_resource(self, resource_id: int):
        """
        获取数据域资源目录信息
        """
        payload = {
            "pageSize": self.resource_count,
            "pageNo": 1,
            "keyword": "",
            "condition": {"id": resource_id},
        }
        resp = requests.post(
            url=self.data_scope_resource_url,
            headers=self.bdp_headers,
            json=payload,
            verify=False,
        )
        if resp.status_code != 200:
            logger.error(resp.raise_for_status())
            raise resp.raise_for_status()
        try:
            resp_json = resp.json()
            if resp_json.get("status") != 200:
                logger.error(
                    f"数据域资源目录获取异常: resp_json.status={resp_json.get('status')}"
                )
            data = resp_json.get("data", {})
            elements = data.get("elements", [])
            logger.info(f"数据域资源目录[{resource_id}]获取到{len(elements)}个资源")
            self.resource_elements = elements
        except Exception as err:
            logger.error(err)

    def crawl_detail(self, resource_id: str) -> tuple[TableMetaDataSchema, list[dict]]:
        """
        获取资源详情
        Args:
            resource_id:

        Returns:

        """
        payload = {"resourceId": resource_id}
        resp = requests.get(
            url=self.data_scope_resource_detail_url,
            headers=self.bdp_headers,
            params=payload,
            verify=False,
        )
        if resp.status_code != 200:
            logger.error(resp.raise_for_status())
            raise resp.raise_for_status()
        resp_json = resp.json()
        if resp_json.get("status") != 200:
            logger.error(
                f"数据域资源 [resourceId={resource_id}] 详情获取异常: resp_json.status={resp_json.get('status')}"
            )

        data = resp_json.get("data", {})
        resource = data.get("resource", {})
        fields = data.get("fields", [])
        table_metadata_model = table_metadata_verify2model(
            table_metadata_fields=fields, source=MetaDataSource.data_scope
        )
        # 补充表名称等元数据信息
        table_metadata_model.table_en_name = resource.get("ename", "")
        table_metadata_model.table_cn_name = resource.get("name", "")
        table_metadata_model.description = resource.get("description", "")
        table_metadata_model.position_type = resource.get("positionType", "")
        table_metadata_model.storage_type = resource.get("storageType", "")
        table_metadata_model.area_code = resource.get("areaCode", "")
        table_metadata_model.source = MetaDataSource.data_scope
        status, tb_meta_uuid = get_md5(
            f"{table_metadata_model.table_en_name}"
            f"{table_metadata_model.source}"
            f"{table_metadata_model.area_code}"
            f"{table_metadata_model.area_name}"
        )
        if status is False:
            logger.error(
                f"计算{MetaDataSource.data_scope}表{table_metadata_model.table_en_name}元数据UUID异常!"
            )
        else:
            table_metadata_model.uuid = tb_meta_uuid
        # 填充样例数据
        examples = data.get("example", [])
        if examples is None:
            examples = []
        logger.trace(
            f"raw table_metadata_model: {table_metadata_model.model_dump_json()}"
        )
        table_metadata_model = fill_one_example2model(
            table_metadata_model=table_metadata_model, example_slice=examples
        )
        logger.trace(
            f"filled table_metadata_model: {table_metadata_model.model_dump_json()}"
        )
        return table_metadata_model, examples

    def run(self):
        # resource_ids获取 https://172.17.63.12:12018/offsite/v1/domain/query?type=1&keyword=&_=1747895349267
        for rs_id in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]:
            self.crawl_resource(resource_id=rs_id)
            for resource_element in self.resource_elements:
                resource_id = resource_element.get("id", "-1")
                each_table_metadata_model, each_table_examples = self.crawl_detail(
                    resource_id=resource_id
                )
                save_status, save_message = table_metadata_save(
                    record=each_table_metadata_model.model_dump(),
                    db_handler=self.inner_db,
                )
                if save_status is False:
                    logger.error(
                        f"数据域元数据信息入库异常: {each_table_metadata_model.model_dump_json()} "
                        f"ERROR: {save_message}"
                    )
                if len(each_table_examples) >= 100:
                    each_table_examples = each_table_examples[:100]
                for ex_data in each_table_examples:
                    data_uuid_md5_status, data_uuid = get_md5(json.dumps(ex_data))
                    if data_uuid_md5_status is False:
                        continue
                    example_data = TableExampleSchema(
                        uuid=data_uuid,
                        table_uuid=each_table_metadata_model.uuid,
                        example_data=ex_data,
                    )
                    save_ex_status, save_ex_message = table_example_save(
                        record=example_data.model_dump(), db_handler=self.inner_db
                    )
                    if save_ex_status is False:
                        logger.error(
                            f"数据域{each_table_metadata_model.table_en_name}"
                            f"样例数据入库异常: {example_data.model_dump_json()} "
                            f"ERROR: {save_ex_message}"
                        )


if __name__ == "__main__":
    db = Database()
    dsc = DataScopeCrawler(
        inner_db=db,
        resource_url=data_scope_resource_url,
        detail_url=data_scope_resource_detail_url,
        cookie=data_scope_cookie,
    )
    dsc.run()
