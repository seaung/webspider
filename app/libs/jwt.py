from functools import wraps
from typing import Callable, TypeVar
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_current_user, create_access_token, create_refresh_token, get_jwt

F = TypeVar("F", bound=Callable[..., object])


jwt = JWTManager()


def require_access_level(access_level: str) -> Callable[[F], F]:
    def decorator(f: F) -> F:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            current_user = get_current_user()
            __check_is_active(current_user)
            if current_user.get("scope") != access_level:
                raise ValueError
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        token = get_jwt()
        return f(*args, **kwargs)
    return wrapper


def __check_is_active(current_user):
    """check user is actived"""
    ...
