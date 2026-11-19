import re
import secrets

from flask import jsonify, request
from sqlalchemy import func

from database import db
from models.task import Task
from models.user import User
from utils.helpers import MIN_PASSWORD_LENGTH, VALID_ROLES, log_action


_EMAIL = re.compile(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")


def _user_task(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "created_at": str(task.created_at),
        "due_date": str(task.due_date) if task.due_date else None,
        "overdue": task.is_overdue(),
    }


def list_users():
    rows = (
        db.session.query(User, func.count(Task.id))
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id)
        .all()
    )
    result = []
    for user, task_count in rows:
        data = user.to_dict()
        data["task_count"] = task_count
        result.append(data)
    return jsonify(result), 200


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    data = user.to_dict()
    tasks = Task.query.filter_by(user_id=user_id).all()
    data["tasks"] = [task.to_dict() for task in tasks]
    return jsonify(data), 200


def create_user():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not name:
        return jsonify({"error": "Nome é obrigatório"}), 400
    if not email:
        return jsonify({"error": "Email é obrigatório"}), 400
    if not password:
        return jsonify({"error": "Senha é obrigatória"}), 400
    if _EMAIL.match(email) is None:
        return jsonify({"error": "Email inválido"}), 400
    if len(password) < MIN_PASSWORD_LENGTH:
        return jsonify({"error": "Senha deve ter no mínimo 4 caracteres"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email já cadastrado"}), 409
    if role not in VALID_ROLES:
        return jsonify({"error": "Role inválido"}), 400

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role
    db.session.add(user)
    db.session.commit()
    log_action("user_created", f"{user.id} - {user.name}")
    return jsonify(user.to_dict()), 201


def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    if "name" in data:
        user.name = data["name"]

    if "email" in data:
        if _EMAIL.match(data["email"]) is None:
            return jsonify({"error": "Email inválido"}), 400
        existing = User.query.filter_by(email=data["email"]).first()
        if existing and existing.id != user_id:
            return jsonify({"error": "Email já cadastrado"}), 409
        user.email = data["email"]

    if "password" in data:
        if len(data["password"]) < MIN_PASSWORD_LENGTH:
            return jsonify({"error": "Senha muito curta"}), 400
        user.set_password(data["password"])

    if "role" in data:
        if data["role"] not in VALID_ROLES:
            return jsonify({"error": "Role inválido"}), 400
        user.role = data["role"]

    if "active" in data:
        user.active = data["active"]

    db.session.commit()
    return jsonify(user.to_dict()), 200


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    Task.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    log_action("user_deleted", str(user_id))
    return jsonify({"message": "Usuário deletado com sucesso"}), 200


def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([_user_task(task) for task in tasks]), 200


def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Credenciais inválidas"}), 401
    if not user.active:
        return jsonify({"error": "Usuário inativo"}), 403

    return jsonify({
        "message": "Login realizado com sucesso",
        "user": user.to_dict(),
        "token": secrets.token_urlsafe(32),
    }), 200
