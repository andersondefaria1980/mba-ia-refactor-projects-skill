import logging

from sqlalchemy.orm import joinedload

from database import db
from models.task import Task
from models.user import User
from models.category import Category
from services.notification_service import NotificationService
from utils.helpers import calculate_percentage, parse_date

logger = logging.getLogger(__name__)


def list_tasks():
    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()

    result = []
    for t in tasks:
        task_data = t.to_dict()
        task_data['user_name'] = t.user.name if t.user else None
        task_data['category_name'] = t.category.name if t.category else None
        result.append(task_data)

    return result, 200


def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404

    return task.to_dict(), 200


def create_task(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    title = data.get('title')
    if not title:
        return {'error': 'Título é obrigatório'}, 400
    if len(title) < Task.MIN_TITLE_LENGTH:
        return {'error': 'Título muito curto'}, 400
    if len(title) > Task.MAX_TITLE_LENGTH:
        return {'error': 'Título muito longo'}, 400

    description = data.get('description', '')
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
    task.description = description
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    if due_date:
        parsed = parse_date(due_date)
        if not parsed:
            return {'error': 'Formato de data inválido. Use YYYY-MM-DD'}, 400
        task.due_date = parsed

    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    db.session.add(task)
    db.session.commit()
    logger.info("Task criada: %s - %s", task.id, task.title)

    if user:
        NotificationService().notify_task_assigned(user, task)

    return task.to_dict(), 201


def update_task(task_id, data):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404

    if not data:
        return {'error': 'Dados inválidos'}, 400

    if 'title' in data:
        if len(data['title']) < Task.MIN_TITLE_LENGTH:
            return {'error': 'Título muito curto'}, 400
        if len(data['title']) > Task.MAX_TITLE_LENGTH:
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

    assigned_user = None
    if 'user_id' in data:
        if data['user_id']:
            assigned_user = User.query.get(data['user_id'])
            if not assigned_user:
                return {'error': 'Usuário não encontrado'}, 404
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id']:
            cat = Category.query.get(data['category_id'])
            if not cat:
                return {'error': 'Categoria não encontrada'}, 404
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            parsed = parse_date(data['due_date'])
            if not parsed:
                return {'error': 'Formato de data inválido'}, 400
            task.due_date = parsed
        else:
            task.due_date = None

    if 'tags' in data:
        task.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']

    db.session.commit()
    logger.info("Task atualizada: %s", task.id)

    if assigned_user:
        NotificationService().notify_task_assigned(assigned_user, task)

    return task.to_dict(), 200


def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404

    db.session.delete(task)
    db.session.commit()
    logger.info("Task deletada: %s", task_id)

    return {'message': 'Task deletada com sucesso'}, 200


def search_tasks(args):
    tasks = Task.search(
        query=args.get('q', ''),
        status=args.get('status', ''),
        priority=args.get('priority', ''),
        user_id=args.get('user_id', ''),
    )
    return [t.to_dict() for t in tasks], 200


def get_stats():
    stats = Task.stats()
    stats['completion_rate'] = calculate_percentage(stats['done'], stats['total'])
    return stats, 200
