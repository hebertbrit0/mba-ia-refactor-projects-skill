from models.db import get_db


def buscar_produto(produto_id):
    return get_db().execute(
        "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?",
        (produto_id,),
    ).fetchone()


def buscar_produtos(produto_ids):
    ids = list(dict.fromkeys(produto_ids))
    if not ids:
        return {}
    placeholders = ", ".join("?" for _ in ids)
    rows = get_db().execute(
        f"SELECT id, nome, preco, estoque FROM produtos WHERE id IN ({placeholders})",
        tuple(ids),
    ).fetchall()
    return {row["id"]: row for row in rows}


def salvar(usuario_id, total, itens):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    pedido_id = cursor.lastrowid
    for item in itens:
        db.execute(
            """
            INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
            VALUES (?, ?, ?, ?)
            """,
            (pedido_id, item["produto_id"], item["quantidade"], item["preco"]),
        )
        db.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (item["quantidade"], item["produto_id"]),
        )
    db.commit()
    return pedido_id


def listar(usuario_id=None):
    sql = """
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido i ON i.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = i.produto_id
    """
    parametros = ()
    if usuario_id is not None:
        sql += " WHERE p.usuario_id = ?"
        parametros = (usuario_id,)
    sql += " ORDER BY p.id, i.id"
    rows = get_db().execute(sql, parametros).fetchall()
    return _agrupar(rows)


def _agrupar(rows):
    pedidos = []
    indice = {}
    for row in rows:
        pedido_id = row["id"]
        if pedido_id not in indice:
            pedido = {
                "id": pedido_id,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
            indice[pedido_id] = pedido
            pedidos.append(pedido)
        if row["produto_id"] is not None:
            nome = row["produto_nome"] if row["produto_nome"] else "Desconhecido"
            indice[pedido_id]["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": nome,
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return pedidos


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    db.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id),
    )
    db.commit()
    return True


def resumo_vendas():
    row = get_db().execute(
        """
        SELECT
            COUNT(*) AS total_pedidos,
            COALESCE(SUM(total), 0) AS faturamento,
            COALESCE(SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END), 0) AS pendentes,
            COALESCE(SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END), 0) AS aprovados,
            COALESCE(SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END), 0) AS cancelados
        FROM pedidos
        """
    ).fetchone()
    return {
        "total_pedidos": row["total_pedidos"],
        "faturamento": row["faturamento"] or 0,
        "pendentes": row["pendentes"],
        "aprovados": row["aprovados"],
        "cancelados": row["cancelados"],
    }


def contar():
    return get_db().execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]


def resetar():
    db = get_db()
    db.execute("DELETE FROM itens_pedido")
    db.execute("DELETE FROM pedidos")
    db.execute("DELETE FROM produtos")
    db.execute("DELETE FROM usuarios")
    db.commit()
