from flask import Blueprint

from controllers import pedido_controller
from middlewares.auth import login_required

relatorio_bp = Blueprint("relatorios", __name__)

relatorio_bp.add_url_rule(
    "/relatorios/vendas",
    "relatorio_vendas",
    login_required(pedido_controller.relatorio_vendas),
    methods=["GET"],
)
