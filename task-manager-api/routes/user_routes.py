from flask import Blueprint

from controllers import user_controller as controller
from middlewares.auth import login_required

user_bp = Blueprint('users', __name__)

user_bp.add_url_rule('/users', 'get_users', controller.get_users, methods=['GET'])
user_bp.add_url_rule('/users/<int:user_id>', 'get_user', controller.get_user, methods=['GET'])
user_bp.add_url_rule(
    '/users/<int:user_id>/tasks', 'get_user_tasks', controller.get_user_tasks, methods=['GET']
)
user_bp.add_url_rule('/users', 'create_user', controller.create_user, methods=['POST'])
user_bp.add_url_rule(
    '/users/<int:user_id>', 'update_user', login_required(controller.update_user), methods=['PUT']
)
user_bp.add_url_rule(
    '/users/<int:user_id>', 'delete_user', login_required(controller.delete_user), methods=['DELETE']
)
user_bp.add_url_rule('/login', 'login', controller.login, methods=['POST'])
