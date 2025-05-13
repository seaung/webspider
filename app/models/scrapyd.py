from app.models.base import BaseModel
from sqlalchemy import Column, Integer, String


class ScrapydModel(BaseModel):
    __tablename__ = "scrapyd_model"
    id = Column(Integer, primary_key=True)
    server_url = Column(String(255))
    server_name = Column(String(32))
    username = Column(String(32))
    password = Column(String(128))
    enable = Column(Integer(default=0))

    def to_dict(self):
        pass
