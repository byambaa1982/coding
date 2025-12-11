# celeryconfig.py
"""Celery configuration for background tasks."""

import os
from datetime import timedelta

# Broker settings (Redis)
broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Task settings
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True

# Task execution settings
task_acks_late = True
worker_prefetch_multiplier = 1
task_time_limit = 60  # 60 seconds hard limit
task_soft_time_limit = 50  # 50 seconds soft limit

# Result backend settings
result_expires = 3600  # Results expire after 1 hour

# Worker settings
worker_max_tasks_per_child = 100  # Restart worker after 100 tasks
worker_disable_rate_limits = False

# Task routes
task_routes = {
    'app.tasks.execution_tasks.*': {'queue': 'code_execution'},
    'app.tasks.email_tasks.*': {'queue': 'email'},
    'app.tasks.analytics_tasks.*': {'queue': 'analytics'},
}

# Beat schedule (periodic tasks)
beat_schedule = {
    'cleanup-old-submissions': {
        'task': 'app.tasks.analytics_tasks.cleanup_old_submissions',
        'schedule': timedelta(hours=24),
    },
    'update-user-statistics': {
        'task': 'app.tasks.analytics_tasks.update_user_statistics',
        'schedule': timedelta(hours=6),
    },
}
