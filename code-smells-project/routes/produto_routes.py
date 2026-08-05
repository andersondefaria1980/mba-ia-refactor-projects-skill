from flask import Blueprint

from controllers import produto_controller
from middlewares.auth import login_required

produto_bp = Blueprint("produtos", __name__)

produto_bp.add_url_rule(
    "/produtos", "listar_produtos", login_required(produto_controller.listar_produtos), methods=["GET"]
)
produto_bp.add_url_rule(
    "/produtos/busca", "buscar_produtos", login_required(produto_controller.buscar_produtos), methods=["GET"]
)
produto_bp.add_url_rule(
    "/produtos/<int:id>", "buscar_produto", login_required(produto_controller.buscar_produto), methods=["GET"]
)
produto_bp.add_url_rule(
    "/produtos", "criar_produto", login_required(produto_controller.criar_produto), methods=["POST"]
)
produto_bp.add_url_rule(
    "/produtos/<int:id>",
    "atualizar_produto",
    login_required(produto_controller.atualizar_produto),
    methods=["PUT"],
)
produto_bp.add_url_rule(
    "/produtos/<int:id>",
    "deletar_produto",
    login_required(produto_controller.deletar_produto),
    methods=["DELETE"],
)
