import logging

logger = logging.getLogger(__name__)


def notificar_novo_pedido(pedido_id, usuario_id):
    logger.info("Novo pedido criado", extra={"pedido_id": pedido_id, "usuario_id": usuario_id})


def notificar_mudanca_status(pedido_id, novo_status):
    if novo_status == "aprovado":
        logger.info("Pedido aprovado, preparar envio", extra={"pedido_id": pedido_id})
    elif novo_status == "cancelado":
        logger.info("Pedido cancelado, devolver estoque", extra={"pedido_id": pedido_id})
