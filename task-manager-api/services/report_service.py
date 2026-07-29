from datetime import datetime, timedelta, timezone

from models.category import Category
from models.task import Task
from models.user import User


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def build_summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    priority_counts = {
        p: Task.query.filter_by(priority=p).count() for p in (1, 2, 3, 4, 5)
    }

    # Uma única query para todas as tasks, agrupada em memória — elimina o N+1
    # de "uma query de tasks por usuário" que existia na versão anterior.
    all_tasks = Task.query.all()

    overdue_list = [
        {
            'id': t.id,
            'title': t.title,
            'due_date': str(t.due_date),
            'days_overdue': (_now() - t.due_date).days,
        }
        for t in all_tasks
        if t.is_overdue()
    ]

    seven_days_ago = _now() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == 'done', Task.updated_at >= seven_days_ago
    ).count()

    tasks_by_user = {}
    for t in all_tasks:
        tasks_by_user.setdefault(t.user_id, []).append(t)

    user_stats = []
    for u in User.query.all():
        user_tasks = tasks_by_user.get(u.id, [])
        total = len(user_tasks)
        completed = sum(1 for t in user_tasks if t.status == 'done')
        user_stats.append({
            'user_id': u.id,
            'user_name': u.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0,
        })

    return {
        'generated_at': str(_now()),
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
            'critical': priority_counts[1],
            'high': priority_counts[2],
            'medium': priority_counts[3],
            'low': priority_counts[4],
            'minimal': priority_counts[5],
        },
        'overdue': {
            'count': len(overdue_list),
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }


def build_user_report(user):
    tasks = Task.query.filter_by(user_id=user.id).all()

    total = len(tasks)
    done = sum(1 for t in tasks if t.status == 'done')
    pending = sum(1 for t in tasks if t.status == 'pending')
    in_progress = sum(1 for t in tasks if t.status == 'in_progress')
    cancelled = sum(1 for t in tasks if t.status == 'cancelled')
    high_priority = sum(1 for t in tasks if t.priority <= 2)
    overdue = sum(1 for t in tasks if t.is_overdue())

    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': pending,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
        },
    }
