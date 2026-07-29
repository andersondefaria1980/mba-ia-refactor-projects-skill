from flask import Blueprint

from controllers import task_controller as controller
from middlewares.auth import login_required

task_bp = Blueprint('tasks', __name__)

task_bp.add_url_rule('/tasks', 'get_tasks', controller.get_tasks, methods=['GET'])
task_bp.add_url_rule('/tasks/search', 'search_tasks', controller.search_tasks, methods=['GET'])
task_bp.add_url_rule('/tasks/stats', 'task_stats', controller.task_stats, methods=['GET'])
task_bp.add_url_rule('/tasks/<int:task_id>', 'get_task', controller.get_task, methods=['GET'])
task_bp.add_url_rule(
    '/tasks', 'create_task', login_required(controller.create_task), methods=['POST']
)
task_bp.add_url_rule(
    '/tasks/<int:task_id>', 'update_task', login_required(controller.update_task), methods=['PUT']
)
task_bp.add_url_rule(
    '/tasks/<int:task_id>', 'delete_task', login_required(controller.delete_task), methods=['DELETE']
)
