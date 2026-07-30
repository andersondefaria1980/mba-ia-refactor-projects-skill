from flask import current_app, jsonify

from config.settings import Settings
from models import pedido_model, produto_model, usuario_model


def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


def health_check():
    try:
        db = current_app.config["DB"]
        db.ping()
        conn = db.get_connection()

        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": {
                "produtos": produto_model.contar(conn),
                "usuarios": usuario_model.contar(conn),
                "pedidos": pedido_model.contar(conn),
            },
            "versao": "1.0.0",
            "ambiente": "producao",
            "db_path": Settings.DATABASE_PATH,
        }), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhes": str(e)}), 500
