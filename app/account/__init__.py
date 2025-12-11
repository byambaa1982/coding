# app/account/__init__.py
"""Account blueprint for user dashboard and profile."""

from flask import Blueprint

account_bp = Blueprint('account', __name__, url_prefix='/account')

from app.account import routes
