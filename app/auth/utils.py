# app/auth/utils.py
"""Authentication utilities."""

import secrets
from datetime import datetime, timedelta
from flask import url_for, current_app
from flask_mail import Message
from app.extensions import db, mail
from app.models import PasswordReset


def generate_reset_token():
    """Generate secure password reset token."""
    return secrets.token_urlsafe(32)


def create_password_reset(user):
    """Create password reset token for user.
    
    Args:
        user: TutorialUser instance
    
    Returns:
        PasswordReset instance
    """
    token = generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    reset = PasswordReset(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    
    db.session.add(reset)
    db.session.commit()
    
    return reset


def send_password_reset_email(user, token):
    """Send password reset email.
    
    Args:
        user: TutorialUser instance
        token: Password reset token
    """
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    msg = Message(
        subject='Password Reset Request',
        recipients=[user.email],
        body=f'''Hi {user.full_name or user.email},

You requested a password reset for your Tutorial E-Commerce Platform account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
Tutorial E-Commerce Platform Team
'''
    )
    
    mail.send(msg)


def send_welcome_email(user):
    """Send welcome email to new user.
    
    Args:
        user: TutorialUser instance
    """
    msg = Message(
        subject='Welcome to Tutorial E-Commerce Platform',
        recipients=[user.email],
        body=f'''Hi {user.full_name or user.email},

Welcome to Tutorial E-Commerce Platform!

Your account has been created successfully. You can now browse our courses and start learning.

Login here: {url_for('auth.login', _external=True)}

Best regards,
Tutorial E-Commerce Platform Team
'''
    )
    
    mail.send(msg)
