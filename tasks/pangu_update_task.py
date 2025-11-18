#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/12 14:50
# @Author   : guoqun X2590
# @Desc     : 更新盘古Web和db的数据


from crawler.pangu_db_crawler import PanGuDatabaseCrawler
from crawler.pangu_web_crawler import PanGuWebCrawler
from cruds.environment import query_environment_info_by_status
from database_models.sys_enum import EnvironmentStatus
from utils.db_manager import DatabaseManager
from utils.log import logger


def pangu_web_crawler_task():
    """PanGuWeb的采集数据任务"""
    db_manager = DatabaseManager()
    # 获取当前有哪些启用盘古环境配置信息
    query_status, query_message, env_data_slice = query_environment_info_by_status(
        status=EnvironmentStatus.enable, db_manager=db_manager
    )
    if query_status is False:
        logger.error(query_message)
        db_manager.close()
        raise Exception(query_message)

    for each_env_data in env_data_slice:
        logger.info(f"准备env_name={each_env_data.env_name}的PanGuWebCrawler")
        pgc = PanGuWebCrawler(inner_db_manager=db_manager)
        if pgc.run(env_name=str(each_env_data.env_name)):
            logger.info(f"env_name={each_env_data.env_name}的PanGuWebCrawler运行成功")
        else:
            logger.error(f"env_name={each_env_data.env_name}的PanGuWebCrawler运行异常")
    # 关闭数据库链接
    db_manager.close()


def pangu_db_crawler_task():
    """PanGuWeb的采集数据任务"""
    db_manager = DatabaseManager()
    # 获取当前有哪些启用盘古环境配置信息
    query_status, query_message, env_data_slice = query_environment_info_by_status(
        status=EnvironmentStatus.enable, db_manager=db_manager
    )
    if query_status is False:
        logger.error(query_message)
        db_manager.close()
        raise Exception(query_message)

    for each_env_data in env_data_slice:
        logger.info(f"准备env_name={each_env_data.env_name}的PanGuDatabaseCrawler")
        pdc = PanGuDatabaseCrawler(inner_db_manager=db_manager)
        if pdc.run(env_name=str(each_env_data.env_name)):
            logger.info(
                f"env_name={each_env_data.env_name}的PanGuDatabaseCrawler运行成功"
            )
        else:
            logger.error(
                f"env_name={each_env_data.env_name}的PanGuDatabaseCrawler运行异常"
            )
    # 关闭数据库链接
    db_manager.close()


if __name__ == "__main__":
    pangu_web_crawler_task()
