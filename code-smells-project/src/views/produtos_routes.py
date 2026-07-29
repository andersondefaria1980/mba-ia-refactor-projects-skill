from flask import Blueprint

from src.controllers import produto_controller as controller

bp = Blueprint("produtos", __name__)

bp.add_url_rule("/produtos", "listar_produtos", controller.listar_produtos, methods=["GET"])
bp.add_url_rule("/produtos/busca", "buscar_produtos", controller.buscar_produtos, methods=["GET"])
bp.add_url_rule("/produtos/<int:id>", "buscar_produto", controller.buscar_produto, methods=["GET"])
bp.add_url_rule("/produtos", "criar_produto", controller.criar_produto, methods=["POST"])
bp.add_url_rule("/produtos/<int:id>", "atualizar_produto", controller.atualizar_produto, methods=["PUT"])
bp.add_url_rule("/produtos/<int:id>", "deletar_produto", controller.deletar_produto, methods=["DELETE"])
