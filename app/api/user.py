from flask import Blueprint, request, jsonify
from app.models.users import UsersModel
from app.libs.jwt import generate_tokens, refresh_access_token, revoke_token, get_jwt, login_required
from app.models.base import db
from app.validators.forms import LoginRequestFrom

user = Blueprint('user', __name__)


@user.route('/register', methods=['POST'])
def register():
    """用户注册
    
    请求参数:
        username: 用户名
        password: 密码
    
    返回:
        成功: {"msg": "注册成功"}, 201
        失败: {"msg": "错误信息"}, 400
    """
    data = request.get_json()
    if not data:
        return jsonify({"msg": "无效的请求数据"}), 400
        
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"msg": "用户名和密码不能为空"}), 400
    
    # 检查用户名是否已存在
    existing_user = UsersModel.query.filter(UsersModel.nickname == username).first()
    if existing_user:
        return jsonify({"msg": "用户名已存在"}), 400
    
    # 创建新用户
    new_user = UsersModel()
    new_user.nickname = username
    new_user.password = password
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "注册成功"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"注册失败: {str(e)}"}), 500


@user.route('/login', methods=['POST'])
def login():
    """用户登录
    
    请求参数:
        username: 用户名
        password: 密码
    
    返回:
        成功: {"access_token": "...", "refresh_token": "..."}, 200
        失败: {"msg": "错误信息"}, 401
    """
    form = LoginRequestFrom()
    
    # 表单验证
    try:
        if not form.validate():
            # 获取第一个验证错误信息
            for field, errors in form.errors.items():
                return jsonify({"msg": errors[0]}), 400
    except Exception as e:
        return jsonify({"msg": "表单验证失败"}), 400
    
    # 验证用户
    user_info = UsersModel.verify(form.username.data, form.password.data)
    if not user_info:
        return jsonify({"msg": "用户名或密码错误"}), 401
    
    # 生成令牌
    tokens = generate_tokens(user_info['id'], user_info)
    
    return jsonify(tokens), 200


@user.route('/refresh', methods=['POST'])
def refresh():
    """刷新访问令牌
    
    请求头:
        Authorization: Bearer <refresh_token>
    
    返回:
        成功: {"access_token": "..."}, 200
        失败: {"msg": "错误信息"}, 401
    """
    try:
        new_token = refresh_access_token()
        return jsonify(new_token), 200
    except Exception as e:
        return jsonify({"msg": f"令牌刷新失败: {str(e)}"}), 401


@user.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出
    
    请求头:
        Authorization: Bearer <access_token>
    
    返回:
        成功: {"msg": "登出成功"}, 200
        失败: {"msg": "错误信息"}, 401
    """
    token = get_jwt()
    jti = token.get('jti')
    
    if jti:
        revoke_token(jti)
        return jsonify({"msg": "登出成功"}), 200
    else:
        return jsonify({"msg": "无效的令牌"}), 401


@user.route('/profile', methods=['GET'])
@login_required
def profile():
    """获取用户个人资料
    
    请求头:
        Authorization: Bearer <access_token>
    
    返回:
        成功: {"id": 1, "username": "...", ...}, 200
        失败: {"msg": "错误信息"}, 401
    """
    token = get_jwt()
    user_id = token.get('sub')
    
    if not user_id:
        return jsonify({"msg": "无效的令牌"}), 401
    
    user = UsersModel.query.get(user_id)
    if not user:
        return jsonify({"msg": "用户不存在"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.nickname
    }), 200