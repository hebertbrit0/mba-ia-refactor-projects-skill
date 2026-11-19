from flask import jsonify

from config.settings import settings
from models import pedido_model, produto_model, usuario_model
from models.db import get_db


def health_check():
    try:
        get_db().execute("SELECT 1").fetchone()
        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": {
                "produtos": produto_model.contar(),
                "usuarios": usuario_model.contar(),
                "pedidos": pedido_model.contar(),
            },
            "versao": settings.app_version,
            "ambiente": settings.environment,
            "db_path": settings.db_path,
            "debug": settings.debug,
        }), 200
    except Exception:
        return jsonify({"status": "erro", "detalhes": "database unavailable"}), 500
