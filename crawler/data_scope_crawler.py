#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/13 15:28 
# @Author   : guoqun X2590
# @FileName : data_scope_crawler.py
# @Project  : DataForge

import requests
from loguru import logger

import urllib3
from urllib3.exceptions import InsecureRequestWarning

from crawler.config import bdp_cookie, data_scope_resource_url, data_scope_resource_detail_url

urllib3.disable_warnings(InsecureRequestWarning)


class DataScopeCrawler:
    def __init__(self, resource_url: str, detail_url: str, cookie: str, resource_count: int = 200):
        self.data_scope_resource_url = resource_url
        self.data_scope_resource_detail_url = detail_url
        self.resource_count = resource_count
        self.bdp_headers = {"Cookie": cookie}
        self.resource_elements = []

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
        resp_json = resp.json()
        if resp_json.get("status") != 200:
            logger.error(f"数据域资源目录获取异常: resp_json.status={resp_json.get('status')}")
        data = resp_json.get("data", {})
        elements = data.get("elements", [])
        logger.info(f"数据域资源目录获取到{len(elements)}个资源")
        self.resource_elements = elements

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
        fields = data.get("fields", [])
        example = data.get("example", [])


if __name__ == '__main__':
    dsc = DataScopeCrawler(resource_url=data_scope_resource_url, detail_url=data_scope_resource_detail_url,
                           cookie=bdp_cookie)
    dsc.crawl_resource()
