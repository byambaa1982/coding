# app/admin/routes.py
"""Admin routes for course management."""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.admin.decorators import admin_required
from app.admin.forms import TutorialForm, LessonForm, ExerciseForm
from app.models import NewTutorial, Lesson, Exercise, TutorialUser, TutorialOrderItem
from app.extensions import db
from datetime import datetime
from sqlalchemy import func, case


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with comprehensive KPIs and statistics."""
    from app.models import TutorialEnrollment, TutorialOrder, ExerciseSubmission
    from sqlalchemy import func, and_
    from datetime import datetime, timedelta
    
    # Course statistics
    total_tutorials = NewTutorial.query.count()
    python_tutorials = NewTutorial.query.filter_by(course_type='python').count()
    sql_tutorials = NewTutorial.query.filter_by(course_type='sql').count()
    published_tutorials = NewTutorial.query.filter_by(status='published').count()
    draft_tutorials = NewTutorial.query.filter_by(status='draft').count()
    total_lessons = Lesson.query.count()
    total_exercises = Exercise.query.count()
    
    # User statistics
    total_users = TutorialUser.query.count()
    active_users = TutorialUser.query.filter_by(is_active=True).count()
    new_users_today = TutorialUser.query.filter(
        TutorialUser.created_at >= datetime.utcnow().date()
    ).count()
    new_users_week = TutorialUser.query.filter(
        TutorialUser.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    # Enrollment statistics
    total_enrollments = TutorialEnrollment.query.count()
    active_enrollments = TutorialEnrollment.query.filter_by(status='active').count()
    completed_enrollments = TutorialEnrollment.query.filter_by(is_completed=True).count()
    enrollments_today = TutorialEnrollment.query.filter(
        TutorialEnrollment.enrolled_at >= datetime.utcnow().date()
    ).count()
    enrollments_week = TutorialEnrollment.query.filter(
        TutorialEnrollment.enrolled_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    # Revenue statistics
    total_orders = TutorialOrder.query.count()
    completed_orders = TutorialOrder.query.filter_by(status='completed').count()
    total_revenue = db.session.query(func.sum(TutorialOrder.total_amount)).filter_by(
        status='completed'
    ).scalar() or 0
    revenue_today = db.session.query(func.sum(TutorialOrder.total_amount)).filter(
        and_(TutorialOrder.status == 'completed',
             TutorialOrder.paid_at >= datetime.utcnow().date())
    ).scalar() or 0
    revenue_week = db.session.query(func.sum(TutorialOrder.total_amount)).filter(
        and_(TutorialOrder.status == 'completed',
             TutorialOrder.paid_at >= datetime.utcnow() - timedelta(days=7))
    ).scalar() or 0
    revenue_month = db.session.query(func.sum(TutorialOrder.total_amount)).filter(
        and_(TutorialOrder.status == 'completed',
             TutorialOrder.paid_at >= datetime.utcnow() - timedelta(days=30))
    ).scalar() or 0
    
    # Exercise submission statistics
    total_submissions = ExerciseSubmission.query.count()
    passed_submissions = ExerciseSubmission.query.filter_by(status='passed').count()
    submissions_today = ExerciseSubmission.query.filter(
        ExerciseSubmission.submitted_at >= datetime.utcnow().date()
    ).count()
    
    # Top courses by enrollment
    top_courses_by_enrollment = db.session.query(
        NewTutorial.id,
        NewTutorial.title,
        NewTutorial.course_type,
        func.count(TutorialEnrollment.id).label('enrollment_count')
    ).join(TutorialEnrollment).group_by(
        NewTutorial.id, NewTutorial.title, NewTutorial.course_type
    ).order_by(func.count(TutorialEnrollment.id).desc()).limit(5).all()
    
    # Top courses by revenue
    top_courses_by_revenue = db.session.query(
        NewTutorial.id,
        NewTutorial.title,
        NewTutorial.course_type,
        func.sum(TutorialOrder.total_amount).label('revenue')
    ).join(TutorialOrderItem, TutorialOrderItem.tutorial_id == NewTutorial.id
    ).join(TutorialOrder, TutorialOrder.id == TutorialOrderItem.order_id
    ).filter(TutorialOrder.status == 'completed'
    ).group_by(NewTutorial.id, NewTutorial.title, NewTutorial.course_type
    ).order_by(func.sum(TutorialOrder.total_amount).desc()).limit(5).all()
    
    # Recent activities
    recent_tutorials = NewTutorial.query.order_by(NewTutorial.created_at.desc()).limit(5).all()
    recent_enrollments = TutorialEnrollment.query.order_by(TutorialEnrollment.enrolled_at.desc()).limit(5).all()
    recent_orders = TutorialOrder.query.filter_by(status='completed').order_by(TutorialOrder.paid_at.desc()).limit(5).all()
    
    # System health indicators
    pending_orders = TutorialOrder.query.filter_by(status='pending').count()
    failed_orders = TutorialOrder.query.filter_by(status='failed').count()
    
    return render_template('admin/dashboard.html',
                         # Course stats
                         total_tutorials=total_tutorials,
                         python_tutorials=python_tutorials,
                         sql_tutorials=sql_tutorials,
                         published_tutorials=published_tutorials,
                         draft_tutorials=draft_tutorials,
                         total_lessons=total_lessons,
                         total_exercises=total_exercises,
                         # User stats
                         total_users=total_users,
                         active_users=active_users,
                         new_users_today=new_users_today,
                         new_users_week=new_users_week,
                         # Enrollment stats
                         total_enrollments=total_enrollments,
                         active_enrollments=active_enrollments,
                         completed_enrollments=completed_enrollments,
                         enrollments_today=enrollments_today,
                         enrollments_week=enrollments_week,
                         # Revenue stats
                         total_orders=total_orders,
                         completed_orders=completed_orders,
                         total_revenue=total_revenue,
                         revenue_today=revenue_today,
                         revenue_week=revenue_week,
                         revenue_month=revenue_month,
                         # Exercise stats
                         total_submissions=total_submissions,
                         passed_submissions=passed_submissions,
                         submissions_today=submissions_today,
                         # Top courses
                         top_courses_by_enrollment=top_courses_by_enrollment,
                         top_courses_by_revenue=top_courses_by_revenue,
                         # Recent activities
                         recent_tutorials=recent_tutorials,
                         recent_enrollments=recent_enrollments,
                         recent_orders=recent_orders,
                         # System health
                         pending_orders=pending_orders,
                         failed_orders=failed_orders)


@admin_bp.route('/courses')
@login_required
@admin_required
def courses_list():
    """List all courses with filtering."""
    page = request.args.get('page', 1, type=int)
    course_type = request.args.get('type', None)
    status = request.args.get('status', None)
    
    query = NewTutorial.query
    
    if course_type:
        query = query.filter_by(course_type=course_type)
    if status:
        query = query.filter_by(status=status)
    
    tutorials = query.order_by(NewTutorial.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/courses/list.html', 
                         tutorials=tutorials,
                         current_type=course_type,
                         current_status=status)


@admin_bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
@admin_required
def course_create():
    """Create a new course."""
    form = TutorialForm()
    
    if form.validate_on_submit():
        tutorial = NewTutorial(
            instructor_id=current_user.id,
            title=form.title.data,
            slug=form.slug.data,
            short_description=form.short_description.data,
            description=form.description.data,
            course_type=form.course_type.data,
            category=form.category.data,
            difficulty_level=form.difficulty_level.data,
            price=form.price.data,
            is_free=form.is_free.data,
            is_featured=form.is_featured.data,
            thumbnail_url=form.thumbnail_url.data,
            preview_video_url=form.preview_video_url.data,
            tags=form.tags.data,
            estimated_duration_hours=form.estimated_duration_hours.data,
            status=form.status.data
        )
        
        if form.status.data == 'published' and not tutorial.published_at:
            tutorial.published_at = datetime.utcnow()
        
        db.session.add(tutorial)
        db.session.commit()
        
        flash(f'Course "{tutorial.title}" created successfully!', 'success')
        return redirect(url_for('admin.course_edit', course_id=tutorial.id))
    
    return render_template('admin/courses/create.html', form=form)


@admin_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def course_edit(course_id):
    """Edit an existing course."""
    tutorial = NewTutorial.query.get_or_404(course_id)
    form = TutorialForm(obj=tutorial)
    
    if form.validate_on_submit():
        tutorial.title = form.title.data
        tutorial.slug = form.slug.data
        tutorial.short_description = form.short_description.data
        tutorial.description = form.description.data
        tutorial.course_type = form.course_type.data
        tutorial.category = form.category.data
        tutorial.difficulty_level = form.difficulty_level.data
        tutorial.price = form.price.data
        tutorial.is_free = form.is_free.data
        tutorial.is_featured = form.is_featured.data
        tutorial.thumbnail_url = form.thumbnail_url.data
        tutorial.preview_video_url = form.preview_video_url.data
        tutorial.tags = form.tags.data
        tutorial.estimated_duration_hours = form.estimated_duration_hours.data
        
        # Update published date if status changes to published
        if form.status.data == 'published' and tutorial.status != 'published':
            tutorial.published_at = datetime.utcnow()
        
        tutorial.status = form.status.data
        
        db.session.commit()
        
        flash(f'Course "{tutorial.title}" updated successfully!', 'success')
        return redirect(url_for('admin.course_edit', course_id=tutorial.id))
    
    # Get lessons for this course
    lessons = Lesson.query.filter_by(tutorial_id=course_id).order_by(Lesson.order_index).all()
    exercises = Exercise.query.filter_by(tutorial_id=course_id).order_by(Exercise.order_index).all()
    
    return render_template('admin/courses/edit.html', 
                         form=form, 
                         tutorial=tutorial,
                         lessons=lessons,
                         exercises=exercises)


@admin_bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
@admin_required
def course_delete(course_id):
    """Delete a course."""
    tutorial = NewTutorial.query.get_or_404(course_id)
    title = tutorial.title
    
    # Delete associated lessons and exercises
    Lesson.query.filter_by(tutorial_id=course_id).delete()
    Exercise.query.filter_by(tutorial_id=course_id).delete()
    
    db.session.delete(tutorial)
    db.session.commit()
    
    flash(f'Course "{title}" deleted successfully!', 'success')
    return redirect(url_for('admin.courses_list'))


@admin_bp.route('/courses/<int:course_id>/lessons/create', methods=['GET', 'POST'])
@login_required
@admin_required
def lesson_create(course_id):
    """Create a new lesson for a course."""
    tutorial = NewTutorial.query.get_or_404(course_id)
    form = LessonForm()
    
    if form.validate_on_submit():
        lesson = Lesson(
            tutorial_id=course_id,
            title=form.title.data,
            slug=form.slug.data,
            description=form.description.data,
            content_type=form.content_type.data,
            content=form.content.data,
            video_url=form.video_url.data,
            video_duration_seconds=form.video_duration_seconds.data,
            section_name=form.section_name.data,
            order_index=form.order_index.data,
            is_free_preview=form.is_free_preview.data,
            estimated_duration_minutes=form.estimated_duration_minutes.data
        )
        
        db.session.add(lesson)
        
        # Update total lessons count
        tutorial.total_lessons = Lesson.query.filter_by(tutorial_id=course_id).count() + 1
        
        db.session.commit()
        
        flash(f'Lesson "{lesson.title}" created successfully!', 'success')
        return redirect(url_for('admin.course_edit', course_id=course_id))
    
    # Set default order_index to next available
    max_order = db.session.query(func.max(Lesson.order_index)).filter_by(tutorial_id=course_id).scalar()
    form.order_index.data = (max_order or 0) + 1
    
    return render_template('admin/lessons/create.html', form=form, tutorial=tutorial)


@admin_bp.route('/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def lesson_edit(lesson_id):
    """Edit an existing lesson."""
    lesson = Lesson.query.get_or_404(lesson_id)
    form = LessonForm(obj=lesson)
    
    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.slug = form.slug.data
        lesson.description = form.description.data
        lesson.content_type = form.content_type.data
        lesson.content = form.content.data
        lesson.video_url = form.video_url.data
        lesson.video_duration_seconds = form.video_duration_seconds.data
        lesson.section_name = form.section_name.data
        lesson.order_index = form.order_index.data
        lesson.is_free_preview = form.is_free_preview.data
        lesson.estimated_duration_minutes = form.estimated_duration_minutes.data
        
        db.session.commit()
        
        flash(f'Lesson "{lesson.title}" updated successfully!', 'success')
        return redirect(url_for('admin.course_edit', course_id=lesson.tutorial_id))
    
    return render_template('admin/lessons/edit.html', form=form, lesson=lesson)


@admin_bp.route('/lessons/<int:lesson_id>/delete', methods=['POST'])
@login_required
@admin_required
def lesson_delete(lesson_id):
    """Delete a lesson."""
    lesson = Lesson.query.get_or_404(lesson_id)
    course_id = lesson.tutorial_id
    title = lesson.title
    
    # Delete associated exercises
    Exercise.query.filter_by(lesson_id=lesson_id).delete()
    
    db.session.delete(lesson)
    
    # Update total lessons count
    tutorial = NewTutorial.query.get(course_id)
    tutorial.total_lessons = Lesson.query.filter_by(tutorial_id=course_id).count() - 1
    
    db.session.commit()
    
    flash(f'Lesson "{title}" deleted successfully!', 'success')
    return redirect(url_for('admin.course_edit', course_id=course_id))


@admin_bp.route('/courses/<int:course_id>/exercises/create', methods=['GET', 'POST'])
@login_required
@admin_required
def exercise_create(course_id):
    """Create a new exercise for a course."""
    tutorial = NewTutorial.query.get_or_404(course_id)
    form = ExerciseForm()
    
    if form.validate_on_submit():
        exercise = Exercise(
            tutorial_id=course_id,
            lesson_id=request.form.get('lesson_id', type=int),
            title=form.title.data,
            slug=form.slug.data,
            description=form.description.data,
            exercise_type=form.exercise_type.data,
            difficulty=form.difficulty.data,
            starter_code=form.starter_code.data,
            solution_code=form.solution_code.data,
            test_cases=form.test_cases.data,
            hints=form.hints.data,
            database_schema=form.database_schema.data,
            sample_data=form.sample_data.data,
            order_index=form.order_index.data,
            points=form.points.data
        )
        
        db.session.add(exercise)
        db.session.commit()
        
        flash(f'Exercise "{exercise.title}" created successfully!', 'success')
        return redirect(url_for('admin.course_edit', course_id=course_id))
    
    # Set default values
    max_order = db.session.query(func.max(Exercise.order_index)).filter_by(tutorial_id=course_id).scalar()
    form.order_index.data = (max_order or 0) + 1
    form.exercise_type.data = tutorial.course_type
    
    lessons = Lesson.query.filter_by(tutorial_id=course_id).order_by(Lesson.order_index).all()
    
    return render_template('admin/exercises/create.html', 
                         form=form, 
                         tutorial=tutorial,
                         lessons=lessons)


@admin_bp.route('/exercises/<int:exercise_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def exercise_edit(exercise_id):
    """Edit an existing exercise."""
    exercise = Exercise.query.get_or_404(exercise_id)
    form = ExerciseForm(obj=exercise)
    
    if form.validate_on_submit():
        exercise.title = form.title.data
        exercise.slug = form.slug.data
        exercise.description = form.description.data
        exercise.exercise_type = form.exercise_type.data
        exercise.difficulty = form.difficulty.data
        exercise.starter_code = form.starter_code.data
        exercise.solution_code = form.solution_code.data
        exercise.test_cases = form.test_cases.data
        exercise.hints = form.hints.data
        exercise.database_schema = form.database_schema.data
        exercise.sample_data = form.sample_data.data
        exercise.order_index = form.order_index.data
        exercise.points = form.points.data
        exercise.lesson_id = request.form.get('lesson_id', type=int)
        
        db.session.commit()
        
        flash(f'Exercise "{exercise.title}" updated successfully!', 'success')
        return redirect(url_for('admin.course_edit', course_id=exercise.tutorial_id))
    
    lessons = Lesson.query.filter_by(tutorial_id=exercise.tutorial_id).order_by(Lesson.order_index).all()
    
    return render_template('admin/exercises/edit.html', 
                         form=form, 
                         exercise=exercise,
                         lessons=lessons)


@admin_bp.route('/exercises/<int:exercise_id>/delete', methods=['POST'])
@login_required
@admin_required
def exercise_delete(exercise_id):
    """Delete an exercise."""
    exercise = Exercise.query.get_or_404(exercise_id)
    course_id = exercise.tutorial_id
    title = exercise.title
    
    db.session.delete(exercise)
    db.session.commit()
    
    flash(f'Exercise "{title}" deleted successfully!', 'success')
    return redirect(url_for('admin.course_edit', course_id=course_id))


# ============================================================================
# USER MANAGEMENT ROUTES
# ============================================================================

@admin_bp.route('/users')
@login_required
@admin_required
def users_list():
    """List all users with search and filter."""
    from app.models import TutorialEnrollment, TutorialOrder
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    role = request.args.get('role', '')
    
    query = TutorialUser.query
    
    # Search filter
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                TutorialUser.email.ilike(search_pattern),
                TutorialUser.username.ilike(search_pattern),
                TutorialUser.full_name.ilike(search_pattern)
            )
        )
    
    # Status filter
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    elif status == 'verified':
        query = query.filter_by(email_verified=True)
    elif status == 'unverified':
        query = query.filter_by(email_verified=False)
    
    # Role filter
    if role == 'admin':
        query = query.filter_by(is_admin=True)
    elif role == 'instructor':
        query = query.filter_by(is_instructor=True)
    elif role == 'student':
        query = query.filter_by(is_admin=False, is_instructor=False)
    
    users = query.order_by(TutorialUser.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get user statistics
    for user in users.items:
        user.enrollment_count = TutorialEnrollment.query.filter_by(user_id=user.id).count()
        user.order_count = TutorialOrder.query.filter_by(user_id=user.id, status='completed').count()
        user.total_spent = db.session.query(func.sum(TutorialOrder.total_amount)).filter_by(
            user_id=user.id, status='completed'
        ).scalar() or 0
    
    return render_template('admin/users/list.html',
                         users=users,
                         search=search,
                         current_status=status,
                         current_role=role)


@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """View detailed user information."""
    from app.models import TutorialEnrollment, TutorialOrder, ExerciseSubmission
    
    user = TutorialUser.query.get_or_404(user_id)
    
    # User enrollments with progress
    enrollments = TutorialEnrollment.query.filter_by(user_id=user_id).order_by(
        TutorialEnrollment.enrolled_at.desc()
    ).all()
    
    # User orders
    orders = TutorialOrder.query.filter_by(user_id=user_id).order_by(
        TutorialOrder.created_at.desc()
    ).all()
    
    # User submissions
    recent_submissions = ExerciseSubmission.query.filter_by(user_id=user_id).order_by(
        ExerciseSubmission.submitted_at.desc()
    ).limit(10).all()
    
    # Statistics
    total_spent = db.session.query(func.sum(TutorialOrder.total_amount)).filter_by(
        user_id=user_id, status='completed'
    ).scalar() or 0
    total_submissions = ExerciseSubmission.query.filter_by(user_id=user_id).count()
    passed_submissions = ExerciseSubmission.query.filter_by(user_id=user_id, status='passed').count()
    
    return render_template('admin/users/detail.html',
                         user=user,
                         enrollments=enrollments,
                         orders=orders,
                         recent_submissions=recent_submissions,
                         total_spent=total_spent,
                         total_submissions=total_submissions,
                         passed_submissions=passed_submissions)


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def user_toggle_active(user_id):
    """Ban/unban a user."""
    user = TutorialUser.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account!', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.email} has been {status}!', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def user_toggle_admin(user_id):
    """Grant/revoke admin privileges."""
    user = TutorialUser.query.get_or_404(user_id)
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {status} for {user.email}!', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/users/<int:user_id>/enroll', methods=['POST'])
@login_required
@admin_required
def user_manual_enroll(user_id):
    """Manually enroll a user in a course."""
    from app.models import TutorialEnrollment
    
    user = TutorialUser.query.get_or_404(user_id)
    tutorial_id = request.form.get('tutorial_id', type=int)
    
    if not tutorial_id:
        flash('Please select a course!', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    tutorial = NewTutorial.query.get_or_404(tutorial_id)
    
    # Check if already enrolled
    existing = TutorialEnrollment.query.filter_by(
        user_id=user_id, tutorial_id=tutorial_id
    ).first()
    
    if existing:
        flash(f'User is already enrolled in "{tutorial.title}"!', 'warning')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    # Create enrollment
    enrollment = TutorialEnrollment(
        user_id=user_id,
        tutorial_id=tutorial_id,
        status='active',
        enrollment_type='gifted'
    )
    
    db.session.add(enrollment)
    db.session.commit()
    
    flash(f'User enrolled in "{tutorial.title}" successfully!', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/users/<int:user_id>/unenroll/<int:enrollment_id>', methods=['POST'])
@login_required
@admin_required
def user_manual_unenroll(user_id, enrollment_id):
    """Manually unenroll a user from a course."""
    from app.models import TutorialEnrollment
    
    enrollment = TutorialEnrollment.query.get_or_404(enrollment_id)
    
    if enrollment.user_id != user_id:
        flash('Invalid enrollment!', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    tutorial_title = enrollment.tutorial.title
    db.session.delete(enrollment)
    db.session.commit()
    
    flash(f'User unenrolled from "{tutorial_title}"!', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))


# ============================================================================
# REVENUE & ANALYTICS ROUTES
# ============================================================================

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Analytics dashboard with detailed reports."""
    from app.models import TutorialEnrollment, TutorialOrder, ExerciseSubmission
    from datetime import datetime, timedelta
    
    # Date range filter
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Revenue analytics
    daily_revenue = db.session.query(
        func.date(TutorialOrder.paid_at).label('date'),
        func.sum(TutorialOrder.total_amount).label('revenue'),
        func.count(TutorialOrder.id).label('orders')
    ).filter(
        TutorialOrder.status == 'completed',
        TutorialOrder.paid_at >= start_date
    ).group_by(func.date(TutorialOrder.paid_at)).order_by('date').all()
    
    # Course type revenue comparison
    course_type_revenue = db.session.query(
        NewTutorial.course_type,
        func.sum(TutorialOrder.total_amount).label('revenue'),
        func.count(TutorialEnrollment.id).label('enrollments')
    ).join(TutorialOrderItem, TutorialOrderItem.tutorial_id == NewTutorial.id
    ).join(TutorialOrder, TutorialOrder.id == TutorialOrderItem.order_id
    ).outerjoin(TutorialEnrollment, TutorialEnrollment.tutorial_id == NewTutorial.id
    ).filter(TutorialOrder.status == 'completed'
    ).group_by(NewTutorial.course_type).all()
    
    # User growth
    daily_signups = db.session.query(
        func.date(TutorialUser.created_at).label('date'),
        func.count(TutorialUser.id).label('signups')
    ).filter(
        TutorialUser.created_at >= start_date
    ).group_by(func.date(TutorialUser.created_at)).order_by('date').all()
    
    # Enrollment trends
    daily_enrollments = db.session.query(
        func.date(TutorialEnrollment.enrolled_at).label('date'),
        func.count(TutorialEnrollment.id).label('enrollments')
    ).filter(
        TutorialEnrollment.enrolled_at >= start_date
    ).group_by(func.date(TutorialEnrollment.enrolled_at)).order_by('date').all()
    
    # Submission activity
    daily_submissions = db.session.query(
        func.date(ExerciseSubmission.submitted_at).label('date'),
        func.count(ExerciseSubmission.id).label('submissions'),
        func.sum(case((ExerciseSubmission.status == 'passed', 1), else_=0)).label('passed')
    ).filter(
        ExerciseSubmission.submitted_at >= start_date
    ).group_by(func.date(ExerciseSubmission.submitted_at)).order_by('date').all()
    
    return render_template('admin/analytics.html',
                         days=days,
                         daily_revenue=daily_revenue,
                         course_type_revenue=course_type_revenue,
                         daily_signups=daily_signups,
                         daily_enrollments=daily_enrollments,
                         daily_submissions=daily_submissions)


