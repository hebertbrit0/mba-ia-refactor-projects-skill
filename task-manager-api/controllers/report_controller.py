from datetime import timedelta

from flask import jsonify, request
from sqlalchemy import func

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import DEFAULT_COLOR, calculate_percentage, utcnow


def summary_report():
    now = utcnow()
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status="pending").count()
    in_progress = Task.query.filter_by(status="in_progress").count()
    done = Task.query.filter_by(status="done").count()
    cancelled = Task.query.filter_by(status="cancelled").count()

    priorities = {
        priority: Task.query.filter_by(priority=priority).count()
        for priority in range(1, 6)
    }

    overdue_count = 0
    overdue_list = []
    for task in Task.query.all():
        if not task.is_overdue():
            continue
        overdue_count += 1
        overdue_list.append({
            "id": task.id,
            "title": task.title,
            "due_date": str(task.due_date),
            "days_overdue": (now - task.due_date).days,
        })

    seven_days_ago = now - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == "done",
        Task.updated_at >= seven_days_ago,
    ).count()

    productivity = (
        db.session.query(User.id, User.name, func.count(Task.id))
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id, User.name)
        .all()
    )
    done_by_user = dict(
        db.session.query(Task.user_id, func.count(Task.id))
        .filter(Task.status == "done")
        .group_by(Task.user_id)
        .all()
    )
    user_stats = []
    for user_id, user_name, total in productivity:
        completed = done_by_user.get(user_id, 0)
        user_stats.append({
            "user_id": user_id,
            "user_name": user_name,
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": calculate_percentage(completed, total),
        })

    report = {
        "generated_at": str(now),
        "overview": {
            "total_tasks": total_tasks,
            "total_users": total_users,
            "total_categories": total_categories,
        },
        "tasks_by_status": {
            "pending": pending,
            "in_progress": in_progress,
            "done": done,
            "cancelled": cancelled,
        },
        "tasks_by_priority": {
            "critical": priorities[1],
            "high": priorities[2],
            "medium": priorities[3],
            "low": priorities[4],
            "minimal": priorities[5],
        },
        "overdue": {
            "count": overdue_count,
            "tasks": overdue_list,
        },
        "recent_activity": {
            "tasks_created_last_7_days": recent_tasks,
            "tasks_completed_last_7_days": recent_done,
        },
        "user_productivity": user_stats,
    }
    return jsonify(report), 200


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    done = pending = in_progress = cancelled = overdue = high_priority = 0
    for task in tasks:
        if task.status == "done":
            done += 1
        elif task.status == "pending":
            pending += 1
        elif task.status == "in_progress":
            in_progress += 1
        elif task.status == "cancelled":
            cancelled += 1
        if task.priority <= 2:
            high_priority += 1
        if task.is_overdue():
            overdue += 1

    total = len(tasks)
    report = {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
        "statistics": {
            "total_tasks": total,
            "done": done,
            "pending": pending,
            "in_progress": in_progress,
            "cancelled": cancelled,
            "overdue": overdue,
            "high_priority": high_priority,
            "completion_rate": calculate_percentage(done, total),
        },
    }
    return jsonify(report), 200


def list_categories():
    counts = dict(
        db.session.query(Task.category_id, func.count(Task.id))
        .group_by(Task.category_id)
        .all()
    )
    result = []
    for category in Category.query.all():
        data = category.to_dict()
        data["task_count"] = counts.get(category.id, 0)
        result.append(data)
    return jsonify(result), 200


def create_category():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400
    name = data.get("name")
    if not name:
        return jsonify({"error": "Nome é obrigatório"}), 400

    category = Category()
    category.name = name
    category.description = data.get("description", "")
    category.color = data.get("color", DEFAULT_COLOR)
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201


def update_category(cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        return jsonify({"error": "Categoria não encontrada"}), 404

    data = request.get_json(silent=True) or {}
    if "name" in data:
        category.name = data["name"]
    if "description" in data:
        category.description = data["description"]
    if "color" in data:
        category.color = data["color"]
    db.session.commit()
    return jsonify(category.to_dict()), 200


def delete_category(cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        return jsonify({"error": "Categoria não encontrada"}), 404
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Categoria deletada"}), 200
