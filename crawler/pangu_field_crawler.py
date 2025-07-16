#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/16 15:51 
# @Author   : guoqun X2590
# @FileName : pangu_field_crawler.py
# @Project  : DataForge

from urllib.parse import quote_plus

from config import METADATA_DB_IP, METADATA_DB_NAME, METADATA_DB_USER, METADATA_DB_PORT, METADATA_DB_PASSWORD
from cruds.pangu import (get_all_pangu_field_stat, pangu_recommend_field_info, pangu_dict_key_values,
                         save_recommend_pangu_field_info, save_pangu_dict_info)
from utils.db import Database
from utils.log import logger


class PanGuFieldCrawler:
    def __init__(self, inner_db: Database):
        self.inner_db = inner_db
        self.metadata_sqlalchemy_url = f"postgresql+psycopg2://" \
                                       f"{METADATA_DB_USER}:{quote_plus(METADATA_DB_PASSWORD)}" \
                                       f"@{METADATA_DB_IP}:{METADATA_DB_PORT}" \
                                       f"/{METADATA_DB_NAME}" \
                                       f"?client_encoding=UTF8"
        self.metadata_db = Database(url=self.metadata_sqlalchemy_url)
        self.all_field_stat_data: list[dict[str, int]] = list()
        self.all_dictkey_with_nlevel_data: list[str] = list()

    def fetch_pangu_all_field_stat(self) -> bool:
        logger.info("正在执行采集盘古所有字段统计信息")
        status, message, data = get_all_pangu_field_stat(db_handler=self.metadata_db)
        if status is False:
            logger.error(f"获取盘古所有字段统计信息异常: {message}")
            return False
        logger.info(f"共有{len(data)}个字段")
        self.all_field_stat_data = data
        return True

    def fetch_pangu_field_recommend_info(self) -> bool:
        logger.info("正在执行盘古字段推荐")
        for each_field_data in self.all_field_stat_data:
            field_en_name = each_field_data.get("ename", "")
            logger.info(f"正在进行盘古字段推荐: field_en_name={field_en_name}")
            status, message, data = pangu_recommend_field_info(db_handler=self.metadata_db,
                                                               field_en_name=field_en_name)
            if status is False:
                logger.error(f"盘古字段推荐异常: field_en_name={field_en_name} ERROR: {message}")
                return False
            if data.dictkey:
                self.all_dictkey_with_nlevel_data.append(data.dictkey)
            save_filed_status, save_field_message = save_recommend_pangu_field_info(
                db_handler=self.inner_db,
                recommend_pangu_field_data=data.model_dump())
            if save_filed_status is False:
                logger.error(f"存储盘古字段推荐异常: field_en_name={field_en_name} ERROR: {save_field_message}")
                self.inner_db.session.rollback()
                return False
            self.inner_db.session.flush()
        self.inner_db.session.commit()
        return True

    def fetch_pangu_dict_info(self) -> bool:
        logger.info("正在执行盘古字典采集")
        for dictkey_with_nlevel in set(self.all_dictkey_with_nlevel_data):
            status, message, data = pangu_dict_key_values(db_handler=self.metadata_db,
                                                          dictkey_with_nlevel=dictkey_with_nlevel)
            if status is False:
                logger.error(f"获取盘古字典异常: dictkey_with_nlevel={dictkey_with_nlevel} ERROR: {message}")
                return False
            save_status, save_message = save_pangu_dict_info(db_handler=self.inner_db, pangu_dict_key_data=data)
            if save_status is False:
                logger.error(f"存储盘古字典异常: dictkey_with_nlevel={dictkey_with_nlevel} ERROR: {message}")
                self.inner_db.session.rollback()
                return False
        self.inner_db.session.commit()
        return True

    def run(self):
        logger.info("开始采集盘古字段和字典信息")
        if self.fetch_pangu_all_field_stat():
            if self.fetch_pangu_field_recommend_info():
                if self.fetch_pangu_dict_info():
                    logger.info("采集盘古字段和字典信息已完成")


if __name__ == '__main__':
    pfc = PanGuFieldCrawler(inner_db=Database())
    pfc.run()
