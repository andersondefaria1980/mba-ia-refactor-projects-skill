from flask import abort, jsonify, request

from src.models import pedido_model
from src.services import notification_service


def criar_pedido():
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="Dados inválidos")

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        abort(400, description="Usuario ID é obrigatório")
    if not itens:
        abort(400, description="Pedido deve ter pelo menos 1 item")

    try:
        resultado = pedido_model.criar(usuario_id, itens)
    except pedido_model.PedidoError as e:
        return jsonify({"erro": str(e), "sucesso": False}), 400

    notification_service.notificar_novo_pedido(resultado["pedido_id"], usuario_id)

    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def listar_pedidos_usuario(usuario_id):
    pedidos = pedido_model.get_por_usuario(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def listar_todos_pedidos():
    pedidos = pedido_model.get_todos()
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    dados = request.get_json(silent=True) or {}
    novo_status = dados.get("status", "")

    if novo_status not in ["pendente", "aprovado", "enviado", "entregue", "cancelado"]:
        abort(400, description="Status inválido")

    pedido_model.atualizar_status(pedido_id, novo_status)
    notification_service.notificar_mudanca_status(pedido_id, novo_status)

    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200


def relatorio_vendas():
    agregados = pedido_model.obter_agregados_vendas()
    faturamento = agregados["faturamento_bruto"]
    desconto = _calcular_desconto(faturamento)
    total_pedidos = agregados["total_pedidos"]

    return jsonify({
        "dados": {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": agregados["pedidos_pendentes"],
            "pedidos_aprovados": agregados["pedidos_aprovados"],
            "pedidos_cancelados": agregados["pedidos_cancelados"],
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
        },
        "sucesso": True,
    }), 200


def _calcular_desconto(faturamento):
    """Regra de negócio de desconto por faixa de faturamento (não pertence ao Model)."""
    if faturamento > 10000:
        return faturamento * 0.1
    if faturamento > 5000:
        return faturamento * 0.05
    if faturamento > 1000:
        return faturamento * 0.02
    return 0
