from flask import Blueprint

sql_practice_bp = Blueprint('sql_practice', __name__, url_prefix='/sql-practice')

from app.sql_practice import routes
