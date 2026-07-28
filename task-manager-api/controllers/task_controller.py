from flask import abort, jsonify, request
from sqlalchemy.orm import joinedload

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from services.notification_service import NotificationService
from utils.helpers import DEFAULT_PRIORITY, process_task_data

notification_service = NotificationService()


def get_tasks():
    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
    result = []
    for t in tasks:
        data = t.to_dict()
        data['user_name'] = t.user.name if t.user else None
        data['category_name'] = t.category.name if t.category else None
        result.append(data)
    return jsonify(result), 200


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        abort(404, description='Task não encontrada')
    return jsonify(task.to_dict()), 200


def create_task():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description='Dados inválidos')
    if not data.get('title'):
        abort(400, description='Título é obrigatório')

    validated, error = process_task_data(data)
    if error:
        abort(400, description=error)

    user_id = data.get('user_id')
    category_id = data.get('category_id')
    if user_id and not db.session.get(User, user_id):
        abort(404, description='Usuário não encontrado')
    if category_id and not db.session.get(Category, category_id):
        abort(404, description='Categoria não encontrada')

    task = Task()
    task.title = validated['title']
    task.description = validated.get('description', data.get('description', ''))
    task.status = validated.get('status', 'pending')
    task.priority = validated.get('priority', DEFAULT_PRIORITY)
    task.user_id = user_id
    task.category_id = category_id
    if 'due_date' in validated:
        task.due_date = validated['due_date']
    if 'tags' in validated:
        task.tags = validated['tags']

    try:
        db.session.add(task)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    if task.user_id:
        user = db.session.get(User, task.user_id)
        notification_service.notify_task_assigned(user, task)

    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        abort(404, description='Task não encontrada')

    data = request.get_json(silent=True)
    if not data:
        abort(400, description='Dados inválidos')

    validated, error = process_task_data(data)
    if error:
        abort(400, description=error)

    if 'user_id' in data:
        if data['user_id'] and not db.session.get(User, data['user_id']):
            abort(404, description='Usuário não encontrado')
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not db.session.get(Category, data['category_id']):
            abort(404, description='Categoria não encontrada')
        task.category_id = data['category_id']

    for field in ('title', 'description', 'status', 'priority'):
        if field in validated:
            setattr(task, field, validated[field])
    if 'due_date' in validated:
        task.due_date = validated['due_date']
    if 'tags' in validated:
        task.tags = validated['tags']

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify(task.to_dict()), 200


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        abort(404, description='Task não encontrada')

    try:
        db.session.delete(task)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    query = request.args.get('q', '')
    status = request.args.get('status', '')
    priority = request.args.get('priority', type=int)
    user_id = request.args.get('user_id', type=int)

    tasks = Task.query
    if query:
        tasks = tasks.filter(
            db.or_(Task.title.like(f'%{query}%'), Task.description.like(f'%{query}%'))
        )
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority is not None:
        tasks = tasks.filter(Task.priority == priority)
    if user_id is not None:
        tasks = tasks.filter(Task.user_id == user_id)

    return jsonify([t.to_dict() for t in tasks.all()]), 200


def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()
    overdue_count = sum(1 for t in Task.query.all() if t.is_overdue())

    return jsonify({
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }), 200
