#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/29 17:46
# @Author   : guoqun X2590
# @FileName : bdos_table_meta_excel.py
# @Project  : DataForge


import pathlib
import warnings

from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string

from cruds.table_metadata import table_metadata_save
from database_models.schema import TableMetaDataSchema, TableRawFieldSchema
from database_models.sys_enum import MetaDataSource
from utils.db import Database
from utils.file import find_all_files, get_md5
from utils.log import logger

"""
select
        ordinal_position,
        column_name,
        pd.description,
        case
                when is_nullable = 'YES' then '是'
                when is_nullable = 'NO' then '否'
        end as is_nullable,
        case
                when data_type = 'integer' then 'INT'
                when data_type = 'character varying' then 'STRING'
                when data_type = 'bigint' then 'LONG'
                when data_type = 'boolean' then 'BOOLEAN'
                when data_type = 'text' then 'STRING'
                else data_type
        end as data_type
from
        information_schema."columns" c
left join pg_catalog.pg_description pd on
        pd.objoid = (
        select
                oid
        from
                pg_catalog.pg_class pc
        where
                relname = c.table_name)
        and pd.objsubid = c.ordinal_position
where
        c.table_schema = 'public'
        and c.table_name = 'powerrecord_group_chat_group_base_info'
order by
        ordinal_position;
"""

"""
select
	COLUMN_NAME ,
	COLUMN_TYPE ,
	IS_NULLABLE ,
	COLUMN_COMMENT
from
	information_schema.`COLUMNS` c
where
	TABLE_NAME = 'adu_case_info';
"""


class IntelligenceAnalysisAssistantTableMetaExcelLoad:
    def __init__(
        self,
        table_meta_excel_dir_path: str,
        inner_db: Database,
    ):
        # 忽略 openpyxl 的样式警告
        warnings.filterwarnings(
            "ignore", category=UserWarning, module="openpyxl.styles.stylesheet"
        )
        self.table_meta_excel_dir_path = table_meta_excel_dir_path
        self.inner_db = inner_db

    def find_all_excel(self) -> list[pathlib.Path]:
        """
        查找所有IntelligenceAnalysisAssistant资源表excel路径
        :return:
        """
        logger.info(
            f"查找所有IntelligenceAnalysisAssistant数据资源表excel, 查找目录: {self.table_meta_excel_dir_path}"
        )
        all_excel_path = [
            ele for ele in find_all_files(goal_path=self.table_meta_excel_dir_path)
        ]
        logger.info(
            f"找到IntelligenceAnalysisAssistant数据资源表excel数量: {len(all_excel_path)}"
        )
        return all_excel_path

    @staticmethod
    def parse_excel(excel_path: pathlib.Path) -> TableMetaDataSchema:
        """
        读取excel并解析
        :param excel_path:
        :return:
        """
        wb = load_workbook(filename=excel_path, read_only=True)
        table_fields_sheet = wb["字段"]
        table_fields: list[TableRawFieldSchema] = list()
        # B: 字段英文名*
        # C: 字段属性
        # E: 字典
        # F: 字段说明
        # J: 字段类型*
        # K: 数据项内容是否必填*
        target_columns = ["B", "C", "E", "F", "J", "K"]
        # 获取列索引
        col_indices = [column_index_from_string(col=col) - 1 for col in target_columns]
        for row in table_fields_sheet.iter_rows(min_row=2, values_only=True):
            row_data = {}
            for idx, col in zip(col_indices, target_columns):
                # 检查列索引是否在范围内（避免越界）
                if idx < len(row):
                    value = row[idx]
                    row_data[col] = str(value) if value is not None else ""
                else:
                    row_data[col] = ""  # 列不存在时回填空字符串
            # row_data
            # {'B': 'MD_ID', 'C': '标识ID', 'E': '', 'J': 'STRING', 'K': '否'}
            table_raw_field = TableRawFieldSchema(
                en_name=row_data["B"],
                cn_name=row_data["C"],
                desc=row_data["F"],
                field_type=row_data["J"],
                is_require=0 if row_data["K"] == "否" else 1,
                dict_key=row_data["E"],
                dict_name="",
            )
            table_fields.append(table_raw_field)
        table_resource_sheet = wb["资源"]
        table_ename_cell_value = table_resource_sheet["A2"].value.strip()
        table_cname_cell_value = table_resource_sheet["B2"].value.strip()
        description_cell_value = table_resource_sheet["C2"].value.strip()
        bdos_table_metadata = TableMetaDataSchema(
            table_en_name=table_ename_cell_value,
            table_cn_name=table_cname_cell_value,
            description=description_cell_value,
            table_fields=table_fields,
            position_type="PG",
            source=MetaDataSource.intelligence_analysis_assistant,
            # env_uuid="xxxxxx",
        )
        status, tb_meta_uuid = get_md5(
            f"{bdos_table_metadata.table_en_name}"
            f"{bdos_table_metadata.source}"
            f"{bdos_table_metadata.area_code}"
            f"{bdos_table_metadata.area_name}"
        )
        if status is False:
            logger.error(
                f"计算{bdos_table_metadata.source}表{bdos_table_metadata.table_en_name}元数据UUID异常!"
            )
        else:
            bdos_table_metadata.uuid = tb_meta_uuid
        return bdos_table_metadata

    def run(self):
        for item_excel_path in self.find_all_excel():
            logger.info(f"解析: {item_excel_path.name}")
            each_table_metadata_model = self.parse_excel(item_excel_path)
            each_table_metadata_record = each_table_metadata_model.model_dump()
            each_table_metadata_record.update({"remark": item_excel_path.name})
            save_status, save_message = table_metadata_save(
                record=each_table_metadata_record, db_handler=self.inner_db
            )
            if save_status is False:
                logger.error(
                    f"{MetaDataSource.intelligence_analysis_assistant}元数据信息入库异常: {each_table_metadata_record} ERROR: {save_message}"
                )
            else:
                logger.info(f"入库: {item_excel_path.name}")


if __name__ == "__main__":
    db_handler = Database()
    obj = IntelligenceAnalysisAssistantTableMetaExcelLoad(
        table_meta_excel_dir_path=r"F:\GITLAB\DataForge\input_data\intelligenceAnalysisAssistant",
        inner_db=db_handler,
    )
    obj.run()
    db_handler.session.close()
