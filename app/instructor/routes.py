"""Routes for instructor panel."""
from flask import render_template, redirect, url_for, flash, request, abort, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename
from app.instructor import instructor_bp
from app.instructor.decorators import instructor_required, can_edit_course
from app.instructor.forms import CourseForm, LessonForm, ExerciseForm
from app.models import NewTutorial, Lesson, Exercise, TutorialEnrollment, db
from datetime import datetime
import re
import os
from PIL import Image


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})


@instructor_bp.route('/')
@instructor_bp.route('/dashboard')
@login_required
@instructor_required
def dashboard():
    """Instructor dashboard showing their courses and stats."""
    # Get instructor's courses
    if current_user.is_admin:
        # Admins see all courses
        courses = NewTutorial.query.order_by(NewTutorial.created_at.desc()).all()
    else:
        # Instructors see only their courses
        courses = NewTutorial.query.filter_by(
            instructor_id=current_user.id
        ).order_by(NewTutorial.created_at.desc()).all()
    
    # Calculate stats
    total_courses = len(courses)
    published_courses = sum(1 for c in courses if c.status == 'published')
    draft_courses = sum(1 for c in courses if c.status == 'draft')
    total_enrollments = sum(c.enrollment_count for c in courses)
    
    # Get recent enrollments for instructor's courses
    course_ids = [c.id for c in courses]
    recent_enrollments = TutorialEnrollment.query.filter(
        TutorialEnrollment.tutorial_id.in_(course_ids)
    ).order_by(TutorialEnrollment.enrolled_at.desc()).limit(10).all() if course_ids else []
    
    stats = {
        'total_courses': total_courses,
        'published_courses': published_courses,
        'draft_courses': draft_courses,
        'total_enrollments': total_enrollments
    }
    
    return render_template('instructor/dashboard.html', 
                         courses=courses, 
                         stats=stats,
                         recent_enrollments=recent_enrollments)


@instructor_bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
@instructor_required
def create_course():
    """Create a new course."""
    form = CourseForm()
    
    if form.validate_on_submit():
        # Create slug from title
        slug = slugify(form.title.data)
        
        # Ensure unique slug
        existing = NewTutorial.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{datetime.utcnow().timestamp()}"
        
        # Create course
        course = NewTutorial(
            instructor_id=current_user.id,
            title=form.title.data,
            slug=slug,
            description=form.description.data,
            short_description=form.short_description.data,
            course_type=form.course_type.data,
            category=form.category.data,
            difficulty_level=form.difficulty_level.data,
            price=form.price.data,
            is_free=form.is_free.data,
            estimated_duration_hours=form.estimated_duration_hours.data,
            thumbnail_url=form.thumbnail_url.data,
            preview_video_url=form.preview_video_url.data,
            tags=form.tags.data,
            status='draft'
        )
        
        db.session.add(course)
        db.session.commit()
        
        flash(f'Course "{course.title}" created successfully!', 'success')
        return redirect(url_for('instructor.edit_course', course_id=course.id))
    
    return render_template('instructor/course_form.html', form=form, mode='create')


@instructor_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@instructor_required
def edit_course(course_id):
    """Edit course metadata."""
    course = NewTutorial.query.get_or_404(course_id)
    
    # Check permissions
    if not can_edit_course(current_user, course):
        flash('You do not have permission to edit this course.', 'danger')
        abort(403)
    
    form = CourseForm(obj=course)
    
    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        course.short_description = form.short_description.data
        course.course_type = form.course_type.data
        course.category = form.category.data
        course.difficulty_level = form.difficulty_level.data
        course.price = form.price.data
        course.is_free = form.is_free.data
        course.estimated_duration_hours = form.estimated_duration_hours.data
        course.thumbnail_url = form.thumbnail_url.data
        course.preview_video_url = form.preview_video_url.data
        course.tags = form.tags.data
        
        db.session.commit()
        
        flash('Course updated successfully!', 'success')
        return redirect(url_for('instructor.course_detail', course_id=course.id))
    
    return render_template('instructor/course_form.html', form=form, course=course, mode='edit')


@instructor_bp.route('/courses/<int:course_id>')
@login_required
@instructor_required
def course_detail(course_id):
    """View course details with lessons and exercises."""
    course = NewTutorial.query.get_or_404(course_id)
    
    # Check permissions
    if not can_edit_course(current_user, course):
        flash('You do not have permission to view this course.', 'danger')
        abort(403)
    
    # Get lessons and exercises
    lessons = Lesson.query.filter_by(tutorial_id=course_id).order_by(Lesson.order_index).all()
    exercises = Exercise.query.filter_by(tutorial_id=course_id).order_by(Exercise.order_index).all()
    
    # Get enrollments count
    enrollments_count = TutorialEnrollment.query.filter_by(tutorial_id=course_id).count()
    
    return render_template('instructor/course_detail.html',
                         course=course,
                         lessons=lessons,
                         exercises=exercises,
                         enrollments_count=enrollments_count)


