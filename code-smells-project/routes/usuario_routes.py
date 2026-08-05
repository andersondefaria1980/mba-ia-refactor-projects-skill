from flask import Blueprint

from controllers import usuario_controller
from middlewares.auth import login_required

usuario_bp = Blueprint("usuarios", __name__)

usuario_bp.add_url_rule(
    "/usuarios", "listar_usuarios", login_required(usuario_controller.listar_usuarios), methods=["GET"]
)
usuario_bp.add_url_rule(
    "/usuarios/<int:id>", "buscar_usuario", login_required(usuario_controller.buscar_usuario), methods=["GET"]
)
usuario_bp.add_url_rule(
    "/usuarios", "criar_usuario", login_required(usuario_controller.criar_usuario), methods=["POST"]
)
# /login é o único endpoint público — é o meio de obter o token exigido por
# todas as demais rotas do projeto.
usuario_bp.add_url_rule("/login", "login", usuario_controller.login, methods=["POST"])
