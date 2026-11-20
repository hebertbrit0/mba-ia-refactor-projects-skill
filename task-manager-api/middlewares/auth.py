import secrets

from flask import jsonify, request

from database import db
from models.user import User

_tokens = {}


def issue_token(user_id):
    token = secrets.token_urlsafe(32)
    _tokens[token] = user_id
    return token


def revoke_user(user_id):
    for token, owner_id in list(_tokens.items()):
        if owner_id == user_id:
            del _tokens[token]


def _bearer_token():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header[7:].strip()
    return token or None


def current_user():
    token = _bearer_token()
    if token is None:
        return None
    user_id = _tokens.get(token)
    if user_id is None:
        return None
    user = db.session.get(User, user_id)
    if user is None or not user.active:
        return None
    return user


def require_user():
    user = current_user()
    if user is None:
        return None, (jsonify({"error": "Não autenticado"}), 401)
    return user, None
