import logging

from flask import Flask
from flask_cors import CORS

from config.database import Database
from config.settings import Settings
from middlewares import error_handler
from routes.admin_routes import admin_bp
from routes.main_routes import main_bp
from routes.pedido_routes import pedido_bp
from routes.produto_routes import produto_bp
from routes.relatorio_routes import relatorio_bp
from routes.usuario_routes import usuario_bp


def create_app():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    app = Flask(__name__)
    app.config["SECRET_KEY"] = Settings.SECRET_KEY
    app.config["DEBUG"] = Settings.DEBUG
    app.config["DB"] = Database(Settings.DATABASE_PATH)

    CORS(app)
    error_handler.register(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(relatorio_bp)
    app.register_blueprint(admin_bp)

    return app


app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://localhost:{Settings.PORT}")
    print("=" * 50)

    app.run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
