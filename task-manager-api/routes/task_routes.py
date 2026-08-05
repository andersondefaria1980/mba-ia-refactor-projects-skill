from flask import Blueprint, jsonify, request

from controllers import task_controller
from middlewares.auth import token_required

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/tasks', methods=['GET'])
@token_required
def get_tasks():
    body, status = task_controller.list_tasks()
    return jsonify(body), status


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
@token_required
def get_task(task_id):
    body, status = task_controller.get_task(task_id)
    return jsonify(body), status


@task_bp.route('/tasks', methods=['POST'])
@token_required
def create_task():
    body, status = task_controller.create_task(request.get_json())
    return jsonify(body), status


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(task_id):
    body, status = task_controller.update_task(task_id, request.get_json())
    return jsonify(body), status


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(task_id):
    body, status = task_controller.delete_task(task_id)
    return jsonify(body), status


@task_bp.route('/tasks/search', methods=['GET'])
@token_required
def search_tasks():
    body, status = task_controller.search_tasks(
        request.args.get('q', ''),
        request.args.get('status', ''),
        request.args.get('priority', ''),
        request.args.get('user_id', ''),
    )
    return jsonify(body), status


@task_bp.route('/tasks/stats', methods=['GET'])
@token_required
def task_stats():
    body, status = task_controller.task_stats()
    return jsonify(body), status