@instructor_bp.route('/courses/<int:course_id>/publish', methods=['POST'])
@login_required
@instructor_required
def publish_course(course_id):
    """Publish a course."""
    course = NewTutorial.query.get_or_404(course_id)
    
    if not can_edit_course(current_user, course):
        abort(403)
    
    if course.status == 'published':
        flash('Course is already published.', 'info')
    else:
        course.status = 'published'
        course.published_at = datetime.utcnow()
        db.session.commit()
        flash(f'Course "{course.title}" has been published!', 'success')
    
    return redirect(url_for('instructor.course_detail', course_id=course.id))


@instructor_bp.route('/courses/<int:course_id>/unpublish', methods=['POST'])
@login_required
@instructor_required
def unpublish_course(course_id):
    """Unpublish a course."""
    course = NewTutorial.query.get_or_404(course_id)
    
    if not can_edit_course(current_user, course):
        abort(403)
    
    if course.status == 'draft':
        flash('Course is already unpublished.', 'info')
    else:
        course.status = 'draft'
        db.session.commit()
        flash(f'Course "{course.title}" has been unpublished.', 'success')
    
    return redirect(url_for('instructor.course_detail', course_id=course.id))


@instructor_bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
@instructor_required
def delete_course(course_id):
    """Delete a course (soft delete)."""
    course = NewTutorial.query.get_or_404(course_id)
    
    if not can_edit_course(current_user, course):
        abort(403)
    
    # Check if course has enrollments
    enrollments = TutorialEnrollment.query.filter_by(tutorial_id=course_id).count()
    if enrollments > 0:
        flash('Cannot delete course with active enrollments. Please unpublish instead.', 'danger')
        return redirect(url_for('instructor.course_detail', course_id=course.id))
    
    # Delete course and related content
    Lesson.query.filter_by(tutorial_id=course_id).delete()
    Exercise.query.filter_by(tutorial_id=course_id).delete()
    db.session.delete(course)
    db.session.commit()
    
    flash('Course deleted successfully.', 'success')
    return redirect(url_for('instructor.dashboard'))


# Lesson routes
@instructor_bp.route('/courses/<int:course_id>/lessons/create', methods=['GET', 'POST'])
@login_required
@instructor_required
def create_lesson(course_id):
    """Create a new lesson."""
    course = NewTutorial.query.get_or_404(course_id)
    
    if not can_edit_course(current_user, course):
        abort(403)
    
    form = LessonForm()
    
    # Set default order_index to the next available
    if request.method == 'GET':
        max_order = db.session.query(func.max(Lesson.order_index)).filter_by(tutorial_id=course_id).scalar() or -1
        form.order_index.data = max_order + 1
    
    if form.validate_on_submit():
        slug = slugify(form.title.data)
        
        lesson = Lesson(
            tutorial_id=course_id,
            title=form.title.data,
            slug=slug,
            description=form.description.data,
            section_name=form.section_name.data,
            content_type=form.content_type.data,
            content=form.content.data,
            video_url=form.video_url.data,
            video_duration_seconds=form.video_duration_seconds.data,
            estimated_duration_minutes=form.estimated_duration_minutes.data,
            is_free_preview=form.is_free_preview.data,
            order_index=form.order_index.data
        )
        
        db.session.add(lesson)
        
        # Update course lesson count
        course.total_lessons = Lesson.query.filter_by(tutorial_id=course_id).count() + 1
        
        db.session.commit()
        
        flash(f'Lesson "{lesson.title}" created successfully!', 'success')
        return redirect(url_for('instructor.course_detail', course_id=course_id))
    
    return render_template('instructor/lesson_form.html', form=form, course=course, mode='create')


