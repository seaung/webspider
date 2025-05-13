from typing import Any
from . import client


def list_projects() -> Any:
    """列出爬虫项目"""
    return client.list_projects()


def list_spiders() -> Any:
    """列出爬虫列表"""
    return client.list_spiders()


def scheduler_spider(project: str, spider: str, settings: Any):
    """调度爬虫"""
    return client.schedule(project=project, spider=spider,
                           settings=settings or {})


def list_jobs(project):
    """列出工作列表"""
    return client.list_jobs(project)


def cancel_job(project, job_id):
    """关闭作业"""
    return client.cancel_job(project, job_id)
