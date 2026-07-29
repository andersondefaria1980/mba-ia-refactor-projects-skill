import re

from flask import abort, jsonify, request

from src.middlewares.auth import gerar_token
from src.models import usuario_model

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def listar_usuarios():
    usuarios = usuario_model.get_todos()
    return jsonify({"dados": usuarios, "sucesso": True}), 200


def buscar_usuario(id):
    usuario = usuario_model.get_por_id(id)
    if not usuario:
        abort(404, description="Usuário não encontrado")
    return jsonify({"dados": usuario, "sucesso": True}), 200


def criar_usuario():
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="Dados inválidos")

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        abort(400, description="Nome, email e senha são obrigatórios")
    if not EMAIL_REGEX.match(email):
        abort(400, description="Email inválido")
    if len(senha) < 6:
        abort(400, description="Senha deve ter ao menos 6 caracteres")

    usuario_id = usuario_model.criar(nome, email, senha)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    dados = request.get_json(silent=True) or {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not email or not senha:
        abort(400, description="Email e senha são obrigatórios")

    usuario = usuario_model.autenticar(email, senha)
    if not usuario:
        return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401

    token = gerar_token(usuario)
    return jsonify({"dados": usuario, "token": token, "sucesso": True, "mensagem": "Login OK"}), 200
