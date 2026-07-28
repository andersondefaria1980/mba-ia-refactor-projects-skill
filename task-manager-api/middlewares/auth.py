from functools import wraps

from flask import abort, current_app, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from config import settings


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="refactor-arch-auth")


def gerar_token(usuario):
    return _serializer().dumps({"id": usuario.id, "role": usuario.role})


def verificar_token(token):
    try:
        return _serializer().loads(token, max_age=settings.TOKEN_TTL_SECONDS)
    except (BadSignature, SignatureExpired):
        return None


def login_required(f):
    """Exige um token válido emitido por /login. Não decide papel/role —
    apenas confirma que a requisição vem de um usuário autenticado."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header[len("Bearer "):] if auth_header.startswith("Bearer ") else None
        payload = verificar_token(token) if token else None
        if not payload:
            abort(401, description="Autenticação necessária")
        request.usuario = payload
        return f(*args, **kwargs)

    return wrapper
