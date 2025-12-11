# app/learning/__init__.py
"""Learning blueprint for lesson viewing and progress tracking."""

from flask import Blueprint

learning_bp = Blueprint('learning', __name__, url_prefix='/learn')

from app.learning import routes
