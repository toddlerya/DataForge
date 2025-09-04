#!/usr/bin/env python
# coding: utf-8
# @Time     : 2024/11/21 15:10
# @Author   : guoqun X2590
# @FileName : environment.py
# @Project  : HETUTaskChecker

from sqlalchemy import desc

from database_models.models import EnvironmentInfo
from utils.db import Database
from utils.log import logger


def save_environment_info(environment_data: dict, db: Database) -> tuple[bool, str]:
    """
    存储环境配置信息

    Args:
        environment_data (dict): 配置中心的配置信息
        db (Database): 数据库连接对象
    """
    try:
        db.insert_or_update(EnvironmentInfo, **environment_data)
    except Exception as err:
        db.session.rollback()
        message = f"数据库写操作错误: {err}"
        return False, message
    else:
        db.session.commit()
        return True, "ok"


def query_environment_info_by_apollo_ip(
    apollo_web_ip: str, db: Database
) -> tuple[bool, str, EnvironmentInfo]:
    """
    根据阿波罗IP获取对应的环境配置信息
    :param apollo_web_ip:
    :param db:
    :return:
    """
    try:
        logger.trace(
            f"query_environment_info_by_apollo_ip(apollo_web_ip={apollo_web_ip})"
        )
        data = (
            db.session.query(EnvironmentInfo)
            .filter(EnvironmentInfo.apollo_web_ip == apollo_web_ip)
            .order_by(desc(EnvironmentInfo.create_time))
            .first()
        )
    except Exception as err:
        message = f"根据阿波罗IP获取对应的环境配置信息失败! apollo_web_ip={apollo_web_ip} ERROR: {err}"
        return False, message, EnvironmentInfo()
    else:
        return True, "ok", data


if __name__ == "__main__":
    db_handler = Database()
    s, m, r = query_environment_info_by_apollo_ip(
        apollo_web_ip="172.21.4.30", db=db_handler
    )
    print(s)
    print(m)
    print(r.to_dict())
    db_handler.session.close()
