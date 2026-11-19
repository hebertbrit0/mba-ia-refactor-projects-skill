from models.db import get_db


def _para_dict(row):
    if row is None:
        return None
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def listar():
    rows = get_db().execute("SELECT * FROM produtos").fetchall()
    return [_para_dict(row) for row in rows]


def buscar_por_id(produto_id):
    row = get_db().execute(
        "SELECT * FROM produtos WHERE id = ?",
        (produto_id,),
    ).fetchone()
    return _para_dict(row)


def criar(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO produtos (nome, descricao, preco, estoque, categoria)
        VALUES (?, ?, ?, ?, ?)
        """,
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    db.execute(
        """
        UPDATE produtos
        SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ?
        WHERE id = ?
        """,
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    db.commit()
    return True


def deletar(produto_id):
    db = get_db()
    db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()
    return True


def buscar(termo, categoria=None, preco_min=None, preco_max=None):
    clausulas = ["1=1"]
    parametros = []
    if termo:
        clausulas.append("(nome LIKE ? OR descricao LIKE ?)")
        like = f"%{termo}%"
        parametros.extend([like, like])
    if categoria:
        clausulas.append("categoria = ?")
        parametros.append(categoria)
    if preco_min is not None:
        clausulas.append("preco >= ?")
        parametros.append(preco_min)
    if preco_max is not None:
        clausulas.append("preco <= ?")
        parametros.append(preco_max)
    query = "SELECT * FROM produtos WHERE " + " AND ".join(clausulas)
    rows = get_db().execute(query, parametros).fetchall()
    return [_para_dict(row) for row in rows]


def contar():
    return get_db().execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
