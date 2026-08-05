import logging
from datetime import datetime

from sqlalchemy.orm import joinedload

from config.settings import Settings
from database import db
from models.category import Category
from models.task import Task
from models.user import User
from services.notification_service import NotificationService
from utils.helpers import utc_now

logger = logging.getLogger(__name__)

notification_service = NotificationService(
    host=Settings.SMTP_HOST,
    port=Settings.SMTP_PORT,
    user=Settings.SMTP_USER,
    password=Settings.SMTP_PASSWORD,
    enabled=Settings.NOTIFICATIONS_ENABLED,
)


def _serialize_task(task):
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return data


def list_tasks():
    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
    result = []
    for task in tasks:
        data = _serialize_task(task)
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
        result.append(data)
    return result, 200


def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    return _serialize_task(task), 200


def create_task(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    title = data.get('title')
    if not title:
        return {'error': 'Título é obrigatório'}, 400

    if len(title) < 3:
        return {'error': 'Título muito curto'}, 400

    if len(title) > 200:
        return {'error': 'Título muito longo'}, 400

    status = data.get('status', 'pending')
    priority = data.get('priority', 3)
    user_id = data.get('user_id')
    category_id = data.get('category_id')
    due_date = data.get('due_date')
    tags = data.get('tags')

    if not Task.validate_status(status):
        return {'error': 'Status inválido'}, 400

    if not Task.validate_priority(priority):
        return {'error': 'Prioridade deve ser entre 1 e 5'}, 400

    user = None
    if user_id:
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Usuário não encontrado'}, 404

    if category_id:
        cat = Category.query.get(category_id)
        if not cat:
            return {'error': 'Categoria não encontrada'}, 404

    task = Task()
    task.title = title
    task.description = data.get('description', '')
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            return {'error': 'Formato de data inválido. Use YYYY-MM-DD'}, 400

    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    try:
        db.session.add(task)
        db.session.commit()
        logger.info("Task criada: %s - %s", task.id, task.title)
    except Exception:
        db.session.rollback()
        logger.exception("Erro ao criar task")
        return {'error': 'Erro ao criar task'}, 500

    if user:
        notification_service.notify_task_assigned(user, task)

    return task.to_dict(), 201


def update_task(task_id, data):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404

    if not data:
        return {'error': 'Dados inválidos'}, 400

    if 'title' in data:
        if len(data['title']) < 3:
            return {'error': 'Título muito curto'}, 400
        if len(data['title']) > 200:
            return {'error': 'Título muito longo'}, 400
        task.title = data['title']

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if not Task.validate_status(data['status']):
            return {'error': 'Status inválido'}, 400
        task.status = data['status']

    if 'priority' in data:
        if not Task.validate_priority(data['priority']):
            return {'error': 'Prioridade deve ser entre 1 e 5'}, 400
        task.priority = data['priority']

    newly_assigned_user = None
    if 'user_id' in data:
        if data['user_id']:
            user = User.query.get(data['user_id'])
            if not user:
                return {'error': 'Usuário não encontrado'}, 404
            if data['user_id'] != task.user_id:
                newly_assigned_user = user
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id']:
            cat = Category.query.get(data['category_id'])
            if not cat:
                return {'error': 'Categoria não encontrada'}, 404
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
            except ValueError:
                return {'error': 'Formato de data inválido'}, 400
        else:
            task.due_date = None

    if 'tags' in data:
        task.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']

    task.updated_at = utc_now()

    try:
        db.session.commit()
        logger.info("Task atualizada: %s", task.id)
    except Exception:
        db.session.rollback()
        logger.exception("Erro ao atualizar task")
        return {'error': 'Erro ao atualizar'}, 500

    if newly_assigned_user:
        notification_service.notify_task_assigned(newly_assigned_user, task)

    return task.to_dict(), 200


def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404

    try:
        db.session.delete(task)
        db.session.commit()
        logger.info("Task deletada: %s", task_id)
    except Exception:
        db.session.rollback()
        logger.exception("Erro ao deletar task")
        return {'error': 'Erro ao deletar'}, 500

    return {'message': 'Task deletada com sucesso'}, 200


def search_tasks(query, status, priority, user_id):
    tasks = Task.query

    if query:
        tasks = tasks.filter(
            db.or_(
                Task.title.like(f'%{query}%'),
                Task.description.like(f'%{query}%')
            )
        )

    if status:
        tasks = tasks.filter(Task.status == status)

    if priority:
        tasks = tasks.filter(Task.priority == int(priority))

    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))

    return [t.to_dict() for t in tasks.all()], 200


def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    overdue_count = sum(1 for t in Task.query.all() if t.is_overdue())

    stats = {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
    }

    return stats, 200
