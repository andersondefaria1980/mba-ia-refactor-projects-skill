from flask import Blueprint

from controllers import main_controller
from middlewares.auth import login_required

main_bp = Blueprint("main", __name__)

main_bp.add_url_rule("/", "index", login_required(main_controller.index), methods=["GET"])
main_bp.add_url_rule("/health", "health_check", login_required(main_controller.health_check), methods=["GET"])
