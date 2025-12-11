# app/auth/routes.py
"""Authentication routes."""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import auth_bp
from app.auth.forms import (
    RegistrationForm, LoginForm, 
    RequestPasswordResetForm, ResetPasswordForm
)
from app.auth.utils import create_password_reset, send_password_reset_email, send_welcome_email
from app.models import TutorialUser, PasswordReset
from app.extensions import db
from datetime import datetime


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = TutorialUser(
            email=form.email.data.lower(),
            username=form.username.data or None,
            full_name=form.full_name.data or None,
            email_verified=False
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Send welcome email (in production, use background task)
        try:
            send_welcome_email(user)
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = TutorialUser.query.filter_by(email=form.email.data.lower()).first()
        
        if user is None:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))
        
        if user.is_locked():
            flash('Account is locked due to multiple failed login attempts. Try again later.', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.check_password(form.password.data):
            user.increment_failed_login()
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Your account has been deactivated.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Successful login
        user.reset_failed_login()
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=form.remember_me.data)
        
        # Redirect to next page or home
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        flash('Login successful!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def request_password_reset():
    """Request password reset."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RequestPasswordResetForm()
    
    if form.validate_on_submit():
        user = TutorialUser.query.filter_by(email=form.email.data.lower()).first()
        
        if user:
            reset = create_password_reset(user)
            try:
                send_password_reset_email(user, reset.token)
                flash('Password reset instructions sent to your email.', 'info')
            except Exception as e:
                print(f"Failed to send reset email: {e}")
                flash('Failed to send reset email. Please try again.', 'danger')
        else:
            # Don't reveal if email exists
            flash('If that email exists, password reset instructions have been sent.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/request_reset.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    reset = PasswordReset.query.filter_by(token=token).first()
    
    if not reset or not reset.is_valid():
        flash('Invalid or expired password reset link.', 'danger')
        return redirect(url_for('auth.request_password_reset'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        reset.user.set_password(form.password.data)
        reset.used = True
        db.session.commit()
        
        flash('Your password has been reset. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)
