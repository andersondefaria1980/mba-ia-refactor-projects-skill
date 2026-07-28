from functools import wraps

from flask import abort, current_app, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from src.config import settings


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="refactor-arch-auth")


def gerar_token(usuario):
    return _serializer().dumps({"id": usuario["id"], "tipo": usuario["tipo"]})


def verificar_token(token):
    try:
        return _serializer().loads(token, max_age=settings.ADMIN_TOKEN_TTL_SECONDS)
    except (BadSignature, SignatureExpired):
        return None


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header[len("Bearer "):] if auth_header.startswith("Bearer ") else None
        payload = verificar_token(token) if token else None
        if not payload or payload.get("tipo") != "admin":
            abort(401, description="Acesso restrito a administradores")
        return f(*args, **kwargs)

    return wrapper
