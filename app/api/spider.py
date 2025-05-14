from flask import Blueprint, jsonify, request
from app.scrapyd_client.client import (
    list_projects, list_spiders, list_jobs, schedule_spider, 
    cancel_job, get_job_log, get_daemon_status, delete_project,
    delete_version, list_versions, get_job_stats, get_job_items
)


spider_api = Blueprint("spider_api", __name__)


@spider_api.route("/projects", methods=["GET"])
def get_projects():
    """获取所有爬虫项目"""
    projects = list_projects()
    return jsonify({"code": 200, "data": projects})


@spider_api.route("/spiders", methods=["GET"])
def get_spiders():
    """获取指定项目的爬虫列表"""
    project = request.args.get("project")
    if not project:
        return jsonify({"code": 400, "message": "缺少项目名称参数"})
    
    spiders = list_spiders(project)
    return jsonify({"code": 200, "data": spiders})


@spider_api.route("/jobs", methods=["GET"])
def get_jobs():
    """获取指定项目的作业列表"""
    project = request.args.get("project")
    if not project:
        return jsonify({"code": 400, "message": "缺少项目名称参数"})
    
    jobs = list_jobs(project)
    return jsonify({"code": 200, "data": jobs})


@spider_api.route("/schedule", methods=["POST"])
def schedule():
    """调度爬虫运行"""
    data = request.json
    project = data.get("project")
    spider = data.get("spider")
    settings = data.get("settings", {})
    
    if not project or not spider:
        return jsonify({"code": 400, "message": "缺少必要参数"})
    
    result = schedule_spider(project, spider, settings)
    return jsonify({"code": 200, "data": result})


@spider_api.route("/cancel", methods=["POST"])
def cancel():
    """取消作业"""
    data = request.json
    project = data.get("project")
    job_id = data.get("job_id")
    
    if not project or not job_id:
        return jsonify({"code": 400, "message": "缺少必要参数"})
    
    result = cancel_job(project, job_id)
    return jsonify({"code": 200, "data": result})


@spider_api.route("/log", methods=["GET"])
def get_log():
    """获取作业日志"""
    project = request.args.get("project")
    spider = request.args.get("spider")
    job_id = request.args.get("job_id")
    log_type = request.args.get("log_type", "log")
    
    if not project or not spider or not job_id:
        return jsonify({"code": 400, "message": "缺少必要参数"})
    
    log = get_job_log(project, spider, job_id, log_type)
    return jsonify({"code": 200, "data": log})


@spider_api.route("/status", methods=["GET"])
def get_status():
    """获取Scrapyd守护进程状态"""
    status = get_daemon_status()
    return jsonify({"code": 200, "data": status})


@spider_api.route("/versions", methods=["GET"])
def get_versions():
    """获取项目版本列表"""
    project = request.args.get("project")
    if not project:
        return jsonify({"code": 400, "message": "缺少项目名称参数"})
    
    versions = list_versions(project)
    return jsonify({"code": 200, "data": versions})


@spider_api.route("/project", methods=["DELETE"])
def remove_project():
    """删除项目"""
    project = request.args.get("project")
    if not project:
        return jsonify({"code": 400, "message": "缺少项目名称参数"})
    
    result = delete_project(project)
    return jsonify({"code": 200, "data": result})


@spider_api.route("/version", methods=["DELETE"])
def remove_version():
    """删除项目版本"""
    project = request.args.get("project")
    version = request.args.get("version")
    
    if not project or not version:
        return jsonify({"code": 400, "message": "缺少必要参数"})
    
    result = delete_version(project, version)
    return jsonify({"code": 200, "data": result})


@spider_api.route("/job/stats", methods=["GET"])
def get_stats():
    """获取作业统计信息"""
    project = request.args.get("project")
    job_id = request.args.get("job_id")
    
    if not project or not job_id:
        return jsonify({"code": 400, "message": "缺少必要参数"})
    
    stats = get_job_stats(project, job_id)
    return jsonify({"code": 200, "data": stats})


@spider_api.route("/job/items", methods=["GET"])
def get_items():
    """获取作业采集的数据项"""
    project = request.args.get("project")
    spider = request.args.get("spider")
    job_id = request.args.get("job_id")
    
    if not project or not spider or not job_id:
        return jsonify({"code": 400, "message": "缺少必要参数"})
    
    items = get_job_items(project, spider, job_id)
    return jsonify({"code": 200, "data": items})
