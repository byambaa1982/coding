# app/celery_app.py
"""Celery application initialization."""

from celery import Celery
import os


def make_celery(app=None):
    """Create Celery instance."""
    celery = Celery(
        'tutorial_platform',
        broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        include=[
            'app.tasks.execution_tasks',
            'app.tasks.email_tasks',
            'app.tasks.analytics_tasks'
        ]
    )
    
    # Load celeryconfig
    celery.config_from_object('celeryconfig')
    
    if app:
        # Update celery config from Flask config
        celery.conf.update(app.config)
        
        class ContextTask(celery.Task):
            """Make celery tasks work with Flask app context."""
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
    
    return celery


# Create Celery instance (can be imported by worker)
celery = make_celery()