@admin_bp.route('/revenue')
@login_required
@admin_required
def revenue():
    """Revenue reports and order management."""
    from app.models import TutorialOrder
    from datetime import datetime, timedelta
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = TutorialOrder.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    orders = query.order_by(TutorialOrder.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Revenue statistics
    total_revenue = db.session.query(func.sum(TutorialOrder.total_amount)).filter_by(
        status='completed'
    ).scalar() or 0
    
    revenue_today = db.session.query(func.sum(TutorialOrder.total_amount)).filter(
        TutorialOrder.status == 'completed',
        TutorialOrder.paid_at >= datetime.utcnow().date()
    ).scalar() or 0
    
    revenue_week = db.session.query(func.sum(TutorialOrder.total_amount)).filter(
        TutorialOrder.status == 'completed',
        TutorialOrder.paid_at >= datetime.utcnow() - timedelta(days=7)
    ).scalar() or 0
    
    revenue_month = db.session.query(func.sum(TutorialOrder.total_amount)).filter(
        TutorialOrder.status == 'completed',
        TutorialOrder.paid_at >= datetime.utcnow() - timedelta(days=30)
    ).scalar() or 0
    
    return render_template('admin/revenue.html',
                         orders=orders,
                         current_status=status_filter,
                         total_revenue=total_revenue,
                         revenue_today=revenue_today,
                         revenue_week=revenue_week,
                         revenue_month=revenue_month)


@admin_bp.route('/orders/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    """View detailed order information."""
    from app.models import TutorialOrder
    
    order = TutorialOrder.query.get_or_404(order_id)
    
    return render_template('admin/orders/detail.html', order=order)


@admin_bp.route('/orders/<int:order_id>/refund', methods=['POST'])
@login_required
@admin_required
def order_refund(order_id):
    """Process order refund."""
    from app.models import TutorialOrder, TutorialEnrollment
    
    order = TutorialOrder.query.get_or_404(order_id)
    
    if order.status != 'completed':
        flash('Only completed orders can be refunded!', 'error')
        return redirect(url_for('admin.order_detail', order_id=order_id))
    
    if order.refunded_at:
        flash('Order has already been refunded!', 'warning')
        return redirect(url_for('admin.order_detail', order_id=order_id))
    
    # Update order status
    order.status = 'refunded'
    order.refunded_at = datetime.utcnow()
    
    # Cancel associated enrollments
    TutorialEnrollment.query.filter_by(order_id=order_id).update({'status': 'cancelled'})
    
    db.session.commit()
    
    flash(f'Order {order.order_number} refunded successfully!', 'success')
    # TODO: Process Stripe refund via payment/stripe_utils.py
    
    return redirect(url_for('admin.order_detail', order_id=order_id))


# ============================================================================
# SYSTEM MONITORING ROUTES
# ============================================================================

@admin_bp.route('/system')
@login_required
@admin_required
def system_health():
    """System health monitoring dashboard."""
    from app.models import TutorialOrder, ExerciseSubmission
    import psutil
    import os
    
    # Database statistics
    db_stats = {
        'users': TutorialUser.query.count(),
        'tutorials': NewTutorial.query.count(),
        'lessons': Lesson.query.count(),
        'exercises': Exercise.query.count(),
        'enrollments': db.session.query(func.count()).select_from(
            db.session.query(TutorialEnrollment).subquery()
        ).scalar(),
        'orders': TutorialOrder.query.count(),
        'submissions': ExerciseSubmission.query.count()
    }
    
    # System resources
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    system_stats = {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'memory_used_gb': memory.used / (1024**3),
        'memory_total_gb': memory.total / (1024**3),
        'disk_percent': disk.percent,
        'disk_used_gb': disk.used / (1024**3),
        'disk_total_gb': disk.total / (1024**3)
    }
    
    # Recent errors (would integrate with error logging system)
    # For now, showing failed orders as proxy
    recent_failures = {
        'failed_orders': TutorialOrder.query.filter_by(status='failed').count(),
        'pending_orders': TutorialOrder.query.filter_by(status='pending').count(),
        'error_submissions': ExerciseSubmission.query.filter_by(status='error').count()
    }
    
    return render_template('admin/system.html',
                         db_stats=db_stats,
                         system_stats=system_stats,
                         recent_failures=recent_failures)


@admin_bp.route('/submissions')
@login_required
@admin_required
def submissions():
    """Monitor exercise submissions for moderation."""
    from app.models import ExerciseSubmission
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    exercise_type = request.args.get('type', '')
    
    query = ExerciseSubmission.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if exercise_type:
        query = query.join(Exercise).filter(Exercise.exercise_type == exercise_type)
    
    submissions = query.order_by(ExerciseSubmission.submitted_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    # Statistics
    total_submissions = ExerciseSubmission.query.count()
    passed_count = ExerciseSubmission.query.filter_by(status='passed').count()
    failed_count = ExerciseSubmission.query.filter_by(status='failed').count()
    error_count = ExerciseSubmission.query.filter_by(status='error').count()
    
    return render_template('admin/submissions.html',
                         submissions=submissions,
                         current_status=status_filter,
                         current_type=exercise_type,
                         total_submissions=total_submissions,
                         passed_count=passed_count,
                         failed_count=failed_count,
                         error_count=error_count)
