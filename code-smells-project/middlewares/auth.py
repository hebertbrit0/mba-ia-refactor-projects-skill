import secrets

from flask import request

from models import usuario_model

_tokens = {}


def issue_token(user_id):
    token = secrets.token_urlsafe(32)
    _tokens[token] = user_id
    return token


def current_user():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header[7:].strip()
    user_id = _tokens.get(token)
    if user_id is None:
        return None
    return usuario_model.buscar_por_id(user_id)
