# app/tasks/__init__.py
"""Celery tasks package."""

from app.tasks.execution_tasks import execute_python_code_async
from app.tasks.email_tasks import send_email_async
from app.tasks.analytics_tasks import update_user_statistics, cleanup_old_submissions

__all__ = [
    'execute_python_code_async',
    'send_email_async',
    'update_user_statistics',
    'cleanup_old_submissions'
]
