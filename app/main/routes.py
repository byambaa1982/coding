# app/main/routes.py
"""Main routes."""

from flask import render_template
from flask_login import current_user
from app.main import main_bp


@main_bp.route('/')
def index():
    """Homepage."""
    return render_template('index.html')


@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')
