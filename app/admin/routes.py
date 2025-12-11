# app/admin/routes.py
"""Admin routes for course management."""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.admin.decorators import admin_required
from app.admin.forms import TutorialForm, LessonForm, ExerciseForm
from app.models import NewTutorial, Lesson, Exercise, TutorialUser
from app.extensions import db
from datetime import datetime
from sqlalchemy import func


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with statistics."""
    # Get statistics
    total_tutorials = NewTutorial.query.count()
    python_tutorials = NewTutorial.query.filter_by(course_type='python').count()
    sql_tutorials = NewTutorial.query.filter_by(course_type='sql').count()
    published_tutorials = NewTutorial.query.filter_by(status='published').count()
    total_users = TutorialUser.query.count()
    total_lessons = Lesson.query.count()
    total_exercises = Exercise.query.count()
    
    # Recent tutorials
    recent_tutorials = NewTutorial.query.order_by(NewTutorial.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_tutorials=total_tutorials,
                         python_tutorials=python_tutorials,
                         sql_tutorials=sql_tutorials,
                         published_tutorials=published_tutorials,
                         total_users=total_users,
                         total_lessons=total_lessons,
                         total_exercises=total_exercises,
                         recent_tutorials=recent_tutorials)


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
