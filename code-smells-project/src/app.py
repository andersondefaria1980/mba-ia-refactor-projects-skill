import logging

from flask import Flask
from flask_cors import CORS

from src.config import settings
from src.config.db import init_db
from src.middlewares.error_handler import register_error_handlers
from src.views import misc_routes, pedidos_routes, produtos_routes, usuarios_routes


def create_app():
    logging.basicConfig(level=logging.INFO)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG

    CORS(app, origins=settings.CORS_ORIGINS)

    init_db(app)
    register_error_handlers(app)

    app.register_blueprint(produtos_routes.bp)
    app.register_blueprint(usuarios_routes.bp)
    app.register_blueprint(pedidos_routes.bp)
    app.register_blueprint(misc_routes.bp)

    return app
