#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/6/18 9:53
# @Author   : guoqun X2590
# @FileName : advanced_query.py
# @Project  : DataForge


from typing import Dict, List, Optional

from utils.db_manager import DatabaseManager


def sliding_window_query(
    db_manager: DatabaseManager,
    model_class,
    fields: List[str],
    window_size: int = 50,
    step_size: int = 10,
    order_by_field: str = "id",
    filters: Optional[Dict[str, List[str]]] = None,
    callback: Optional[callable] = None,
):
    """
    执行滑动窗口查询
    Args:
        db_handler: SQLAlchemy数据库操作对象
        model_class: 要查询的模型类
        fields: 要查询的字段列表
        window_size: 窗口大小，默认50
        step_size: 步长，默认10
        order_by_field: 排序字段，默认为"id"
        filters: 查询过滤条件字典
        callback: 每个窗口的回调函数，用于处理查询结果

    Returns:
        所有窗口的查询结果列表
    """

    all_results = []
    offset = 0
    window_index = 0

    # 首先获取总记录数
    total_count_query = db_manager.get_session().query(model_class)
    if filters:
        for field, value_slice in filters.items():
            total_count_query = total_count_query.filter(
                getattr(model_class, field).in_(value_slice)
            )
    total_count = total_count_query.count()

    while offset < total_count:
        # 构建查询
        query = db_handler.session.query(
            *[getattr(model_class, field) for field in fields]
        )

        # 应用过滤条件
        for field, value_slice in filters.items():
            total_count_query = total_count_query.filter(
                getattr(model_class, field).in_(value_slice)
            )

        # 排序、分页
        query = query.order_by(getattr(model_class, order_by_field))
        query = query.offset(offset).limit(window_size)

        # 执行查询
        results = query.all()

        if not results:
            break

        # 转换为字典格式
        windows_data = []
        for row in results:
            row_dict = {}
            for i, field in enumerate(fields):
                row_dict[field] = row[i]
            windows_data.append(row_dict)

        # actual_end = min(offset + len(windows_data) - 1, total_count - 1)
        if callback:
            callback(windows_data, window_index, offset)

        all_results.append(windows_data)

        # 移动窗口
        offset += step_size
        window_index += 1

        # 如果当前窗口数据不足window_size，说明已经到了末尾，但数据已经添加到了all_results中，结束循环
        if len(results) < window_size:
            break

    return all_results


if __name__ == "__main__":
    from database_models.models import TableMetaDataInfo

    def print_cb(windows_data, window_index, offset):
        print(f"当前窗口: {window_index} 当前偏移量: {offset} 当前数据: {windows_data}")
        pass

    db_manager = DatabaseManager()
    all_results = sliding_window_query(
        db_manager=db_manager,
        model_class=TableMetaDataInfo,
        fields=["table_en_name", "table_cn_name", "description"],
        # filters={"source": "盘古"},
        callback=print_cb,
    )
    db_manager.close()
