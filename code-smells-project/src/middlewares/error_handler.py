import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({"erro": e.description, "sucesso": False}), e.code

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        logger.exception("Erro não tratado")
        # Nunca vazar str(e) crua ao cliente (pode conter fragmento de SQL/schema).
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
