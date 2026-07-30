import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger("code_smells_project")


def register(app):
    """Handler central de erros não previstos.

    Controllers continuam tratando erros esperados do domínio (404, 400, 401)
    com respostas específicas; apenas exceções não capturadas chegam aqui,
    evitando repetir o mesmo try/except genérico em cada função e sem
    vazar detalhes internos (mensagem de exceção, stack trace) ao cliente.
    """

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        if isinstance(e, HTTPException):
            return e
        logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
