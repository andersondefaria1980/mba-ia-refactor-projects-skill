from datetime import datetime, timedelta, timezone

import jwt
from werkzeug.security import check_password_hash, generate_password_hash

from config.settings import Settings
from database import db
from utils.helpers import VALID_ROLES, utc_now


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at)
        }

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

    def is_admin(self):
        return self.role == 'admin'

    @staticmethod
    def validate_role(role):
        return role in VALID_ROLES

    def generate_token(self):
        payload = {
            'user_id': self.id,
            'exp': datetime.now(timezone.utc) + timedelta(seconds=Settings.TOKEN_TTL_SECONDS),
        }
        return jwt.encode(payload, Settings.SECRET_KEY, algorithm='HS256')
