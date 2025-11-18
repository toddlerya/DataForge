#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/16 15:51
# @Author   : guoqun X2590
# @FileName : pangu_field_crawler.py
# @Project  : DataForge

from urllib.parse import quote_plus

from cruds.dynamic_query import query_sql
from cruds.environment import query_environment_info_by_env_name
from cruds.pangu import (
    get_all_pangu_field_stat,
    pangu_dict_key_values,
    pangu_recommend_field_info,
    save_pangu_dict_info,
    save_recommend_pangu_field_info,
)
from database_models.schema import RecommendPanGuFieldSchema
from utils.db_manager import DatabaseManager
from utils.log import logger


class PanGuDatabaseCrawler:
    def __init__(self, inner_db_manager: DatabaseManager):
        self.env_name: str = ""
        self.inner_db_manager = inner_db_manager
        logger.debug(f"inner_db_manager: {inner_db_manager.db}")
        self.metadata_sqlalchemy_url: str = ""
        self.all_field_stat_data: list[dict[str, int | str]] = []
        self.batch_size = 100

    def sync_env_data(self, env_name: str):
        """同步环境配置信息

        Args:
            env_name (str): _description_
        """
        self.env_name = env_name
        status, message, result = query_environment_info_by_env_name(
            env_name=env_name, db_manager=self.inner_db_manager
        )
        if status is False:
            logger.error(f"同步环境配置信息异常: {message}")
            raise Exception(message)
        metadata_db_ip = result.metadata_db_ip
        metadata_db_port = str(result.metadata_db_port)
        metadata_db_user = str(result.metadata_db_user)
        metadata_db_password = str(result.metadata_db_password)
        metadata_db_name = str(result.metadata_db_name)
        self.local_city_code = str(result.local_city_code)
        self.metadata_sqlalchemy_url = (
            f"postgresql+psycopg2://"
            f"{metadata_db_user}:{quote_plus(metadata_db_password)}"
            f"@{metadata_db_ip}:{metadata_db_port}"
            f"/{metadata_db_name}"
            f"?client_encoding=UTF8"
        )
        logger.debug(f"metadata_sqlalchemy_url => {self.metadata_sqlalchemy_url}")

    def connect_pangu_metadata_db(self):
        self.metadata_db_manager: DatabaseManager = DatabaseManager(
            url=self.metadata_sqlalchemy_url
        )

    def fetch_pangu_all_field_stat(self) -> bool:
        logger.info("正在执行采集盘古所有字段统计信息")
        status, message, data = get_all_pangu_field_stat(
            db_manager=self.metadata_db_manager
        )
        if status is False:
            logger.error(f"获取盘古所有字段统计信息异常: {message}")
            return False
        if data:
            logger.info(f"共有{len(data)}个字段")
            self.all_field_stat_data = data
        else:
            logger.error(f"获取盘古所有字段统计信息异常, 没有获取到结果! data={data}")
            return False
        return True

    def fetch_pangu_field_recommend_info(self) -> bool:
        logger.info("正在执行盘古字段推荐")
        for index, each_field_data in enumerate(self.all_field_stat_data, start=1):
            field_en_name = each_field_data.get("ename", "")
            if not field_en_name:
                logger.warning(
                    "没有获取到each_field_data的ename, 跳过! "
                    f"each_field_data={each_field_data}"
                )
                continue
            logger.info(f"[{index}]正在进行盘古字段推荐: field_en_name={field_en_name}")
            status, message, field_info_data = pangu_recommend_field_info(
                db_manager=self.metadata_db_manager,
                field_en_name=str(field_en_name),
            )
            if status is False:
                logger.error(
                    f"盘古字段推荐异常: field_en_name={field_en_name} ERROR: {message}"
                )
                return False
            if field_info_data is None:
                logger.warning(
                    f"盘古字段推荐异常: field_en_name={field_en_name} 结果为空!"
                )
                return False
            try:
                data = RecommendPanGuFieldSchema(**field_info_data)
            except Exception as err:
                logger.error(
                    f"盘古字段推荐结果校验! field_en_name={field_en_name} ERROR: {err}"
                )
                continue
            save_filed_status, save_field_message = save_recommend_pangu_field_info(
                db_manager=self.inner_db_manager,
                recommend_pangu_field_data=data.model_dump(),
                auto_commit=False,
            )
            if save_filed_status is False:
                logger.error(
                    f"存储盘古字段推荐异常: field_en_name={field_en_name} "
                    f"ERROR: {save_field_message}"
                )
                return False
            if index % self.batch_size == 0:
                self.inner_db_manager.get_session().commit()
                logger.info(f"盘古字段推荐 db commit: {index}")
        self.inner_db_manager.get_session().commit()
        logger.info("盘古字段推荐 db commit done")
        return True

    def fetch_pangu_dict_info(self) -> bool:
        logger.info("正在执行盘古字典采集")
        query_status, query_message, distinct_dict_keys = query_sql(
            db_manager=self.inner_db_manager,
            sql_text="SELECT DISTINCT dictkey FROM recommend_pangu_field_info "
            "WHERE dictkey IS NOT NULL",
        )
        if query_status is False:
            logger.error(f"无法获取推荐字段的字典集合: {query_message}")
            return False
        all_dictkey_with_nlevel_data = [ele["dictkey"] for ele in distinct_dict_keys]
        logger.info(f"共计需要采集 {len(all_dictkey_with_nlevel_data)} 个盘古字典")
        for index, dictkey_with_nlevel in enumerate(
            all_dictkey_with_nlevel_data, start=1
        ):
            logger.info(
                f"[{index}]正在采集盘古字典: dictkey_with_nlevel={dictkey_with_nlevel}"
            )
            status, message, data = pangu_dict_key_values(
                db_manager=self.metadata_db_manager,
                dictkey_with_nlevel=dictkey_with_nlevel,
            )
            if status is False:
                logger.error(
                    f"获取盘古字典异常: dictkey_with_nlevel={dictkey_with_nlevel} "
                    f"ERROR: {message}"
                )
                return False
            for each_data in data:
                save_status, save_message = save_pangu_dict_info(
                    db_manager=self.inner_db_manager,
                    pangu_dict_key_data=each_data,
                    auto_commit=False,
                )
                if save_status is False:
                    logger.error(
                        f"存储盘古字典异常: dictkey_with_nlevel={dictkey_with_nlevel} "
                        f"each_data={each_data} "
                        f"ERROR: {save_message}"
                    )
                    self.inner_db_manager.get_session().rollback()
                    return False
            if index % self.batch_size == 0:
                self.inner_db_manager.get_session().commit()
                logger.info(f"盘古字典采集 db commit: {index}")
        self.inner_db_manager.get_session().commit()
        logger.info("盘古字典采集 db commit done")
        return True

    def run(self, env_name: str):
        logger.info("开始采集盘古字段和字典信息")
        self.sync_env_data(env_name=env_name)
        try:
            self.connect_pangu_metadata_db()
            if self.fetch_pangu_all_field_stat():
                if self.fetch_pangu_field_recommend_info():
                    if self.fetch_pangu_dict_info():
                        logger.info("采集盘古字段和字典信息已完成")
        except Exception as err:
            logger.error(err)
        finally:
            self.metadata_db_manager.close()


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

    inner_db_manager = DatabaseManager()
    pdc = PanGuDatabaseCrawler(inner_db_manager=inner_db_manager)
    pdc.run(env_name="测试部仿真测试环境")
    inner_db_manager.close()
