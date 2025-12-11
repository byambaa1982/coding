# app/payment/__init__.py
"""Payment blueprint for Stripe integration and order management."""

from flask import Blueprint

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

from app.payment import routes
