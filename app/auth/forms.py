# app/auth/forms.py
"""Authentication forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import TutorialUser


class RegistrationForm(FlaskForm):
    """User registration form."""
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=255)
    ])
    username = StringField('Username (optional)', validators=[
        Length(max=100)
    ])
    full_name = StringField('Full Name', validators=[
        Length(max=200)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        """Check if email already exists."""
        if TutorialUser.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')
    
    def validate_username(self, field):
        """Check if username already exists."""
        if field.data and TutorialUser.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken.')


class LoginForm(FlaskForm):
    """User login form."""
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RequestPasswordResetForm(FlaskForm):
    """Request password reset form."""
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    """Reset password form."""
    
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8)
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
