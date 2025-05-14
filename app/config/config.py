class BaseConfig:
    MODE = False
    JWT_SECRET_KEY = "xxxx-1234-5678===="
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 访问令牌过期时间，1小时
    JWT_REFRESH_TOKEN_EXPIRES = 604800  # 刷新令牌过期时间，7天
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"


class Development(BaseConfig):
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = "sqlite:///dev.db"
    SQLALCHEMY_ECHO = True


class Productions(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:password@localhost/webspider_db"
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_MAX_OVERFLOW = 20


configs = {
    "dev": Development(),
    "prod": Productions(),
}
