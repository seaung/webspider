from functools import wraps
from typing import Callable, TypeVar, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from flask import jsonify, current_app
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_current_user, create_access_token, create_refresh_token, get_jwt, get_jwt_identity

F = TypeVar("F", bound=Callable[..., object])


jwt = JWTManager()

# 存储已撤销的令牌
revoked_tokens = set()


def require_access_level(access_level: str) -> Callable[[F], F]:
    """装饰器：要求用户具有特定的访问级别
    
    Args:
        access_level: 所需的访问级别
        
    Returns:
        装饰器函数
    """
    def decorator(f: F) -> F:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            current_user = get_current_user()
            try:
                __check_is_active(current_user)
            except ValueError as e:
                return jsonify({"msg": str(e)}), 403
                
            if current_user.get("scope") != access_level:
                return jsonify({"msg": "权限不足，无法访问此资源"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def login_required(f: F) -> F:
    """装饰器：要求用户登录
    
    Args:
        f: 被装饰的函数
        
    Returns:
        装饰器函数
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        token = get_jwt()
        
        # 检查令牌是否被撤销
        jti = token.get("jti")
        if jti in revoked_tokens:
            return jsonify({"msg": "令牌已被撤销"}), 401
        
        # 检查用户状态
        current_user = get_current_user()
        try:
            __check_is_active(current_user)
        except ValueError as e:
            return jsonify({"msg": str(e)}), 403
            
        return f(*args, **kwargs)
    return wrapper


def __check_is_active(current_user: Dict[str, Any]) -> None:
    """检查用户是否处于活动状态
    
    Args:
        current_user: 当前用户信息
        
    Raises:
        ValueError: 如果用户未激活或已被禁用
    """
    if not current_user:
        raise ValueError("用户信息不存在")
        
    if not current_user.get("is_active", False):
        raise ValueError("用户账户未激活或已被禁用")


def generate_tokens(user_id: Union[str, int], additional_claims: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """为用户生成访问令牌和刷新令牌
    
    Args:
        user_id: 用户ID
        additional_claims: 要添加到令牌中的额外声明
        
    Returns:
        包含访问令牌和刷新令牌的字典
    """
    if additional_claims is None:
        additional_claims = {}
        
    access_token = create_access_token(
        identity=user_id,
        additional_claims=additional_claims,
        fresh=True
    )
    
    refresh_token = create_refresh_token(identity=user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def refresh_access_token() -> Dict[str, str]:
    """使用刷新令牌生成新的访问令牌
    
    Returns:
        包含新访问令牌的字典
    """
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user, fresh=False)
    
    return {"access_token": new_access_token}


def revoke_token(jti: str) -> None:
    """撤销指定的令牌
    
    Args:
        jti: 令牌的唯一标识符
    """
    revoked_tokens.add(jti)


def get_user_info() -> Dict[str, Any]:
    """获取当前登录用户的信息
    
    Returns:
        用户信息字典
    """
    verify_jwt_in_request()
    return get_current_user()


def is_token_revoked(jti: str) -> bool:
    """检查令牌是否已被撤销
    
    Args:
        jti: 令牌的唯一标识符
        
    Returns:
        如果令牌已被撤销，则为True，否则为False
    """
    return jti in revoked_tokens
