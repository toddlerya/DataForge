#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/09 10:49
# @Author   : guoqun X2590
# @Desc     : 定时任务

from apscheduler.schedulers.background import BackgroundScheduler

from utils.db_manager import DatabaseManager
from utils.log import logger


class CrondTask:
    def __init__(
        self, scheduler: BackgroundScheduler, db_manager: DatabaseManager
    ) -> None:
        self.scheduler = scheduler
        self.db_manager = db_manager

    def check_job_if_exist(self, job_id):
        """
        检查任务是否存在

        Args:
            job_id (str): 任务ID
        """
        return self.scheduler.get_job(job_id)

    def show_jobs(self):
        logger.info("当前的周期任务信息列表：")
        for i, job in enumerate(self.scheduler.get_jobs()):
            logger.info(f"序号: {i + 1} job信息: {job.id} {job.trigger}")
