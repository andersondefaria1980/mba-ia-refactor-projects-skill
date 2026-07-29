from flask import abort, jsonify, request

from database import db
from middlewares.auth import gerar_token
from models.task import Task
from models.user import User
from utils.helpers import MIN_PASSWORD_LENGTH, VALID_ROLES, validate_email


def get_users():
    users = User.query.all()
    result = []
    for u in users:
        user_data = u.to_dict()
        user_data['task_count'] = len(u.tasks)
        result.append(user_data)
    return jsonify(result), 200


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404, description='Usuário não encontrado')

    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
    return jsonify(data), 200


def create_user():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description='Dados inválidos')

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        abort(400, description='Nome é obrigatório')
    if not email:
        abort(400, description='Email é obrigatório')
    if not password:
        abort(400, description='Senha é obrigatória')
    if not validate_email(email):
        abort(400, description='Email inválido')
    if len(password) < MIN_PASSWORD_LENGTH:
        abort(400, description=f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres')
    if User.query.filter_by(email=email).first():
        abort(409, description='Email já cadastrado')
    if role not in VALID_ROLES:
        abort(400, description='Role inválido')

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    try:
        db.session.add(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify(user.to_dict()), 201


def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404, description='Usuário não encontrado')

    data = request.get_json(silent=True)
    if not data:
        abort(400, description='Dados inválidos')

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        if not validate_email(data['email']):
            abort(400, description='Email inválido')
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            abort(409, description='Email já cadastrado')
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            abort(400, description='Senha muito curta')
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            abort(400, description='Role inválido')
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify(user.to_dict()), 200


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404, description='Usuário não encontrado')

    try:
        for t in Task.query.filter_by(user_id=user_id).all():
            db.session.delete(t)
        db.session.delete(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404, description='Usuário não encontrado')

    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([t.to_dict() for t in tasks]), 200


def login():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description='Dados inválidos')

    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        abort(400, description='Email e senha são obrigatórios')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Credenciais inválidas'}), 401
    if not user.active:
        return jsonify({'error': 'Usuário inativo'}), 403

    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': gerar_token(user),
    }), 200
