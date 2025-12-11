# app/python_practice/__init__.py
"""Python practice blueprint for interactive code exercises."""

from flask import Blueprint

python_practice_bp = Blueprint('python_practice', __name__, url_prefix='/python-practice')

from app.python_practice import routes
