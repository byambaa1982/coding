# app/account/routes.py
"""Account management routes."""

import logging
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func

from app.account import account_bp
from app.models import (
    TutorialEnrollment, TutorialOrder, NewTutorial, Wishlist
)
from app.extensions import db

logger = logging.getLogger(__name__)


@account_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard overview."""
    # Get enrollment statistics
    total_enrollments = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).count()
    
    completed_courses = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        status='active',
        is_completed=True
    ).count()
    
    # Get active enrollments with progress
    active_enrollments = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        status='active',
        is_completed=False
    ).order_by(TutorialEnrollment.enrolled_at.desc()).limit(5).all()
    
    # Get recently completed
    recent_completions = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        status='active',
        is_completed=True
    ).order_by(TutorialEnrollment.completed_at.desc()).limit(3).all()
    
    # Get total spent
    total_spent = db.session.query(func.sum(TutorialOrder.total_amount))\
        .filter_by(user_id=current_user.id, status='completed')\
        .scalar() or 0
    
    # Get course type breakdown
    python_courses = TutorialEnrollment.query.join(NewTutorial)\
        .filter(
            TutorialEnrollment.user_id == current_user.id,
            TutorialEnrollment.status == 'active',
            NewTutorial.course_type == 'python'
        ).count()
    
    sql_courses = TutorialEnrollment.query.join(NewTutorial)\
        .filter(
            TutorialEnrollment.user_id == current_user.id,
            TutorialEnrollment.status == 'active',
            NewTutorial.course_type == 'sql'
        ).count()
    
    return render_template('account/dashboard.html',
                         total_enrollments=total_enrollments,
                         completed_courses=completed_courses,
                         active_enrollments=active_enrollments,
                         recent_completions=recent_completions,
                         total_spent=total_spent,
                         python_courses=python_courses,
                         sql_courses=sql_courses)


@account_bp.route('/my-courses')
@login_required
def my_courses():
    """Display user's enrolled courses."""
    # Get filter parameters
    course_type = request.args.get('type', 'all')
    status_filter = request.args.get('status', 'active')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Build query
    query = TutorialEnrollment.query.filter_by(user_id=current_user.id)
    
    # Apply status filter
    if status_filter == 'in-progress':
        query = query.filter_by(status='active', is_completed=False)
    elif status_filter == 'completed':
        query = query.filter_by(status='active', is_completed=True)
    else:
        query = query.filter_by(status='active')
    
    # Apply course type filter
    if course_type != 'all':
        query = query.join(NewTutorial).filter(NewTutorial.course_type == course_type)
    
    # Paginate
    enrollments = query.order_by(TutorialEnrollment.enrolled_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('account/my_courses.html',
                         enrollments=enrollments,
                         course_type=course_type,
                         status_filter=status_filter)


@account_bp.route('/progress')
@login_required
def progress():
    """Display detailed progress analytics."""
    # Get all active enrollments
    enrollments = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).all()
    
    # Calculate statistics
    total_courses = len(enrollments)
    completed = sum(1 for e in enrollments if e.is_completed)
    in_progress = total_courses - completed
    
    # Average progress
    avg_progress = sum(float(e.progress_percentage) for e in enrollments) / total_courses if total_courses > 0 else 0
    
    # Total lessons and exercises completed
    total_lessons = sum(e.lessons_completed for e in enrollments)
    total_exercises = sum(e.exercises_completed for e in enrollments)
    
    # Group by course type
    python_enrollments = [e for e in enrollments if e.tutorial.course_type == 'python']
    sql_enrollments = [e for e in enrollments if e.tutorial.course_type == 'sql']
    
    return render_template('account/progress.html',
                         enrollments=enrollments,
                         total_courses=total_courses,
                         completed=completed,
                         in_progress=in_progress,
                         avg_progress=avg_progress,
                         total_lessons=total_lessons,
                         total_exercises=total_exercises,
                         python_enrollments=python_enrollments,
                         sql_enrollments=sql_enrollments)


@account_bp.route('/wishlist')
@login_required
def wishlist():
    """Display user's wishlist."""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id)\
        .order_by(Wishlist.added_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('account/wishlist.html', wishlist_items=wishlist_items)


@account_bp.route('/wishlist/add/<int:tutorial_id>', methods=['POST'])
@login_required
def add_to_wishlist(tutorial_id):
    """Add course to wishlist."""
    tutorial = NewTutorial.query.get_or_404(tutorial_id)
    
    # Check if already in wishlist
    existing = Wishlist.query.filter_by(
        user_id=current_user.id,
        tutorial_id=tutorial_id
    ).first()
    
    if existing:
        flash('This course is already in your wishlist.', 'info')
    else:
        wishlist_item = Wishlist(
            user_id=current_user.id,
            tutorial_id=tutorial_id
        )
        db.session.add(wishlist_item)
        db.session.commit()
        flash(f'Added "{tutorial.title}" to wishlist.', 'success')
    
    return redirect(request.referrer or url_for('catalog.index'))


@account_bp.route('/wishlist/remove/<int:tutorial_id>', methods=['POST'])
@login_required
def remove_from_wishlist(tutorial_id):
    """Remove course from wishlist."""
    wishlist_item = Wishlist.query.filter_by(
        user_id=current_user.id,
        tutorial_id=tutorial_id
    ).first()
    
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
        flash('Removed from wishlist.', 'success')
    
    return redirect(request.referrer or url_for('account.wishlist'))


@account_bp.route('/settings')
@login_required
def settings():
    """User account settings."""
    return render_template('account/settings.html')


@account_bp.route('/billing')
@login_required
def billing():
    """User billing and payment history."""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    orders = TutorialOrder.query.filter_by(user_id=current_user.id)\
        .order_by(TutorialOrder.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('account/billing.html', orders=orders)