@instructor_bp.route('/courses/<int:course_id>/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
@instructor_required
def edit_lesson(course_id, lesson_id):
    """Edit a lesson."""
    course = NewTutorial.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    
    if not can_edit_course(current_user, course):
        abort(403)
    
    if lesson.tutorial_id != course_id:
        abort(404)
    
    form = LessonForm(obj=lesson)
    
    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.description = form.description.data
        lesson.section_name = form.section_name.data
        lesson.content_type = form.content_type.data
        lesson.content = form.content.data
        lesson.video_url = form.video_url.data
        lesson.video_duration_seconds = form.video_duration_seconds.data
        lesson.estimated_duration_minutes = form.estimated_duration_minutes.data
        lesson.is_free_preview = form.is_free_preview.data
        lesson.order_index = form.order_index.data
        
        db.session.commit()
        
        flash('Lesson updated successfully!', 'success')
        return redirect(url_for('instructor.course_detail', course_id=course_id))
    
    return render_template('instructor/lesson_form.html', form=form, course=course, lesson=lesson, mode='edit')


@instructor_bp.route('/courses/<int:course_id>/lessons/<int:lesson_id>/delete', methods=['POST'])
@login_required
@instructor_required
def delete_lesson(course_id, lesson_id):
    """Delete a lesson."""
    course = NewTutorial.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    
    if not can_edit_course(current_user, course):
        abort(403)
    
    if lesson.tutorial_id != course_id:
        abort(404)
    
    db.session.delete(lesson)
    
    # Update course lesson count
    course.total_lessons = Lesson.query.filter_by(tutorial_id=course_id).count() - 1
    
    db.session.commit()
    
    flash('Lesson deleted successfully.', 'success')
    return redirect(url_for('instructor.course_detail', course_id=course_id))


# Exercise routes
@instructor_bp.route('/courses/<int:course_id>/exercises/create', methods=['GET', 'POST'])
@login_required
@instructor_required
def create_exercise(course_id):
    """Create a new exercise."""
    course = NewTutorial.query.get_or_404(course_id)
    
    if not can_edit_course(current_user, course):
        abort(403)
    
    form = ExerciseForm()
    
    # Set default order_index
    if request.method == 'GET':
        max_order = db.session.query(func.max(Exercise.order_index)).filter_by(tutorial_id=course_id).scalar() or -1
        form.order_index.data = max_order + 1
        form.exercise_type.data = course.course_type  # Default to course type
    
    if form.validate_on_submit():
        slug = slugify(form.title.data)
        
        exercise = Exercise(
            tutorial_id=course_id,
            title=form.title.data,
            slug=slug,
            description=form.description.data,
            exercise_type=form.exercise_type.data,
            difficulty=form.difficulty.data,
            starter_code=form.starter_code.data,
            solution_code=form.solution_code.data,
            test_cases=form.test_cases.data,
            hints=form.hints.data,
            database_schema=form.database_schema.data,
            sample_data=form.sample_data.data,
            expected_output=form.expected_output.data,
            points=form.points.data,
            order_index=form.order_index.data
        )
        
        db.session.add(exercise)
        db.session.commit()
        
        flash(f'Exercise "{exercise.title}" created successfully!', 'success')
        return redirect(url_for('instructor.course_detail', course_id=course_id))
    
    return render_template('instructor/exercise_form.html', form=form, course=course, mode='create')


@instructor_bp.route('/courses/<int:course_id>/exercises/<int:exercise_id>/edit', methods=['GET', 'POST'])
@login_required
@instructor_required
def edit_exercise(course_id, exercise_id):
    """Edit an exercise."""
    course = NewTutorial.query.get_or_404(course_id)
    exercise = Exercise.query.get_or_404(exercise_id)
    
    if not can_edit_course(current_user, course):
        abort(403)
    
    if exercise.tutorial_id != course_id:
        abort(404)
    
    form = ExerciseForm(obj=exercise)
    
    if form.validate_on_submit():
        exercise.title = form.title.data
        exercise.description = form.description.data
        exercise.exercise_type = form.exercise_type.data
        exercise.difficulty = form.difficulty.data
        exercise.starter_code = form.starter_code.data
        exercise.solution_code = form.solution_code.data
        exercise.test_cases = form.test_cases.data
        exercise.hints = form.hints.data
        exercise.database_schema = form.database_schema.data
        exercise.sample_data = form.sample_data.data
        exercise.expected_output = form.expected_output.data
        exercise.points = form.points.data
        exercise.order_index = form.order_index.data
        
        db.session.commit()
        
        flash('Exercise updated successfully!', 'success')
        return redirect(url_for('instructor.course_detail', course_id=course_id))
    
    return render_template('instructor/exercise_form.html', form=form, course=course, exercise=exercise, mode='edit')


@instructor_bp.route('/courses/<int:course_id>/exercises/<int:exercise_id>/delete', methods=['POST'])
@login_required
@instructor_required
def delete_exercise(course_id, exercise_id):
    """Delete an exercise."""
    course = NewTutorial.query.get_or_404(course_id)
    exercise = Exercise.query.get_or_404(exercise_id)
    
    if not can_edit_course(current_user, course):
        abort(403)
    
    if exercise.tutorial_id != course_id:
        abort(404)
    
    db.session.delete(exercise)
    db.session.commit()
    
    flash('Exercise deleted successfully.', 'success')
    return redirect(url_for('instructor.course_detail', course_id=course_id))


# Image Upload for Markdown Editor
@instructor_bp.route('/upload-image', methods=['POST'])
@login_required
@instructor_required
def upload_image():
    """Upload image for markdown editor."""
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'File type not allowed. Use PNG, JPG, JPEG, GIF, or WEBP'}), 400
    
    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{current_user.id}_{filename}"
        
        # Create upload directory if it doesn't exist
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        filepath = os.path.join(upload_folder, filename)
        
        # Save and optimize image
        file.save(filepath)
        
        # Optimize image with Pillow
        with Image.open(filepath) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if too large (max 1920px width)
            max_width = 1920
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save optimized
            img.save(filepath, quality=85, optimize=True)
        
        # Return URL for markdown
        url = url_for('static', filename=f'uploads/{filename}')
        
        return jsonify({
            'success': True,
            'url': url,
            'filename': filename
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@instructor_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    return send_from_directory(upload_folder, filename)

