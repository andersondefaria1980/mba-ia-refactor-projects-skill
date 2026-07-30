import logging

from flask import current_app, jsonify

logger = logging.getLogger(__name__)


def reset_database():
    """Apaga todos os dados de negócio. Requer autenticação de admin
    (ver middlewares/auth.require_admin_auth) — antes desta refatoração
    o endpoint era público e destrutivo para qualquer cliente."""
    current_app.config["DB"].reset()
    logger.warning("Banco de dados resetado")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
