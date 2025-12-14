"""Decorators for instructor panel access control."""
from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user


def instructor_required(f):
    """Require user to be an instructor or admin to access route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access the instructor panel.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not (current_user.is_instructor or current_user.is_admin):
            flash('You do not have permission to access the instructor panel.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def can_edit_course(user, course):
    """Check if user can edit a specific course."""
    if user.is_admin:
        return True  # Admins can edit any course
    if user.is_instructor and course.instructor_id == user.id:
        return True  # Instructors can edit their own courses
    return False
