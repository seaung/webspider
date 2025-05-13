from flask import Blueprint, jsonify, request
from app.scrapyd_client.client import list_projects, list_jobs


spider_api = Blueprint("spider_api", __name__)


@spider_api.route("/list", methods=["GET"])
def list_project():
    projects = list_projects()

    return jsonify({"code": 200, "data": projects})


@spider_api.route("/jobs", methods=["GET"])
def list_job():
    job = request.data["jobs"]
    jobs = list_jobs(job)
    return jsonify({"code": 200, "data": jobs})
