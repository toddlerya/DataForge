#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/21 10:11
# @Author   : guoqun X2590
# @FileName : pangu_crawler.py.py
# @Project  : DataForge

import json

import requests
import urllib3
from loguru import logger
from urllib3.exceptions import InsecureRequestWarning

from bdp.bdp_token_create import create_bdp_token
from crawler.common import fill_one_example2model, table_metadata_verify2model
from cruds.environment import query_environment_info_by_env_name
from cruds.table_example import table_example_save
from cruds.table_metadata import table_metadata_query_by_entity_id, table_metadata_save
from database_models.schema import TableExampleSchema, TableMetaDataSchema
from database_models.sys_enum import MetaDataSource
from utils.db_manager import DatabaseManager
from utils.file import get_md5

urllib3.disable_warnings(InsecureRequestWarning)


class PanGuCrawler:
    def __init__(
        self,
        inner_db_manager: DatabaseManager,
        resource_count: int = 2000,
    ):
        self.inner_db_manager = inner_db_manager
        self.bdp_ip: str = ""
        self.local_city_code: str = ""
        self.pangu_web_ip_port = ""
        self.resource_url: str = ""
        self.pangu_data_inner_resource_dir_url: str = ""
        self.entity_list_url: str = ""
        self.detail_url: str = ""
        self.query_url: str = ""
        self.resource_count = resource_count
        self.bdp_headers = {"Cookie": ""}
        self.resource_elements: list[dict] = []
        self.template_id_slice: list[int] = []
        self.entity_elements: list[dict] = []

    def sync_env_data(self, env_name: str):
        """同步环境配置信息

        Args:
            env_name (str): _description_
        """
        status, message, result = query_environment_info_by_env_name(
            env_name=env_name, db_manager=self.inner_db_manager
        )
        if status is False:
            logger.error(f"同步环境配置信息异常: {message}")
            raise Exception(message)
        self.pangu_web_ip_port = f"{result.pangu_web_ip}:11018"
        self.bdp_ip = str(result.bdp_web_ip)
        self.local_city_code = str(result.local_city_code)
        logger.debug(
            f"pangu_web_ip_port: {self.pangu_web_ip_port} "
            f"bdp_ip: {self.bdp_ip} "
            f"local_city_code: {self.local_city_code} "
        )

    def auth(self):
        """登录BDP认证"""
        app_id = "pangu"
        message, data = create_bdp_token(bdp_ip=self.bdp_ip, app_id=app_id)
        if message != "ok":
            logger.error(f"PanGuWeb BDP认证异常: {message}")
            raise Exception(message)
        logger.debug(f"bdp token data: {json.dumps(data)}")
        self.pangu_cookie = (
            "contextPath=/catalog; JSESSIONID=212D9047AF5D54880D245EE23D92C371; "
            f"contextPath=/; citycode={self.local_city_code}; appId={app_id}; "
            f"topoptid={app_id}; JSESSIONID=8CE476D6DFFC4A1DEEEC90D89199E76D; "
            f"userToken={data.get('userToken')}; "
            f"appToken={data.get('appToken')}; "
            "loginIp=1.1.1.1; loginMac=A4-BB-6D-43-BE-0D"
        )
        logger.debug(f"pangu_cookie: {self.pangu_cookie}")
        self.bdp_headers = {"Cookie": self.pangu_cookie}

    def set_pangu_url_config(self):
        # 盘古配置
        # 数据资产-数据资源目录
        self.resource_url = (
            f"https://{self.pangu_web_ip_port}/catalog/catalog/res/searchResourceManage"
        )
        # 数据资产-设置中心-资源管理(内部)
        self.pangu_data_inner_resource_dir_url = (
            f"https://{self.pangu_web_ip_port}/catalog/catalog/data/getResourcePage"
        )
        self.entity_list_url = (
            f"https://{self.pangu_web_ip_port}/catalog/catalog/query/getEntityList"
        )
        self.detail_url = (
            f"https://{self.pangu_web_ip_port}/catalog/catalog/query/getEntityDetail"
        )
        self.query_url = (
            f"https://{self.pangu_web_ip_port}/catalog/catalog/query/getDataBySql"
        )

    def crawl_inner_resource(self):
        """
        抓取资源管理(内部)清单
        :return:
        """
        page_size = 200
        page_no = 1
        # 初始值，可以是任意值，但会被动态覆盖
        page_no_max = 50
        while True:
            payload = {
                "dataAtlas": 0,
                "dirIds": [],
                "ignore": -1,
                "isGab": 0,
                "keyword": "",
                "manageDataSizeFilter": -1,
                "pageType": "inner",
                "pageno": page_no,
                "pagesize": page_size,
                "release": -1,
                "state": "-1",
                "treeId": "-2",
                "type": 2,
            }
            resp = requests.post(
                url=self.pangu_data_inner_resource_dir_url,
                headers=self.bdp_headers,
                json=payload,
                verify=False,
            )
            if resp.status_code != 200:
                logger.error(resp.raise_for_status())
                resp.raise_for_status()
            try:
                resp_json = resp.json()
                if resp_json.get("status") != 200:
                    logger.error(
                        "数据资产-设置中心-资源管理(内部)获取异常: "
                        f"resp_json.status={resp_json.get('status')}"
                    )
                data = resp_json.get("data", {})
                records_total = data.get("recordsTotal", 200)
                resources = data.get("data", [])
                self.template_id_slice.extend(
                    [ele.get("TEMPLATE_ID", -1) for ele in resources]
                )

                # 计算下一页的页码
                page_no += 1
                page_no_max = int(records_total / page_size) + 1
                # 如果当前页已经大于等于最大页数，就退出循环
                if page_no > page_no_max:
                    logger.info(
                        f"盘古内部数据资源目录获取到{records_total}个资源, "
                        f"实际{len(self.template_id_slice)}个资源"
                    )
                    break
            except Exception as err:
                logger.error(err)

    def crawl_resource(self):
        """
        抓取数据资源目录
        Returns:

        """
        payload = {
            "pageNo": 1,
            "pageSize": self.resource_count,
            "keyword": "",
            "isAdmin": 1,
        }
        resp = requests.post(
            url=self.resource_url, headers=self.bdp_headers, json=payload, verify=False
        )
        if resp.status_code != 200:
            logger.error(resp.raise_for_status())
            resp.raise_for_status()
        try:
            resp_json = resp.json()
            if resp_json.get("status") != 200:
                logger.error(
                    "盘古数据资源目录获取异常: "
                    f"resp_json.status={resp_json.get('status')}"
                )
            data = resp_json.get("data", {})
            total_records = data.get("totalRecords", -1)
            resources = data.get("resources", [])
            logger.info(
                f"盘古数据资源目录获取到{total_records}个资源, "
                f"实际{len(resources)}个资源"
            )
            self.template_id_slice.extend(
                [ele.get("templateId", -1) for ele in resources]
            )
        except Exception as err:
            logger.error(err)

    def crawl_resource_entity_list(self, template_id: int):
        """
        根据数据资源编码templateID获取实例列表信息
        Args:
            template_id:

        Returns:

        """

        payload = {"templateId": template_id}
        resp = requests.get(
            url=self.entity_list_url,
            headers=self.bdp_headers,
            params=payload,
            verify=False,
        )
        if resp.status_code != 200:
            logger.error(resp.raise_for_status())
            resp.raise_for_status()
        try:
            resp_json = resp.json()
            if resp_json.get("status") != 200:
                logger.error(
                    "盘古资源实体清单获取异常: "
                    f"resp_json.status={resp_json.get('status')}"
                )
            data = resp_json.get("data", [])
            logger.trace(
                f"盘古资源实体清单获取到{len(data)}个实体, templateId={template_id}"
            )
            self.entity_elements.extend(data)
        except Exception as err:
            logger.error(err)

    def crawl_entity_detail(self, entity_id: str) -> TableMetaDataSchema | None:
        """
        抓取详情
        Args:
            entity_id:

        Returns:

        """
        logger.trace(f"正在获取entity_id={entity_id}信息")

        def __get_storage_type_value(entity_extends: list[dict]) -> str:
            for entity_ext in entity_extends:
                if entity_ext.get("key") == "storage_type":
                    return entity_ext.get("value", "").upper()
            return ""

        payload = {"entityId": entity_id}

        resp = requests.get(
            url=self.detail_url, headers=self.bdp_headers, params=payload, verify=False
        )
        if resp.status_code != 200:
            logger.error(resp.raise_for_status())
            resp.raise_for_status()
        try:
            resp_json = resp.json()
            if resp_json.get("status") != 200:
                logger.error(
                    f"盘古表详情获取异常: resp_json.status={resp_json.get('status')}"
                )
            else:
                data = resp_json.get("data", {})
                entity_extends_value = data.get("entityExtends", {}).get(
                    "entityExtends", []
                )
                entity_info = data.get("entityInfo", {})
                base_table_en_name = entity_info.get("ename", "")
                field_info_list = data.get("fieldInfoList", [])
                position_info = data.get("positionInfo", {})
                data_source_name = position_info.get("DATASOURCE", "")
                # 结束提取position_type
                table_metadata_model = table_metadata_verify2model(
                    table_metadata_fields=field_info_list, source=MetaDataSource.pangu
                )
                table_metadata_model.table_en_name = (
                    f"{data_source_name}.{base_table_en_name}"
                )
                table_metadata_model.table_cn_name = entity_info.get("name", "")
                table_metadata_model.description = entity_info.get("description", "")
                table_metadata_model.position_type = entity_info.get("positionName", "")
                table_metadata_model.storage_type = __get_storage_type_value(
                    entity_extends=entity_extends_value
                )
                table_metadata_model.area_name = entity_info.get("areaName", "")
                table_metadata_model.source = MetaDataSource.pangu
                status, tb_meta_uuid = get_md5(
                    f"{table_metadata_model.table_en_name}"
                    f"{table_metadata_model.source}"
                    f"{table_metadata_model.env_name}"
                )
                if status is False:
                    logger.error(
                        f"计算{table_metadata_model.source}表{table_metadata_model.table_en_name}元数据UUID异常!"
                    )
                else:
                    table_metadata_model.uuid = tb_meta_uuid
                logger.trace(
                    f"table_metadata_model: {table_metadata_model.model_dump_json()}"
                )
                return table_metadata_model
        except Exception as err:
            logger.error(err)
            return None

    def crawl_sample(
        self, table_en_name: str, entity_id: int, type_value: str = "2", limit: int = 10
    ) -> list[dict]:
        """
        抓取样例数据
        Args:
            table_en_name:
            entity_id:
            type_value:
            limit:
        Returns:

        """
        data = []
        sql = f"SELECT * FROM {table_en_name} LIMIT {limit}"
        payload = {"sql": sql, "entityId": entity_id, "type": type_value}
        try:
            resp = requests.get(
                url=self.query_url,
                headers=self.bdp_headers,
                params=payload,
                timeout=60,
                verify=False,
            )
        except Exception:
            logger.error(f"请求url={self.query_url} payload={payload} 超时")
        else:
            if resp.status_code != 200:
                logger.error(resp.raise_for_status())
                # raise resp.raise_for_status()
            try:
                resp_json = resp.json()
                if resp_json.get("status") != 200:
                    logger.error(
                        f"盘古样例数据获取异常: "
                        f"table_en_name={table_en_name} "
                        f"entity_id={entity_id} "
                        f"resp_json.status={resp_json.get('status')}"
                    )
                else:
                    data: list[dict] = resp_json.get("data", [])
            except Exception as err:
                logger.error(err)
            finally:
                return data
        finally:
            return data

    def run(self, env_name: str, need_overwrite: bool = False):
        self.sync_env_data(env_name=env_name)
        self.auth()
        self.set_pangu_url_config()
        self.crawl_inner_resource()
        self.crawl_resource()
        # template_id_slice 去重
        self.template_id_slice = list(set(self.template_id_slice))
        logger.info(f"盘古去重后一共有{len(self.template_id_slice)}个资源")
        logger.info("正在获取资源实体信息, 请等待...")
        for template_id in self.template_id_slice:
            self.crawl_resource_entity_list(template_id=template_id)
        logger.info(f"盘古实体清单获取到{len(self.entity_elements)}个实体信息")
        for entity_info in self.entity_elements:
            entity_id = entity_info.get("entityId", -1)
            if entity_id in []:
                continue
            if not need_overwrite:
                query_status, query_msg, entity_data = (
                    table_metadata_query_by_entity_id(
                        entity_id=entity_id, db_manager=self.inner_db_manager
                    )
                )
                if query_status and entity_data:
                    # 数据已存在则跳过
                    logger.warning(
                        f"数据已存在，跳过: entity_id={entity_id} "
                        f"table_en_name={entity_data.table_en_name}"
                    )
                    continue
            logger.info(f"采集实例元数据入库中: entity_id={entity_id}")
            each_table_metadata_model = self.crawl_entity_detail(entity_id=entity_id)
            if each_table_metadata_model is None:
                continue
            # 采集表的样例数据
            if not each_table_metadata_model.table_en_name.startswith(
                "massdata"
            ) and not each_table_metadata_model.table_en_name.startswith("fmdbmeta"):
                logger.warning(
                    "不是massdata或fmdbmeta库的表, 跳过: "
                    f"{each_table_metadata_model.table_en_name}"
                )
                continue
            example_data = self.crawl_sample(
                table_en_name=each_table_metadata_model.table_en_name,
                entity_id=entity_id,
                limit=5,
            )
            logger.debug(
                f"entity_id={entity_id} "
                f"table_en_name={each_table_metadata_model.table_en_name} "
                f"获取到样例数据{len(example_data)}条"
            )
            # 填充样例数据
            each_table_metadata_model = fill_one_example2model(
                table_metadata_model=each_table_metadata_model,
                example_slice=example_data,
            )
            each_table_metadata_record = each_table_metadata_model.model_dump()
            each_table_metadata_record.update(
                {"remark": entity_id, "env_name": env_name}
            )
            save_status, save_message = table_metadata_save(
                record=each_table_metadata_record, db_manager=self.inner_db_manager
            )
            if save_status is False:
                logger.error(
                    f"盘古元数据信息入库异常: {each_table_metadata_record} "
                    f"ERROR: {save_message}"
                )
            for ex_data in example_data:
                data_uuid_md5_status, data_uuid = get_md5(json.dumps(ex_data))
                if data_uuid_md5_status is False:
                    continue
                example_data = TableExampleSchema(
                    uuid=data_uuid,
                    table_uuid=each_table_metadata_model.uuid,
                    example_data=ex_data,
                    env_name=env_name,
                )
                save_ex_status, save_ex_message = table_example_save(
                    record=example_data.model_dump(), db_manager=self.inner_db_manager
                )
                if save_ex_status is False:
                    logger.error(
                        f"数据域{each_table_metadata_model.table_en_name}"
                        f"样例数据入库异常: {example_data.model_dump_json()} "
                        f"ERROR: {save_ex_message}"
                    )


if __name__ == "__main__":
    from loguru import logger

    from common.initialization import setup_logging
    from config import PROJECT_PATH
    from utils.log import LogManager

    log_config = LogManager(
        base_path=str(PROJECT_PATH.absolute()),
        log_path="logs",
        log_name="debug.log",
        file_log_level="TRACE",
        console_log_level="INFO",
    )
    setup_logging(log_config.get_config().get("handlers"))

    db_manager = DatabaseManager()
    pgc = PanGuCrawler(inner_db_manager=db_manager)
    pgc.run(env_name="测试部仿真测试环境")
    db_manager.close()
