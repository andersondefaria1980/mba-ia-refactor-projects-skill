from flask import abort, jsonify, request

from database import db
from models.category import Category
from models.task import Task


def get_categories():
    result = []
    for c in Category.query.all():
        cat_data = c.to_dict()
        cat_data['task_count'] = Task.query.filter_by(category_id=c.id).count()
        result.append(cat_data)
    return jsonify(result), 200


def create_category():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description='Dados inválidos')

    name = data.get('name')
    if not name:
        abort(400, description='Nome é obrigatório')

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', '#000000')

    try:
        db.session.add(category)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify(category.to_dict()), 201


def update_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        abort(404, description='Categoria não encontrada')

    data = request.get_json(silent=True)
    if not data:
        abort(400, description='Dados inválidos')

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
        raise

    return jsonify(cat.to_dict()), 200


def delete_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        abort(404, description='Categoria não encontrada')

    try:
        db.session.delete(cat)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({'message': 'Categoria deletada'}), 200
