import logging

from flask import current_app, jsonify, request

from models import pedido_model

logger = logging.getLogger(__name__)


def _conn():
    return current_app.config["DB"].get_connection()


def criar_pedido():
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        return jsonify({"erro": "Usuario ID é obrigatório"}), 400
    if not itens or len(itens) == 0:
        return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

    resultado = pedido_model.criar(_conn(), usuario_id, itens)

    if "erro" in resultado:
        return jsonify({"erro": resultado["erro"], "sucesso": False}), 400

    logger.info(
        "Notificando pedido %s criado para usuario %s (email, sms, push)",
        resultado["pedido_id"],
        usuario_id,
    )

    return jsonify({
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso",
    }), 201


def listar_pedidos_usuario(usuario_id):
    pedidos = pedido_model.get_por_usuario(_conn(), usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def listar_todos_pedidos():
    pedidos = pedido_model.get_todos(_conn())
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    dados = request.get_json()
    novo_status = dados.get("status", "")

    if novo_status not in pedido_model.STATUS_VALIDOS:
        return jsonify({"erro": "Status inválido"}), 400

    pedido_model.atualizar_status(_conn(), pedido_id, novo_status)

    if novo_status == "aprovado":
        logger.info("Pedido %s aprovado. Preparar envio.", pedido_id)
    if novo_status == "cancelado":
        logger.info("Pedido %s cancelado. Devolver estoque.", pedido_id)

    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200


def relatorio_vendas():
    relatorio = pedido_model.relatorio_vendas(_conn())
    return jsonify({"dados": relatorio, "sucesso": True}), 200
