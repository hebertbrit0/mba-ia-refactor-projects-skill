from flask import jsonify, request

from middlewares.auth import current_user
from models import produto_model

MIN_NOME = 2
MAX_NOME = 200
CATEGORIAS_VALIDAS = [
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
]


def _campos_obrigatorios(dados):
    if not dados:
        return "Dados inválidos"
    if "nome" not in dados:
        return "Nome é obrigatório"
    if "preco" not in dados:
        return "Preço é obrigatório"
    if "estoque" not in dados:
        return "Estoque é obrigatório"
    if dados["preco"] < 0:
        return "Preço não pode ser negativo"
    if dados["estoque"] < 0:
        return "Estoque não pode ser negativo"
    return None


def _dados_produto(dados):
    return {
        "nome": dados["nome"],
        "descricao": dados.get("descricao", ""),
        "preco": dados["preco"],
        "estoque": dados["estoque"],
        "categoria": dados.get("categoria", "geral"),
    }


def listar_produtos():
    produtos = produto_model.listar()
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(produto_id):
    produto = produto_model.buscar_por_id(produto_id)
    if produto:
        return jsonify({"dados": produto, "sucesso": True}), 200
    return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404


def criar_produto():
    dados = request.get_json(silent=True)
    erro = _campos_obrigatorios(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    limpo = _dados_produto(dados)
    if len(limpo["nome"]) < MIN_NOME:
        return jsonify({"erro": "Nome muito curto"}), 400
    if len(limpo["nome"]) > MAX_NOME:
        return jsonify({"erro": "Nome muito longo"}), 400
    if limpo["categoria"] not in CATEGORIAS_VALIDAS:
        return jsonify({"erro": "Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS)}), 400

    produto_id = produto_model.criar(
        limpo["nome"],
        limpo["descricao"],
        limpo["preco"],
        limpo["estoque"],
        limpo["categoria"],
    )
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(produto_id):
    existente = produto_model.buscar_por_id(produto_id)
    if not existente:
        return jsonify({"erro": "Produto não encontrado"}), 404

    dados = request.get_json(silent=True)
    erro = _campos_obrigatorios(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    limpo = _dados_produto(dados)
    produto_model.atualizar(
        produto_id,
        limpo["nome"],
        limpo["descricao"],
        limpo["preco"],
        limpo["estoque"],
        limpo["categoria"],
    )
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(produto_id):
    user = current_user()
    if user is None:
        return jsonify({"erro": "Não autenticado", "sucesso": False}), 401
    if user.get("tipo") != "admin":
        return jsonify({"erro": "Acesso negado", "sucesso": False}), 403

    produto = produto_model.buscar_por_id(produto_id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404
    produto_model.deletar(produto_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    preco_min = request.args.get("preco_min")
    preco_max = request.args.get("preco_max")
    if preco_min:
        preco_min = float(preco_min)
    if preco_max:
        preco_max = float(preco_max)

    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
