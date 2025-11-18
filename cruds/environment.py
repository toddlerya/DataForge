#!/usr/bin/env python
# coding: utf-8
# @Time     : 2024/11/21 15:10
# @Author   : guoqun X2590
# @FileName : environment.py
# @Project  : HETUTaskChecker

from sqlalchemy import update

from database_models.models import EnvironmentInfo
from database_models.sys_enum import EnvironmentStatus
from utils.db_manager import DatabaseManager, GenericUpsert
from utils.log import logger


def save_environment_info(
    environment_data: dict, db_manager: DatabaseManager
) -> tuple[bool, str]:
    """
    存储环境配置信息

    Args:
        environment_data (dict): 配置中心的配置信息
        db_manager (DatabaseManager): 数据库连接对象
    """
    try:
        result = GenericUpsert(db=db_manager.db).smart_insert_or_update_single(
            session=db_manager.get_session(),
            model_class=EnvironmentInfo,
            data=environment_data,
        )
        logger.trace(f"save_environment_info: result={result.to_dict()}")
    except Exception as err:
        db_manager.get_session().rollback()
        message = f"数据库写操作错误: {err}"
        return False, message
    else:
        return True, "ok"


def change_env_status(
    env_name: str, status: EnvironmentStatus, db_manager: DatabaseManager
) -> tuple[bool, str]:
    """更新环境配置的状态

    Args:
        env_name (str): _description_
        status (EnvironmentStatus): _description_
        db_manager (DatabaseManager): _description_
    """
    try:
        stmt = (
            update(EnvironmentInfo)
            .where(EnvironmentInfo.env_name == env_name)
            .values(status=status)
        )
        result = db_manager.get_session().execute(stmt)
        db_manager.get_session().commit()
        logger.trace(
            f"更新env_name={env_name}的status为{status} => "
            f"更新了{result.rowcount}条数据"
        )
    except Exception as err:
        db_manager.get_session().rollback()
        message = f"更新env_name={env_name}的status为{status}异常! ERROR: {err}"
        return (False, message)
    return True, "ok"


def query_environment_info_by_env_name(
    env_name: str, db_manager: DatabaseManager
) -> tuple[bool, str, EnvironmentInfo]:
    """
    根据环境名称获取对应的环境配置信息
    :param env_name:
    :param db_manager:
    :return:
    """
    try:
        logger.trace(f"query_environment_info_by_env_name(env_name={env_name})")
        data = (
            db_manager.get_session()
            .query(EnvironmentInfo)
            .filter(EnvironmentInfo.env_name == env_name)
            .one_or_none()
        )
    except Exception as err:
        message = (
            f"根据环境名称获取对应的环境配置信息失败! env_name={env_name} ERROR: {err}"
        )
        return False, message, EnvironmentInfo()
    else:
        return True, "ok", data


def query_environment_info_by_status(
    status: EnvironmentStatus, db_manager: DatabaseManager
) -> tuple[bool, str, list[EnvironmentInfo]]:
    """
    根据状态的环境配置信息
    :param status:
    :param db_manager:
    :return:
    """
    try:
        logger.trace(f"query_environment_info_by_status(status={status})")
        data = (
            db_manager.get_session()
            .query(EnvironmentInfo)
            .filter(EnvironmentInfo.status == status)
            .all()
        )
    except Exception as err:
        message = f"根据状态的环境配置信息失败! status={status} ERROR: {err}"
        return False, message, [EnvironmentInfo()]
    else:
        return True, "ok", data


if __name__ == "__main__":
    db_manager = DatabaseManager()
    s, m, r = query_environment_info_by_env_name(
        env_name="测试部仿真测试环境", db_manager=db_manager
    )
    print(s)
    print(m)
    print(r.to_dict())
    db_manager.close()
