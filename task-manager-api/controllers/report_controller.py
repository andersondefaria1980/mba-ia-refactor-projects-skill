import logging
from collections import defaultdict
from datetime import timedelta

from sqlalchemy import func

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import utc_now

logger = logging.getLogger(__name__)


def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    p1 = Task.query.filter_by(priority=1).count()
    p2 = Task.query.filter_by(priority=2).count()
    p3 = Task.query.filter_by(priority=3).count()
    p4 = Task.query.filter_by(priority=4).count()
    p5 = Task.query.filter_by(priority=5).count()

    all_tasks = Task.query.all()

    overdue_count = 0
    overdue_list = []
    tasks_by_user = defaultdict(list)
    for t in all_tasks:
        if t.is_overdue():
            overdue_count += 1
            overdue_list.append({
                'id': t.id,
                'title': t.title,
                'due_date': str(t.due_date),
                'days_overdue': (utc_now() - t.due_date).days
            })
        if t.user_id:
            tasks_by_user[t.user_id].append(t)

    seven_days_ago = utc_now() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()

    recent_done = Task.query.filter(
        Task.status == 'done',
        Task.updated_at >= seven_days_ago
    ).count()

    users = User.query.all()
    user_stats = []
    for u in users:
        user_tasks = tasks_by_user.get(u.id, [])
        total = len(user_tasks)
        completed = sum(1 for t in user_tasks if t.status == 'done')
        user_stats.append({
            'user_id': u.id,
            'user_name': u.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0
        })

    report = {
        'generated_at': str(utc_now()),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
        },
        'tasks_by_priority': {
            'critical': p1,
            'high': p2,
            'medium': p3,
            'low': p4,
            'minimal': p5,
        },
        'overdue': {
            'count': overdue_count,
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }

    return report, 200


def user_report(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    tasks = Task.query.filter_by(user_id=user_id).all()

    total = len(tasks)
    done = 0
    pending = 0
    in_progress = 0
    cancelled = 0
    overdue = 0
    high_priority = 0

    for t in tasks:
        if t.status == 'done':
            done += 1
        elif t.status == 'pending':
            pending += 1
        elif t.status == 'in_progress':
            in_progress += 1
        elif t.status == 'cancelled':
            cancelled += 1

        if t.priority <= 2:
            high_priority += 1

        if t.is_overdue():
            overdue += 1

    report = {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': pending,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
        }
    }

    return report, 200


def list_categories():
    categories = Category.query.all()
    counts = dict(
        db.session.query(Task.category_id, func.count(Task.id))
        .group_by(Task.category_id)
        .all()
    )
    result = []
    for c in categories:
        cat_data = c.to_dict()
        cat_data['task_count'] = counts.get(c.id, 0)
        result.append(cat_data)
    return result, 200


def create_category(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    name = data.get('name')
    if not name:
        return {'error': 'Nome é obrigatório'}, 400

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', '#000000')

    try:
        db.session.add(category)
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("Erro ao criar categoria")
        return {'error': 'Erro ao criar categoria'}, 500

    return category.to_dict(), 201


def update_category(cat_id, data):
    cat = Category.query.get(cat_id)
    if not cat:
        return {'error': 'Categoria não encontrada'}, 404

    if not data:
        return {'error': 'Dados inválidos'}, 400

    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("Erro ao atualizar categoria")
        return {'error': 'Erro ao atualizar'}, 500

    return cat.to_dict(), 200


def delete_category(cat_id):
    cat = Category.query.get(cat_id)
    if not cat:
        return {'error': 'Categoria não encontrada'}, 404

    try:
        db.session.delete(cat)
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("Erro ao deletar categoria")
        return {'error': 'Erro ao deletar'}, 500

    return {'message': 'Categoria deletada'}, 200
