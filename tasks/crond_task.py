#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/09 10:49
# @Author   : guoqun X2590
# @Desc     : 定时任务

from apscheduler.schedulers.blocking import BlockingScheduler

from tasks.pangu_update_task import pangu_db_crawler_task, pangu_web_crawler_task
from utils.log import logger


class CrondTask:
    def __init__(self, scheduler: BlockingScheduler) -> None:
        self.scheduler = scheduler

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

    def crond_update_pangu_web_data(self):
        """定时更新盘古Web数据"""
        job_id = "crond_update_pangu_web_data"
        if self.check_job_if_exist(job_id=job_id):
            logger.warning(f"任务已经存在, 无需重复创建: {job_id}")
        else:
            logger.info(f"创建任务: {job_id}")
            self.scheduler.add_job(
                id=job_id,
                func=pangu_web_crawler_task,
                trigger="cron",
                # 每日凌晨1点运行
                hour=1,
                minute=0,
                second=0,
                timezone="Asia/Shanghai",
            )

    def crond_update_pangu_db_data(self):
        """定时更新盘古metadata库数据"""
        job_id = "crond_update_pangu_db_data"
        if self.check_job_if_exist(job_id=job_id):
            logger.warning(f"任务已经存在, 无需重复创建: {job_id}")
        else:
            logger.info(f"创建任务: {job_id}")
            self.scheduler.add_job(
                id=job_id,
                func=pangu_db_crawler_task,
                trigger="cron",
                # 每日凌晨2点运行
                hour=2,
                minute=0,
                second=0,
                timezone="Asia/Shanghai",
            )

    def go(self):
        """添加每个定时任务"""
        self.crond_update_pangu_web_data()
        self.crond_update_pangu_db_data()
        self.show_jobs()


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    ct = CrondTask(scheduler=scheduler)
    ct.go()
    # 启动定时任务, 阻塞主线程
    scheduler.start()
