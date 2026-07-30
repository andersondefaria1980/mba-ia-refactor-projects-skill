from flask import Blueprint

from controllers import admin_controller
from middlewares.auth import require_admin_auth

admin_bp = Blueprint("admin", __name__)

admin_bp.add_url_rule(
    "/admin/reset-db",
    "reset_database",
    require_admin_auth(admin_controller.reset_database),
    methods=["POST"],
)

# O antigo endpoint POST /admin/query (executava SQL arbitrário enviado pelo
# cliente sem autenticação) foi removido — ver ARCHITECTURE AUDIT REPORT,
# finding CRITICAL "Endpoint de Execução Arbitrária (SQL)". Não há
# substituto: não existia caso de uso legítimo de produção para ele.
