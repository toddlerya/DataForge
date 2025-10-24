#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/16 17:38
# @Author   : guoqun X2590
# @Desc     : 任务信息结构

from typing import Optional

from pydantic import ConfigDict, Field, model_validator

from database_models.schema import TaskDataSchema


class TaskPayloadSchmea(TaskDataSchema):
    """
    任务信息定义
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    parent_dg_task_id: Optional[str] = Field(
        default="",
        description="父任务DG的任务ID, 针对AI创建任务人工修改派生新任务的情况",
    )
    parent_rule_name: Optional[str] = Field(
        default="",
        description="父任务DG的任务规则名称, 针对AI创建任务人工修改派生新任务的情况",
    )

    @model_validator(mode="after")
    def validate_all(self) -> "TaskPayloadSchmea":
        # 1. 非空校验
        non_empty_fields = {
            "table_en_name",
            "rule_name",
            "task_rule",
            # "parent_dg_task_id",
            # "parent_rule_name",
        }
        for field_name in non_empty_fields:
            value = getattr(self, field_name, None)
            if value is None:
                raise ValueError(f"{field_name} 不可为空")
            if isinstance(value, (str, dict, list)):
                if len(value) == 0:
                    raise ValueError(f"{field_name} 不可为空 {type(value).__name__}")
        # 2. 长度校验
        # if self.parent_dg_task_id and len(self.parent_dg_task_id) < 32:
        #     raise ValueError("parent_dg_task_id 长度必须大于等于 32 位")
        if self.task_uuid and len(self.task_uuid) < 32:
            raise ValueError("task_uuid 长度必须大于等于 32 位")
        # 3. task_rule 内容校验（可选）
        if len(self.task_rule) == 0:
            raise ValueError("task_rule 不可为空数组")
        for i, rule in enumerate(self.task_rule):
            if not rule:
                raise ValueError(f"task_rule 中第 {i + 1} 个规则不可为空")
        return self
