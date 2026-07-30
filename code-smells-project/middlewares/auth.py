from functools import wraps

from flask import current_app, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

TOKEN_MAX_AGE_SEGUNDOS = 3600


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="auth-token")


def gerar_token(usuario_id, tipo):
    return _serializer().dumps({"usuario_id": usuario_id, "tipo": tipo})


def verificar_token(token):
    try:
        return _serializer().loads(token, max_age=TOKEN_MAX_AGE_SEGUNDOS)
    except (BadSignature, SignatureExpired):
        return None


def require_admin_auth(view):
    """Protege rotas administrativas: exige 'Authorization: Bearer <token>'
    de um usuário autenticado com tipo == 'admin'."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"erro": "Autenticação necessária"}), 401

        token = auth_header[len("Bearer "):]
        payload = verificar_token(token)
        if not payload:
            return jsonify({"erro": "Token inválido ou expirado"}), 401

        if payload.get("tipo") != "admin":
            return jsonify({"erro": "Acesso restrito a administradores"}), 403

        return view(*args, **kwargs)

    return wrapper
