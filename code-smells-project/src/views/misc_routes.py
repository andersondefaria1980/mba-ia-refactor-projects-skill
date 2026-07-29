from flask import Blueprint

from src.controllers import misc_controller as controller
from src.middlewares.auth import admin_required

bp = Blueprint("misc", __name__)

bp.add_url_rule("/", "index", controller.index, methods=["GET"])
bp.add_url_rule("/health", "health_check", controller.health_check, methods=["GET"])
bp.add_url_rule(
    "/admin/reset-db",
    "reset_database",
    admin_required(controller.reset_database),
    methods=["POST"],
)
