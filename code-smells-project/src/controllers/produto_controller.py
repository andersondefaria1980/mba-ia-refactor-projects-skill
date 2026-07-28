from flask import abort, jsonify, request

from src.config import settings
from src.models import produto_model


def _validar(dados):
    if not dados:
        abort(400, description="Dados inválidos")
    for campo in ("nome", "preco", "estoque"):
        if campo not in dados:
            abort(400, description=f"{campo.capitalize()} é obrigatório")
    if dados["preco"] < 0:
        abort(400, description="Preço não pode ser negativo")
    if dados["estoque"] < 0:
        abort(400, description="Estoque não pode ser negativo")
    nome = dados["nome"]
    if len(nome) < 2:
        abort(400, description="Nome muito curto")
    if len(nome) > 200:
        abort(400, description="Nome muito longo")
    categoria = dados.get("categoria", "geral")
    if categoria not in settings.CATEGORIAS_VALIDAS:
        abort(400, description=f"Categoria inválida. Válidas: {settings.CATEGORIAS_VALIDAS}")


def listar_produtos():
    produtos = produto_model.get_todos()
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(id):
    produto = produto_model.get_por_id(id)
    if not produto:
        abort(404, description="Produto não encontrado")
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar_produto():
    dados = request.get_json(silent=True)
    _validar(dados)
    produto_id = produto_model.criar(
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(id):
    if not produto_model.get_por_id(id):
        abort(404, description="Produto não encontrado")
    dados = request.get_json(silent=True)
    _validar(dados)
    produto_model.atualizar(
        id,
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(id):
    if not produto_model.get_por_id(id):
        abort(404, description="Produto não encontrado")
    produto_model.deletar(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    preco_min = request.args.get("preco_min", type=float)
    preco_max = request.args.get("preco_max", type=float)
    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
