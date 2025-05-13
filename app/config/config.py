class BaseConfig:
    MODE = False
    JWT_SECRET_KEY = "xxxx-1234-5678===="


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
