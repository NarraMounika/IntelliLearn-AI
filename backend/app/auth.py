import os, jwt
from functools import wraps
from flask import request, jsonify


def secret():
    return os.getenv("JWT_SECRET", "dev-only-change-this-secret")


def token_for(user):
    return jwt.encode({"sub": user["id"], "role": user["role"]}, secret(), algorithm="HS256")


def current_user():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    try:
        return jwt.decode(header.split(" ",1)[1], secret(), algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def require_auth(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            user = current_user()
            if not user:
                return jsonify({"error":"Authentication required"}), 401
            if role and user.get("role") != role:
                return jsonify({"error":"You do not have permission for this action"}), 403
            request.user = user
            return fn(*args, **kwargs)
        return wrapped
    return decorator
