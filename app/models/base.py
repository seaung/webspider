from typing import Any
from contextlib import contextmanager
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from sqlalchemy.orm import Query as BaseQuery
from sqlalchemy import select, Column, Integer, SmallInteger


class Query(BaseQuery):
    """自定义扩展Query类
    覆写filter_by方法
    """

    def filter_by(self, **kwargs):
        """自定义过滤逻辑"""
        if "status" in kwargs.keys():
            kwargs["status"] = 1
        stmt = select(self._entity_from_pre_ent()).filter_by(**kwargs)
        return self.session.execute(stmt).scalar()


class SQLAlchemy(_SQLAlchemy):
    """自定义SQLAlchemy基类"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Query = Query

    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


db = SQLAlchemy()


class BaseModel(db.Model):
    """自定义模型基类
    所有的数据模型都需要继承该类
    """
    __abstract__ = True
    created_time = Column(Integer)
    status = Column(SmallInteger, default=1)

    def __init__(self) -> None:
        self.created_time = int(datetime.now().timestamp())

    def __getitem__(self, item) -> Any:
        return getattr(self, item)

    def set_attrs(self, attrs_dict: Any) -> None:
        """自动设置数据库字段"""
        for k, v in attrs_dict.items():
            if hasattr(self, k) and k != 'id':
                setattr(self, k, v)

    def delete(self) -> None:
        """软删除数据记录"""
        self.status = 0
