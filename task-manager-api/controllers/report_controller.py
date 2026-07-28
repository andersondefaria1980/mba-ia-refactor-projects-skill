from flask import abort, jsonify

from database import db
from models.user import User
from services import report_service


def summary_report():
    return jsonify(report_service.build_summary_report()), 200


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404, description='Usuário não encontrado')
    return jsonify(report_service.build_user_report(user)), 200
