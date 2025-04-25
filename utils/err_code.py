#!/usr/bin/env python
# coding: utf-8
# @File    :   err_code.py
# @Time    :   2023/11/24 18:36
# @Author  :   guo qun X2590
# @Desc    :   None


class ErrorCode(object):
    """
    错误码指定原则:
    1. 快速溯源
    2. 简单易记
    3. 沟通标准化

    错误类型 + 错误编号

    错误类型:
        A --> 输入参数错误
        B --> 数据处理错误
        C --> 文件操作错误
        D --> 数据库错误
        E --> 网络请求错误
        T --> TestToolHub接口错误

    错误编号:
        四位数字
        大类之间步长间距为100
    """

    def __init__(self):
        self.DEFAULT = {"code": "00000", "description": "ok"}

        self.ARGS_MISS_ERROR = {"code": "A1000", "description": "参数项缺失错误"}

        self.ARGS_NOT_FOUND_ERROR = {"code": "A2000", "description": "参数值未找到"}

        self.ARGS_VALUE_ERROR = {"code": "A3000", "description": "参数值错误"}

        self.SYSTEM_CREATE_DIR_ERROR = {"code": "C1000", "description": "创建目录失败"}

        self.SYSTEM_MOVE_ERROR = {"code": "C2000", "description": "移动目录或文件失败"}

        self.SYSTEM_DELETE_ERROR = {"code": "C3000", "description": "删除文件或目录失败"}

        self.SYSTEM_UNCOMPRESS_ERROR = {"code": "C4000", "description": "解压缩文件失败"}

        self.SYSTEM_SAVE_ERROR = {"code": "C5000", "description": "写文件失败"}

        self.DB_CONNECT_ERROR = {"code": "D0000", "description": "数据库连接失败"}

        self.DB_INSERT_OR_UPDATE_ERROR = {
            "code": "D1000",
            "description": "数据库INSERT or UPDATE错误",
        }

        self.DB_SQL_EXECUTE_ERROR = {"code": "D2000", "description": "数据库SQL执行错误"}

        self.DB_SAFE_CHECK_ERROR = {"code": "D3000", "description": "数据库查询SQL安全检查不通过"}

        self.DB_QUERY_ERROR = {"code": "D4000", "description": "数据库查询异常"}

        self.HTTP_UNAUTHORIZED_ERROR = {"code": "E4010", "description": "用户名或密码错误"}

        self.HTTP_DATA_EXCEPTION = {"code": "E4010", "description": "用户名或密码错误"}

        self.BACKGROUND_TASK_EXCEPTION = {"code": "F1000", "description": "创建后台任务失败"}

        self.TTH_EXCEPTION = {"code": "T1000", "description": "TestToolHub的API异常"}

        self.DATA_DUMP = {"code": "J1000", "description": "数据重复"}

        self.DATA_GEN_ERROR = {"code": "J2000", "description": "数据生成失败"}



error_code = ErrorCode()