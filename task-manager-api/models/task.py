from database import db
from utils.helpers import utcnow, VALID_STATUSES


class Task(db.Model):
    __tablename__ = 'tasks'

    MIN_PRIORITY = 1
    MAX_PRIORITY = 5
    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 200

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')
    priority = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
            'overdue': self.is_overdue(),
        }

    @staticmethod
    def validate_status(new_status):
        return new_status in VALID_STATUSES

    @staticmethod
    def validate_priority(priority):
        return Task.MIN_PRIORITY <= priority <= Task.MAX_PRIORITY

    def is_overdue(self):
        if not self.due_date:
            return False
        if self.due_date >= utcnow():
            return False
        return self.status not in ('done', 'cancelled')

    @classmethod
    def search(cls, query=None, status=None, priority=None, user_id=None):
        tasks = cls.query

        if query:
            tasks = tasks.filter(
                db.or_(
                    cls.title.like(f'%{query}%'),
                    cls.description.like(f'%{query}%'),
                )
            )
        if status:
            tasks = tasks.filter(cls.status == status)
        if priority:
            tasks = tasks.filter(cls.priority == int(priority))
        if user_id:
            tasks = tasks.filter(cls.user_id == int(user_id))

        return tasks.all()

    @classmethod
    def stats(cls):
        total = cls.query.count()
        done = cls.query.filter_by(status='done').count()
        overdue = sum(1 for t in cls.query.all() if t.is_overdue())

        return {
            'total': total,
            'pending': cls.query.filter_by(status='pending').count(),
            'in_progress': cls.query.filter_by(status='in_progress').count(),
            'done': done,
            'cancelled': cls.query.filter_by(status='cancelled').count(),
            'overdue': overdue,
        }
