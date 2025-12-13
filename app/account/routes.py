# app/account/routes.py
"""Account management routes."""

import logging
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from sqlalchemy import func

from app.account import account_bp
from app.models import (
    TutorialEnrollment, TutorialOrder, NewTutorial, Wishlist,
    Certificate, Review, Notification, UserAchievement, Achievement
)
from app.extensions import db
from app.account.analytics_utils import (
    get_dashboard_stats, update_user_analytics, get_learning_insights
)
from app.account.achievement_utils import (
    get_user_achievements, get_achievement_stats, check_and_unlock_achievements
)
from app.account.certificate_utils import (
    get_user_certificates, verify_certificate, generate_certificate_pdf
)
from app.account.utils import get_continue_learning_destination

logger = logging.getLogger(__name__)


@account_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard overview with analytics."""
    # Get comprehensive dashboard stats
    stats = get_dashboard_stats(current_user.id)
    
    # Get learning insights
    insights = get_learning_insights(current_user.id)
    
    # Get unread notifications
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    # Get achievement stats
    achievement_stats = get_achievement_stats(current_user.id)
    
    # Course type breakdown
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
                         stats=stats,
                         insights=insights,
                         unread_notifications=unread_notifications,
                         achievement_stats=achievement_stats,
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


@account_bp.route('/continue-learning/<int:enrollment_id>')
@login_required
def continue_learning(enrollment_id):
    """Smart routing for continue learning feature."""
    # Verify enrollment belongs to user
    enrollment = TutorialEnrollment.query.filter_by(
        id=enrollment_id,
        user_id=current_user.id
    ).first_or_404()
    
    # Check if enrollment is active
    if enrollment.status != 'active':
        flash('This course enrollment is not active', 'error')
        return redirect(url_for('account.my_courses'))
    
    # Check expiration
    if enrollment.expires_at and enrollment.expires_at < datetime.utcnow():
        flash('This course has expired', 'warning')
        return redirect(url_for('account.my_courses'))
    
    # Get destination
    destination = get_continue_learning_destination(
        current_user.id, 
        enrollment_id
    )
    
    # Update last accessed timestamp
    enrollment.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Log the event
    logger.info(f"User {current_user.id} continued learning: "
                f"Enrollment {enrollment_id}, "
                f"Routed to {destination['type']}")
    
    # Redirect to destination
    return redirect(destination['url'])


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


# ===== PHASE 7: Analytics Routes =====

@account_bp.route('/analytics')
@login_required
def analytics():
    """Detailed learning analytics page."""
    # Update analytics first
    analytics_data = update_user_analytics(current_user.id)
    
    # Get dashboard stats with charts data
    stats = get_dashboard_stats(current_user.id)
    
    # Get insights
    insights = get_learning_insights(current_user.id)
    
    return render_template('account/analytics.html',
                         analytics=analytics_data,
                         stats=stats,
                         insights=insights)


# ===== PHASE 7: Certificate Routes =====

@account_bp.route('/certificates')
@login_required
def certificates():
    """Display user's certificates."""
    certificates = get_user_certificates(current_user.id)
    
    return render_template('account/certificates.html',
                         certificates=certificates)


@account_bp.route('/certificate/<int:certificate_id>')
@login_required
def view_certificate(certificate_id):
    """View a specific certificate."""
    certificate = Certificate.query.get_or_404(certificate_id)
    
    # Verify ownership
    if certificate.user_id != current_user.id:
        flash('You do not have permission to view this certificate.', 'error')
        return redirect(url_for('account.certificates'))
    
    return render_template('account/view_certificate.html',
                         certificate=certificate)


@account_bp.route('/certificate/<int:certificate_id>/download')
@login_required
def download_certificate(certificate_id):
    """Download certificate PDF."""
    certificate = Certificate.query.get_or_404(certificate_id)
    
    # Verify ownership
    if certificate.user_id != current_user.id:
        flash('You do not have permission to download this certificate.', 'error')
        return redirect(url_for('account.certificates'))
    
    if not certificate.pdf_path:
        flash('Certificate PDF not available.', 'error')
        return redirect(url_for('account.certificates'))
    
    try:
        return send_file(certificate.pdf_path, as_attachment=True,
                        download_name=f'certificate_{certificate.certificate_number}.pdf')
    except Exception as e:
        logger.error(f"Error downloading certificate: {e}")
        flash('Error downloading certificate.', 'error')
        return redirect(url_for('account.certificates'))


