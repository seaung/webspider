from typing import Any
from flask import request
from wtforms import Form as WTForms
from wtforms.validators import DataRequired, Regexp, Length
from wtforms import PasswordField, StringField


class Form(WTForms):
    """自定义表单基类"""

    def __init__(self) -> None:
        data = request.get_json(silent=True)
        args = request.data.to_dict()
        super(Form, self).__init__(data=data, **args)

    def validate_for_api(self) -> Any:
        valid = super(Form, self).validate()
        if not valid:
            raise ValueError()
        return self

    def strip_string_fileds(self) -> Any:
        """去除所有字符串字段的首尾空格"""
        for filed in self._fields.values():
            if isinstance(filed.data, str):
                filed.data = filed.data.strip()
        return self

    def sanitize_string(self, filed_name: Any) -> Any:
        """清理特定字段的特殊字符"""
        if hasattr(self, filed_name):
            filed = getattr(self, filed_name)
            if isinstance(filed.data, str):
                filed.data = ''.join(
                    char for char in filed.data if char.isprintable())
        return self


class LoginRequestFrom(Form):
    """登录请求表单"""
    username = StringField('用户名/邮箱', validators=[
        DataRequired(message='用户名不能为空'),
        Regexp(r'^[\w\.-]+@[\w\.-]+\.\w+$|^[A-Za-z0-9_]+$',
               message='请输入有效的用户名或邮箱地址')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=6, max=22, message='密码长度必须在6-22位之间')
    ])

    def validate(self):
        self.strip_string_fields()
        self.sanitize_string('username')
        return super(LoginRequestFrom, self).validate()
