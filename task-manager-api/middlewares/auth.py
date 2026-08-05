from functools import wraps

import jwt
from flask import jsonify, request

from config.settings import Settings
from models.user import User


def token_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Autenticação necessária"}), 401

        token = auth_header[len("Bearer "):]
        try:
            payload = jwt.decode(token, Settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        user = User.query.get(payload.get("user_id"))
        if not user or not user.active:
            return jsonify({"error": "Token inválido"}), 401

        request.current_user = user
        return view(*args, **kwargs)

    return wrapper
