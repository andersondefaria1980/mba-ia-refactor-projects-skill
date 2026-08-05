from flask import Blueprint, jsonify, request

from controllers import user_controller
from middlewares.auth import token_required

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    body, status = user_controller.list_users()
    return jsonify(body), status


@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    body, status = user_controller.get_user(user_id)
    return jsonify(body), status


@user_bp.route('/users', methods=['POST'])
@token_required
def create_user():
    body, status = user_controller.create_user(request.get_json())
    return jsonify(body), status


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    body, status = user_controller.update_user(user_id, request.get_json())
    return jsonify(body), status


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    body, status = user_controller.delete_user(user_id)
    return jsonify(body), status


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
@token_required
def get_user_tasks(user_id):
    body, status = user_controller.get_user_tasks(user_id)
    return jsonify(body), status


@user_bp.route('/login', methods=['POST'])
def login():
    body, status = user_controller.login(request.get_json())
    return jsonify(body), status
