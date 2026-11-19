from flask import jsonify, request
from sqlalchemy.orm import joinedload

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import (
    DEFAULT_PRIORITY,
    log_action,
    process_task_data,
    utcnow,
)


def _list_item(task):
    data = task.to_dict()
    data["overdue"] = task.is_overdue()
    data["user_name"] = task.user.name if task.user else None
    data["category_name"] = task.category.name if task.category else None
    return data


def list_tasks():
    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
    return jsonify([_list_item(task) for task in tasks]), 200


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    data = task.to_dict()
    data["overdue"] = task.is_overdue()
    return jsonify(data), 200


def _validate_relations(data):
    user_id = data.get("user_id")
    category_id = data.get("category_id")
    if user_id:
        if db.session.get(User, user_id) is None:
            return jsonify({"error": "Usuário não encontrado"}), 404
    if category_id:
        if db.session.get(Category, category_id) is None:
            return jsonify({"error": "Categoria não encontrada"}), 404
    return None


def create_task():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400
    if not data.get("title"):
        return jsonify({"error": "Título é obrigatório"}), 400

    payload = {
        "title": data.get("title"),
        "description": data.get("description", ""),
        "status": data.get("status", "pending"),
        "priority": data.get("priority", DEFAULT_PRIORITY),
    }
    if "due_date" in data:
        payload["due_date"] = data.get("due_date")
    if "tags" in data:
        payload["tags"] = data.get("tags")

    cleaned, error = process_task_data(payload)
    if error:
        return jsonify({"error": error}), 400

    relation_error = _validate_relations(data)
    if relation_error:
        return relation_error

    task = Task()
    task.title = cleaned["title"]
    task.description = cleaned.get("description", "")
    task.status = cleaned.get("status", "pending")
    task.priority = cleaned.get("priority", DEFAULT_PRIORITY)
    task.user_id = data.get("user_id")
    task.category_id = data.get("category_id")
    if "due_date" in cleaned:
        task.due_date = cleaned["due_date"]
    if "tags" in cleaned:
        task.tags = cleaned["tags"]

    db.session.add(task)
    db.session.commit()
    log_action("task_created", f"{task.id} - {task.title}")
    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    fields = {
        key: data[key]
        for key in ("title", "description", "status", "priority", "due_date", "tags")
        if key in data
    }
    if fields:
        cleaned, error = process_task_data(fields)
        if error:
            return jsonify({"error": error}), 400
        for key, value in cleaned.items():
            setattr(task, key, value)

    if "user_id" in data:
        if data["user_id"] and db.session.get(User, data["user_id"]) is None:
            return jsonify({"error": "Usuário não encontrado"}), 404
        task.user_id = data["user_id"]

    if "category_id" in data:
        if data["category_id"] and db.session.get(Category, data["category_id"]) is None:
            return jsonify({"error": "Categoria não encontrada"}), 404
        task.category_id = data["category_id"]

    task.updated_at = utcnow()
    db.session.commit()
    log_action("task_updated", str(task.id))
    return jsonify(task.to_dict()), 200


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    db.session.delete(task)
    db.session.commit()
    log_action("task_deleted", str(task_id))
    return jsonify({"message": "Task deletada com sucesso"}), 200


def search_tasks():
    query = request.args.get("q", "")
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    user_id = request.args.get("user_id", "")

    tasks = Task.query
    if query:
        tasks = tasks.filter(
            db.or_(
                Task.title.like(f"%{query}%"),
                Task.description.like(f"%{query}%"),
            )
        )
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        tasks = tasks.filter(Task.priority == int(priority))
    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))

    return jsonify([task.to_dict() for task in tasks.all()]), 200


def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status="pending").count()
    in_progress = Task.query.filter_by(status="in_progress").count()
    done = Task.query.filter_by(status="done").count()
    cancelled = Task.query.filter_by(status="cancelled").count()
    overdue_count = sum(1 for task in Task.query.all() if task.is_overdue())
    stats = {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "done": done,
        "cancelled": cancelled,
        "overdue": overdue_count,
        "completion_rate": round((done / total) * 100, 2) if total > 0 else 0,
    }
    return jsonify(stats), 200
