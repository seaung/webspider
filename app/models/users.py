from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String
from app.models.base import BaseModel


class UsersModel(BaseModel):
    __tablename__ = "users_model"
    id = Column(Integer, primary_key=True)
    nickname = Column(String(32), unique=True)
    _password = Column("password", String(128))

    @property
    def password(self):
        return self._password

    @property.setter
    def password(self, raw: str) -> None:
        self._password = generate_password_hash(raw)

    @staticmethod
    def verify(username: str, password: str) -> dict:
        user = UsersModel.query.filter(UsersModel.nickname == username).first()
        if not user:
            return None

        if not user.check_password(password):
            return None

        return {
            "uuid": user.id,
            "username": user.username,
        }

    def check_password(self, raw_password: str) -> bool:
        if not self._password:
            return False
        return check_password_hash(self._password, raw_password)
