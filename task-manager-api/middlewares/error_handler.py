import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from database import db

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        if isinstance(error, HTTPException):
            return error

        db.session.rollback()
        logger.exception("Erro nao tratado")
        return jsonify({'error': 'Erro interno do servidor'}), 500
