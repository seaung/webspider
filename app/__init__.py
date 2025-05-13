from flask import Flask


def register_blueprints(app: Flask) -> None:
    """注册蓝图"""
    from app.api.spider import spider_api
    app.register_blueprint(spider_api)


def register_plugins(app: Flask) -> None:
    """注册flask插件"""
    from flask_jwt_extended import JWTManager
    from app.models.base import db

    db.init_app(app)
    JWTManager(app)


def create_app(env: str = "dev") -> Flask:
    """创建flask实例对象"""
    app = Flask(__name__)

    if env == "dev":
        app.config.from_object("app.config.Development")
    else:
        app.config.from_object("app.config.Productions")

    register_plugins(app)
    register_blueprints(app)

    return app
