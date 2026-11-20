from flask import jsonify, request

from middlewares.auth import current_user
from models import pedido_model


def reset_database():
    user = current_user()
    if user is None:
        return jsonify({"erro": "Não autenticado", "sucesso": False}), 401
    if user.get("tipo") != "admin":
        return jsonify({"erro": "Acesso negado", "sucesso": False}), 403
    pedido_model.resetar()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


def executar_query():
    return jsonify({
        "erro": "Execução de SQL arbitrário desabilitada",
        "sucesso": False,
    }), 403
