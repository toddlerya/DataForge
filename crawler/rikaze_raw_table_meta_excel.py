#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/10/11 15:28
# @Author   : guoqun X2590
# @FileName : rikaze_raw_table_meta_excel.py
# @Project  : DataForge

import pathlib
import warnings

from openpyxl import cell, load_workbook

from cruds.table_metadata import table_metadata_save
from database_models.schema import TableMetaDataSchema, TableRawFieldSchema
from database_models.sys_enum import MetaDataSource
from utils.db_manager import DatabaseManager
from utils.file import get_md5
from utils.log import logger


class RKZRawTableMetaExcelLoad:
    def __init__(
        self,
        excel_path: pathlib.Path,
        inner_db_manager: DatabaseManager,
    ):
        # 忽略 openpyxl 的样式警告
        warnings.filterwarnings(
            "ignore", category=UserWarning, module="openpyxl.styles.stylesheet"
        )
        self.excel_path = excel_path
        self.sheet_names: list[str] = []
        self.table_metadatas: list[TableMetaDataSchema] = []
        self.inner_db_manager = inner_db_manager

    def parse_excel(self):
        """
        读取excel并解析
        :param excel_path:
        :return:
        """
        workbook = load_workbook(filename=self.excel_path, read_only=True)
        # 获取所有 sheet 名称
        self.sheet_names = workbook.sheetnames
        for each_sheet_name in self.sheet_names:
            logger.info(f"解析中: {each_sheet_name}")
            table_meta_sheet = workbook[each_sheet_name]
            table_fields: list[TableRawFieldSchema] = []
            # ===== 表结构定义 =====
            # B1:C1 => 表英文名
            # B2:C2 => 表中文名
            # A4:   => 字段英文名
            # B4:   => 字段类型/长度
            # C4:   => 字段注释
            # D4:   => 字典类别代码(dict_category_code) 【可以为空】
            # E4:   => 字典类别代码包含级别(dictkey_with_nlevel) 【可以为空】
            # =====================

            # 读取表名称
            table_ename_cell: cell.cell.Cell = table_meta_sheet["B1"]
            if not table_ename_cell.value:
                logger.error(f"未获取表英文名称, 跳过! sheet_name: {each_sheet_name}")
                break
            table_ename_cell_value = table_ename_cell.value
            table_cname_cell: cell.cell.Cell = table_meta_sheet["B2"]
            if not table_cname_cell.value:
                logger.error(f"未获取表中文名, 跳过! sheet_name: {each_sheet_name}")
                break
            table_cname_cell_value = table_cname_cell.value
            # 读取字段信息
            row_idx = 4
            while True:
                # 读取A列字段英文名称
                en_name_cell = table_meta_sheet.cell(row=row_idx, column=1)
                if not en_name_cell.value:
                    # 字段英文名称为空，结束读取
                    break
                en_name_cell_value = en_name_cell.value
                field_type_cell_value = table_meta_sheet.cell(
                    row=row_idx, column=2
                ).value
                cn_name_cell_value = table_meta_sheet.cell(row=row_idx, column=3).value
                dict_category_code_cell_value = table_meta_sheet.cell(
                    row=row_idx, column=4
                ).value
                dictkey_with_nlevel_cell_value = table_meta_sheet.cell(
                    row=row_idx, column=5
                ).value
                dict_key_cell_value = (
                    dictkey_with_nlevel_cell_value
                    if dictkey_with_nlevel_cell_value
                    else dict_category_code_cell_value
                )
                table_raw_field = TableRawFieldSchema(
                    en_name=str(en_name_cell_value),
                    cn_name=str(cn_name_cell_value)
                    if cn_name_cell_value is not None
                    else "",
                    desc=str(cn_name_cell_value)
                    if cn_name_cell_value is not None
                    else "",
                    field_type=str(field_type_cell_value)
                    if field_type_cell_value is not None
                    else "",
                    dict_key=str(dict_key_cell_value)
                    if dict_key_cell_value is not None
                    else "",
                )
                table_fields.append(table_raw_field)
                row_idx += 1

            table_metadata = TableMetaDataSchema(
                table_en_name=str(table_ename_cell_value),
                table_cn_name=str(table_cname_cell_value),
                description=str(table_cname_cell_value),
                table_fields=table_fields,
                position_type="Oracle",
                storage_type="",
                area_code="",
                area_name="日喀则",
                source=MetaDataSource.excel_file,
                env_name="",
            )
            status, tb_meta_uuid = get_md5(
                f"{table_metadata.table_en_name}"
                f"{table_metadata.source}"
                f"{table_metadata.area_code}"
                f"{table_metadata.area_name}"
            )
            if status is False:
                logger.error(
                    f"计算{table_metadata.source}表{table_metadata.table_en_name}元数据UUID异常!"
                )
            else:
                table_metadata.uuid = tb_meta_uuid
            self.table_metadatas.append(table_metadata)

    def run(self):
        logger.info(f"解析: {self.excel_path.name}")
        self.parse_excel()
        for each_table_metadata_model in self.table_metadatas:
            each_table_metadata_record = each_table_metadata_model.model_dump()
            each_table_metadata_record.update({"remark": self.excel_path.name})
            save_status, save_message = table_metadata_save(
                record=each_table_metadata_record, db_manager=self.inner_db_manager
            )
            if save_status is False:
                logger.error(
                    f"{MetaDataSource.bdos} "
                    f"元数据信息入库异常: {each_table_metadata_record} "
                    f"ERROR: {save_message}"
                )
            else:
                logger.info(f"入库: {self.excel_path.name}")


if __name__ == "__main__":
    db_manager = DatabaseManager()
    obj = RKZRawTableMetaExcelLoad(
        excel_path=pathlib.Path(
            r"F:\GITLAB\DataForge\input_data\日喀则原始表\日喀则原始表信息.xlsx"
        ),
        inner_db_manager=db_manager,
    )
    obj.run()
    db_manager.close()
