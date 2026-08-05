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


def _autenticar_requisicao():
    """Extrai e valida o Bearer token da requisição atual.

    Retorna (payload, None) se válido, ou (None, response_de_erro) caso
    contrário — para ser usado diretamente como early-return nos decorators.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, (jsonify({"erro": "Autenticação necessária"}), 401)

    token = auth_header[len("Bearer "):]
    payload = verificar_token(token)
    if not payload:
        return None, (jsonify({"erro": "Token inválido ou expirado"}), 401)

    return payload, None


def login_required(view):
    """Exige 'Authorization: Bearer <token>' válido de qualquer usuário
    autenticado. Usado em todas as rotas do projeto, exceto /login."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        payload, erro = _autenticar_requisicao()
        if erro:
            return erro
        request.current_user = payload
        return view(*args, **kwargs)

    return wrapper


def require_admin_auth(view):
    """Exige token válido de um usuário autenticado com tipo == 'admin'."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        payload, erro = _autenticar_requisicao()
        if erro:
            return erro
        if payload.get("tipo") != "admin":
            return jsonify({"erro": "Acesso restrito a administradores"}), 403
        request.current_user = payload
        return view(*args, **kwargs)

    return wrapper
