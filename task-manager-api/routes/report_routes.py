from flask import Blueprint, jsonify, request

from controllers import report_controller
from middlewares.auth import token_required

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
@token_required
def summary_report():
    body, status = report_controller.summary_report()
    return jsonify(body), status


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
@token_required
def user_report(user_id):
    body, status = report_controller.user_report(user_id)
    return jsonify(body), status


@report_bp.route('/categories', methods=['GET'])
@token_required
def get_categories():
    body, status = report_controller.list_categories()
    return jsonify(body), status


@report_bp.route('/categories', methods=['POST'])
@token_required
def create_category():
    body, status = report_controller.create_category(request.get_json())
    return jsonify(body), status


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
@token_required
def update_category(cat_id):
    body, status = report_controller.update_category(cat_id, request.get_json())
    return jsonify(body), status


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@token_required
def delete_category(cat_id):
    body, status = report_controller.delete_category(cat_id)
    return jsonify(body), status
