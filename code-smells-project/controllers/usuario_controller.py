import logging

from flask import current_app, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from middlewares.auth import gerar_token
from models import usuario_model

logger = logging.getLogger(__name__)


def _conn():
    return current_app.config["DB"].get_connection()


def listar_usuarios():
    usuarios = usuario_model.get_todos(_conn())
    return jsonify({"dados": usuarios, "sucesso": True}), 200


def buscar_usuario(id):
    usuario = usuario_model.get_por_id(_conn(), id)
    if usuario:
        return jsonify({"dados": usuario, "sucesso": True}), 200
    return jsonify({"erro": "Usuário não encontrado"}), 404


def criar_usuario():
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400

    usuario_id = usuario_model.criar(_conn(), nome, email, generate_password_hash(senha))
    logger.info("Usuário criado: %s", email)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    dados = request.get_json()
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    usuario = usuario_model.get_por_email(_conn(), email)
    if usuario and check_password_hash(usuario["senha"], senha):
        logger.info("Login bem-sucedido: %s", email)
        resposta = {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "tipo": usuario["tipo"],
            "token": gerar_token(usuario["id"], usuario["tipo"]),
        }
        return jsonify({"dados": resposta, "sucesso": True, "mensagem": "Login OK"}), 200

    logger.info("Login falhou: %s", email)
    return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
