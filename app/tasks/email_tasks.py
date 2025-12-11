# app/tasks/email_tasks.py
"""Celery tasks for email notifications."""

from app.celery_app import celery
from flask_mail import Message
from app.extensions import mail


@celery.task(name='app.tasks.email_tasks.send_email_async', bind=True)
def send_email_async(self, subject, recipients, text_body, html_body=None, sender=None):
    """
    Send email asynchronously.
    
    Args:
        self: Celery task instance
        subject: Email subject
        recipients: List of recipient email addresses
        text_body: Plain text email body
        html_body: HTML email body (optional)
        sender: Sender email address (optional)
    """
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        try:
            msg = Message(
                subject=subject,
                recipients=recipients if isinstance(recipients, list) else [recipients],
                body=text_body,
                html=html_body,
                sender=sender or app.config.get('MAIL_DEFAULT_SENDER')
            )
            
            mail.send(msg)
            return {'status': 'success'}
            
        except Exception as e:
            print(f'Error sending email: {str(e)}')
            return {'status': 'error', 'error': str(e)}


@celery.task(name='app.tasks.email_tasks.send_code_execution_notification')
def send_code_execution_notification(user_email, exercise_title, status):
    """
    Send notification about code execution result.
    
    Args:
        user_email: User's email address
        exercise_title: Exercise title
        status: Execution status ('passed', 'failed', etc.)
    """
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        subject = f'Code Execution Result: {exercise_title}'
        
        if status == 'passed':
            text_body = f'Congratulations! Your solution for "{exercise_title}" passed all tests.'
        else:
            text_body = f'Your solution for "{exercise_title}" did not pass all tests. Keep trying!'
        
        return send_email_async(subject, user_email, text_body)
