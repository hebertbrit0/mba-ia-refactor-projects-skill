from flask import jsonify

from models import pedido_model


def reset_database():
    pedido_model.resetar()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


def executar_query():
    return jsonify({
        "erro": "Execução de SQL arbitrário desabilitada",
        "sucesso": False,
    }), 403
