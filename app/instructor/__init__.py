"""Instructor panel blueprint."""
from flask import Blueprint

instructor_bp = Blueprint('instructor', __name__, url_prefix='/instructor')

from app.instructor import routes
