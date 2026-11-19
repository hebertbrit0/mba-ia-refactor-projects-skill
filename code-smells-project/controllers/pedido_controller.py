from flask import jsonify, request

from models import pedido_model

STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


def _notificar_pedido_criado(pedido_id, usuario_id):
    print(f"ENVIANDO EMAIL: Pedido {pedido_id} criado para usuario {usuario_id}")
    print("ENVIANDO SMS: Seu pedido foi recebido!")
    print("ENVIANDO PUSH: Novo pedido recebido pelo sistema")


def _notificar_status(pedido_id, novo_status):
    if novo_status == "aprovado":
        print(f"NOTIFICAÇÃO: Pedido {pedido_id} foi aprovado! Preparar envio.")
    if novo_status == "cancelado":
        print(f"NOTIFICAÇÃO: Pedido {pedido_id} cancelado. Devolver estoque.")


def criar_pedido():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        return jsonify({"erro": "Usuario ID é obrigatório"}), 400
    if not itens:
        return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

    preparados = []
    total = 0
    for item in itens:
        produto = pedido_model.buscar_produto(item["produto_id"])
        if produto is None:
            return jsonify({
                "erro": "Produto " + str(item["produto_id"]) + " não encontrado",
                "sucesso": False,
            }), 400
        if produto["estoque"] < item["quantidade"]:
            return jsonify({
                "erro": "Estoque insuficiente para " + produto["nome"],
                "sucesso": False,
            }), 400
        total = total + (produto["preco"] * item["quantidade"])
        preparados.append({
            "produto_id": item["produto_id"],
            "quantidade": item["quantidade"],
            "preco": produto["preco"],
        })

    pedido_id = pedido_model.salvar(usuario_id, total, preparados)
    _notificar_pedido_criado(pedido_id, usuario_id)
    return jsonify({
        "dados": {"pedido_id": pedido_id, "total": total},
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso",
    }), 201


def listar_pedidos_usuario(usuario_id):
    pedidos = pedido_model.listar(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def listar_todos_pedidos():
    pedidos = pedido_model.listar()
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    dados = request.get_json(silent=True) or {}
    novo_status = dados.get("status", "")
    if novo_status not in STATUS_VALIDOS:
        return jsonify({"erro": "Status inválido"}), 400

    pedido_model.atualizar_status(pedido_id, novo_status)
    _notificar_status(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
