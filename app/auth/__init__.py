# app/auth/__init__.py
"""Authentication blueprint."""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from app.auth import routes
