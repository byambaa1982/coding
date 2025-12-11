# app/catalog/__init__.py
"""Catalog blueprint for course browsing."""

from flask import Blueprint

catalog_bp = Blueprint('catalog', __name__)

from app.catalog import routes