@account_bp.route('/certificate/verify', methods=['GET', 'POST'])
def verify_certificate_page():
    """Certificate verification page."""
    certificate = None
    is_valid = None
    message = None
    
    if request.method == 'POST':
        cert_number = request.form.get('certificate_number', '').strip()
        verify_code = request.form.get('verification_code', '').strip()
        
        is_valid, certificate, message = verify_certificate(
            certificate_number=cert_number if cert_number else None,
            verification_code=verify_code if verify_code else None
        )
    
    return render_template('account/verify_certificate.html',
                         certificate=certificate,
                         is_valid=is_valid,
                         message=message)


# ===== PHASE 7: Achievement Routes =====

@account_bp.route('/achievements')
@login_required
def achievements():
    """Display user's achievements."""
    achievements_by_category = get_user_achievements(current_user.id, include_locked=True)
    achievement_stats = get_achievement_stats(current_user.id)
    
    return render_template('account/achievements.html',
                         achievements=achievements_by_category,
                         stats=achievement_stats)


@account_bp.route('/achievements/refresh', methods=['POST'])
@login_required
def refresh_achievements():
    """Manually refresh/check achievements."""
    newly_unlocked = check_and_unlock_achievements(current_user.id)
    
    if newly_unlocked:
        flash(f'Unlocked {len(newly_unlocked)} new achievement(s)!', 'success')
    else:
        flash('No new achievements unlocked.', 'info')
    
    return redirect(url_for('account.achievements'))


# ===== PHASE 7: Notification Routes =====

@account_bp.route('/notifications')
@login_required
def notifications():
    """Display user notifications."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.is_read.asc(), Notification.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('account/notifications.html',
                         notifications=notifications)


@account_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read."""
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.mark_as_read()
    
    return jsonify({'success': True})


@account_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read."""
    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({'is_read': True, 'read_at': datetime.utcnow()})
    
    db.session.commit()
    
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('account.notifications'))


@account_bp.route('/notifications/unread-count')
@login_required
def unread_notification_count():
    """Get unread notification count (for navbar)."""
    count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    
    return jsonify({'count': count})


# ===== PHASE 7: Review Routes =====

@account_bp.route('/tutorial/<int:tutorial_id>/review', methods=['GET', 'POST'])
@login_required
def add_review(tutorial_id):
    """Add or edit review for a course."""
    tutorial = NewTutorial.query.get_or_404(tutorial_id)
    
    # Check if user is enrolled
    enrollment = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        tutorial_id=tutorial_id,
        status='active'
    ).first()
    
    if not enrollment:
        flash('You must be enrolled in this course to leave a review.', 'error')
        return redirect(url_for('catalog.tutorial_detail', slug=tutorial.slug))
    
    # Check if review already exists
    existing_review = Review.query.filter_by(
        user_id=current_user.id,
        tutorial_id=tutorial_id
    ).first()
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        title = request.form.get('title', '').strip()
        comment = request.form.get('comment', '').strip()
        
        # Validate
        if not rating or rating < 1 or rating > 5:
            flash('Please provide a rating between 1 and 5.', 'error')
        elif not comment:
            flash('Please provide a review comment.', 'error')
        else:
            if existing_review:
                # Update existing review
                existing_review.rating = rating
                existing_review.title = title
                existing_review.comment = comment
                existing_review.updated_at = datetime.utcnow()
                flash('Your review has been updated.', 'success')
            else:
                # Create new review
                review = Review(
                    user_id=current_user.id,
                    tutorial_id=tutorial_id,
                    enrollment_id=enrollment.id,
                    rating=rating,
                    title=title,
                    comment=comment,
                    is_verified_purchase=True
                )
                db.session.add(review)
                flash('Thank you for your review!', 'success')
                
                # Trigger achievement check
                from app.account.achievement_utils import trigger_achievement_check
                trigger_achievement_check(current_user.id, 'review_written')
            
            db.session.commit()
            return redirect(url_for('catalog.tutorial_detail', slug=tutorial.slug))
    
    return render_template('account/add_review.html',
                         tutorial=tutorial,
                         existing_review=existing_review)
