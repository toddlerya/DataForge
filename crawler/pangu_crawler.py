#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/21 10:11 
# @Author   : guoqun X2590
# @FileName : pangu_crawler.py.py
# @Project  : DataForge

from typing import List, Dict
import requests
from loguru import logger

import urllib3
from urllib3.exceptions import InsecureRequestWarning

from config import pangu_data_resource_dir_url
from database_models.schema import TableRawFieldSchema, TableMetaDataSchema
from database_models.sys_enum import MetaDataSource
from database_models.models import TableMetaDataInfo
from utils.db import Database
from utils.file import get_md5
from cruds.table_metadata import table_metadata_save

urllib3.disable_warnings(InsecureRequestWarning)


class PanGuCrawler:
    def __init__(self, inner_db: Database, resource_url: str, detail_url: str, query_url: str, cookie: str,
                 resource_count: int = 2000):
        self.resource_url = resource_url
        self.detail_url = detail_url
        self.query_url = query_url
        self.resource_count = resource_count
        self.bdp_headers = {"Cookie": cookie}
        self.resource_elements = []
        self.inner_db = inner_db

    def crawl_resource(self):
        """
        抓取资源清单
        Returns:

        """
        payload = {
            {
                "pageNo": 1,
                "pageSize": self.resource_count,
                "keyword": "",
                "isAdmin": 1
            }
        }
        resp = requests.post(url=self.resource_url, headers=self.bdp_headers, json=payload, verify=False)
        if resp.status_code != 200:
            logger.error(resp.raise_for_status())
            raise resp.raise_for_status()
        try:
            resp_json = resp.json()
            if resp_json.get("status") != 200:
                logger.error(f"盘古数据资源目录获取异常: resp_json.status={resp_json.get('status')}")
            data = resp_json.get("data", {})
            total_records = data.get("totalRecords", -1)
            resources = data.get("resources", [])
            logger.info(f"盘古数据资源目录获取到{total_records}个资源")
            self.resource_elements = resources
        except Exception as err:
            logger.error(err)

    def crawl_sample(self, sql: str, entity_id: int, type_value: str = 2):
        """
        抓取资源清单
        Returns:

        """

        payload = {
            {
                "sql": sql,
                "entityId": entity_id,
                "type": type_value
            }
        }
        resp = requests.get(url=self.query_url, headers=self.bdp_headers, params=payload, verify=False)
        if resp.status_code != 200:
            logger.error(resp.raise_for_status())
            raise resp.raise_for_status()
        try:
            resp_json = resp.json()
            if resp_json.get("status") != 200:
                logger.error(f"盘古样例数据获取异常: resp_json.status={resp_json.get('status')}")
            data = resp_json.get("data", {})
            total_records = data.get("totalRecords", -1)
            resources = data.get("resources", [])
            logger.info(f"盘古数据资源目录获取到{total_records}个资源")
            self.resource_elements = resources
        except Exception as err:
            logger.error(err)

    def run(self):
        self.crawl_resource()


if __name__ == '__main__':
    pgc = PanGuCrawler(inner_db=Database(), resource_url=pangu_data_resource_dir_url)
