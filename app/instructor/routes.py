"""Routes for instructor panel."""
from flask import render_template, redirect, url_for, flash, request, abort, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename
from app.instructor import instructor_bp
from app.instructor.decorators import instructor_required, can_edit_course
from app.instructor.forms import CourseForm, LessonForm, ExerciseForm, QuizForm, QuizQuestionForm, TestCaseForm
from app.models import NewTutorial, Lesson, Exercise, TutorialEnrollment, Quiz, QuizQuestion, db
from datetime import datetime
import re
import os
import json
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
    quizzes = Quiz.query.filter_by(tutorial_id=course_id).order_by(Quiz.order_index).all()
    
    # Get enrollments count
    enrollments_count = TutorialEnrollment.query.filter_by(tutorial_id=course_id).count()
    
    return render_template('instructor/course_detail.html',
                         course=course,
                         lessons=lessons,
                         exercises=exercises,
                         quizzes=quizzes,
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
    
    # Populate lesson choices
    lessons = Lesson.query.filter_by(tutorial_id=course_id).order_by(Lesson.order_index).all()
    form.lesson_id.choices = [(0, '-- No Lesson (General Exercise) --')] + [(l.id, l.title) for l in lessons]
    
    # Set default order_index
    if request.method == 'GET':
        max_order = db.session.query(func.max(Exercise.order_index)).filter_by(tutorial_id=course_id).scalar() or -1
        form.order_index.data = max_order + 1
        form.exercise_type.data = course.course_type  # Default to course type
    
    if form.validate_on_submit():
        slug = slugify(form.title.data)
        
        exercise = Exercise(
            tutorial_id=course_id,
            lesson_id=form.lesson_id.data if form.lesson_id.data != 0 else None,
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
    
    # Populate lesson choices first
    lessons = Lesson.query.filter_by(tutorial_id=course_id).order_by(Lesson.order_index).all()
    
    # Initialize form
    form = ExerciseForm(obj=exercise)
    
    # Set lesson choices
    form.lesson_id.choices = [(0, '-- No Lesson (General Exercise) --')] + [(l.id, l.title) for l in lessons]
    
    # Set current lesson_id for GET requests
    if request.method == 'GET':
        form.lesson_id.data = exercise.lesson_id if exercise.lesson_id else 0
    
    if form.validate_on_submit():
        exercise.title = form.title.data
        exercise.lesson_id = form.lesson_id.data if form.lesson_id.data != 0 else None
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


@instructor_bp.route('/courses/<int:course_id>/exercises/test', methods=['POST'])
@login_required
@instructor_required
def test_exercise(course_id):
    """Test exercise solution code against test cases in real-time."""
    try:
        course = NewTutorial.query.get_or_404(course_id)
        
        if not can_edit_course(current_user, course):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'})
            
        solution_code = data.get('solution_code', '')
        test_cases_str = data.get('test_cases', '')
        exercise_type = data.get('exercise_type', 'python')
        
        # Validate inputs
        if not solution_code or not solution_code.strip():
            return jsonify({'success': False, 'error': 'Solution code is required'})
        
        if not test_cases_str or not test_cases_str.strip():
            return jsonify({'success': False, 'error': 'Test cases are required'})
        
        # Parse test cases
        try:
            test_cases = json.loads(test_cases_str)
            if not isinstance(test_cases, list):
                return jsonify({'success': False, 'error': 'Test cases must be a JSON array'})
        except json.JSONDecodeError as e:
            return jsonify({'success': False, 'error': f'Invalid JSON in test cases: {str(e)}'})
        
        # Execute code based on type
        if exercise_type == 'python':
            from app.python_practice.validators import validate_python_code
            from app.python_practice.executor import execute_python_code
            
            # Validate code
            is_valid, error_msg = validate_python_code(solution_code)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': error_msg,
                    'validation_failed': True
                })
            
            # Execute code with test cases
            result = execute_python_code(solution_code, test_cases, timeout=10)
            
            return jsonify({
                'success': True,
                'result': {
                    'status': result.get('status'),
                    'output': result.get('output', ''),
                    'error': result.get('error', ''),
                    'test_results': result.get('test_results', []),
                    'tests_passed': result.get('tests_passed', 0),
                    'tests_failed': result.get('tests_failed', 0),
                    'execution_time_ms': result.get('execution_time_ms', 0),
                    'total_tests': len(test_cases)
                }
            })
        
        elif exercise_type == 'sql':
            # TODO: Add SQL testing support
            return jsonify({
                'success': False,
                'error': 'SQL testing is not yet implemented'
            })
        
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported exercise type: {exercise_type}'
            })
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in test_exercise: {error_details}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        })


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


# Quiz routes
@instructor_bp.route('/courses/<int:course_id>/quizzes/create', methods=['GET', 'POST'])
@login_required
@instructor_required
def create_quiz(course_id):
    """Create a new quiz."""
    course = NewTutorial.query.get_or_404(course_id)
    
    if not can_edit_course(current_user, course):
        abort(403)
    
    form = QuizForm()
    
    # Populate lesson choices
    lessons = Lesson.query.filter_by(tutorial_id=course_id).order_by(Lesson.order_index).all()
    form.lesson_id.choices = [(l.id, l.title) for l in lessons]
    
    if not lessons:
        flash('You must create at least one lesson before adding a quiz.', 'warning')
        return redirect(url_for('instructor.course_detail', course_id=course_id))
    
    if form.validate_on_submit():
        # Create slug from title
        slug = slugify(form.title.data)
        
        # Get next order_index
        max_order = db.session.query(func.max(Quiz.order_index)).filter_by(
            tutorial_id=course_id
        ).scalar() or -1
        
        quiz = Quiz(
            tutorial_id=course_id,
            lesson_id=form.lesson_id.data,
            title=form.title.data,
            description=form.description.data,
            passing_score=form.passing_score.data,
            time_limit_minutes=form.time_limit_minutes.data if form.time_limit_minutes.data and form.time_limit_minutes.data > 0 else None,
            max_attempts=form.max_attempts.data,
            shuffle_questions=form.shuffle_questions.data,
            shuffle_options=form.shuffle_options.data,
            show_correct_answers=form.show_correct_answers.data,
            is_required=form.is_required.data,
            order_index=form.order_index.data if form.order_index.data is not None else max_order + 1
        )
        
        db.session.add(quiz)
        db.session.commit()
        
        flash(f'Quiz "{quiz.title}" created successfully! Now add questions.', 'success')
        return redirect(url_for('instructor.edit_quiz', course_id=course_id, quiz_id=quiz.id))
    
    return render_template('instructor/quiz_form.html', form=form, course=course, mode='create')


@instructor_bp.route('/courses/<int:course_id>/quizzes/<int:quiz_id>/edit', methods=['GET', 'POST'])
@login_required
@instructor_required
def edit_quiz(course_id, quiz_id):
    """Edit a quiz."""
    course = NewTutorial.query.get_or_404(course_id)
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if not can_edit_course(current_user, course):
        abort(403)
    
    if quiz.tutorial_id != course_id:
        abort(404)
    
    form = QuizForm(obj=quiz)
    
    # Populate lesson choices
    lessons = Lesson.query.filter_by(tutorial_id=course_id).order_by(Lesson.order_index).all()
    form.lesson_id.choices = [(l.id, l.title) for l in lessons]
    
    # Get quiz questions
    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).order_by(QuizQuestion.order_index).all()
    
    if request.method == 'GET':
        form.lesson_id.data = quiz.lesson_id
        form.time_limit_minutes.data = quiz.time_limit_minutes or 0
    
    if form.validate_on_submit():
        quiz.title = form.title.data
        quiz.lesson_id = form.lesson_id.data
        quiz.description = form.description.data
        quiz.passing_score = form.passing_score.data
        quiz.time_limit_minutes = form.time_limit_minutes.data if form.time_limit_minutes.data and form.time_limit_minutes.data > 0 else None
        quiz.max_attempts = form.max_attempts.data
        quiz.shuffle_questions = form.shuffle_questions.data
        quiz.shuffle_options = form.shuffle_options.data
        quiz.show_correct_answers = form.show_correct_answers.data
        quiz.is_required = form.is_required.data
        quiz.order_index = form.order_index.data
        
        db.session.commit()
        
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('instructor.edit_quiz', course_id=course_id, quiz_id=quiz_id))
    
    return render_template('instructor/quiz_form.html', form=form, course=course, quiz=quiz, 
                         questions=questions, mode='edit')


@instructor_bp.route('/courses/<int:course_id>/quizzes/<int:quiz_id>/delete', methods=['POST'])
@login_required
@instructor_required
def delete_quiz(course_id, quiz_id):
    """Delete a quiz."""
    course = NewTutorial.query.get_or_404(course_id)
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if not can_edit_course(current_user, course):
        abort(403)
    
    if quiz.tutorial_id != course_id:
        abort(404)
    
    db.session.delete(quiz)
    db.session.commit()
    
    flash('Quiz deleted successfully.', 'success')
    return redirect(url_for('instructor.course_detail', course_id=course_id))


# Quiz Question routes
@instructor_bp.route('/courses/<int:course_id>/quizzes/<int:quiz_id>/questions/create', methods=['GET', 'POST'])
@login_required
@instructor_required
def create_quiz_question(course_id, quiz_id):
    """Create a new quiz question."""
    course = NewTutorial.query.get_or_404(course_id)
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if not can_edit_course(current_user, course):
        abort(403)
    
    if quiz.tutorial_id != course_id:
        abort(404)
    
    form = QuizQuestionForm()
    
    if form.validate_on_submit():
        # Get next order_index
        max_order = db.session.query(func.max(QuizQuestion.order_index)).filter_by(
            quiz_id=quiz_id
        ).scalar() or -1
        
        # Prepare options JSON for multiple choice
        options = None
        if form.question_type.data == 'multiple_choice':
            options_list = []
            if form.option_a.data:
                options_list.append({'id': 'a', 'text': form.option_a.data})
            if form.option_b.data:
                options_list.append({'id': 'b', 'text': form.option_b.data})
            if form.option_c.data:
                options_list.append({'id': 'c', 'text': form.option_c.data})
            if form.option_d.data:
                options_list.append({'id': 'd', 'text': form.option_d.data})
            options = json.dumps(options_list)
        
        question = QuizQuestion(
            quiz_id=quiz_id,
            question_text=form.question_text.data,
            question_type=form.question_type.data,
            options=options,
            correct_answer=form.correct_answer.data,
            explanation=form.explanation.data,
            points=form.points.data,
            order_index=form.order_index.data if form.order_index.data is not None else max_order + 1
        )
        
        db.session.add(question)
        db.session.commit()
        
        flash('Question added successfully!', 'success')
        return redirect(url_for('instructor.edit_quiz', course_id=course_id, quiz_id=quiz_id))
    
    return render_template('instructor/quiz_question_form.html', form=form, course=course, 
                         quiz=quiz, mode='create')


@instructor_bp.route('/courses/<int:course_id>/quizzes/<int:quiz_id>/questions/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
@instructor_required
def edit_quiz_question(course_id, quiz_id, question_id):
    """Edit a quiz question."""
    course = NewTutorial.query.get_or_404(course_id)
    quiz = Quiz.query.get_or_404(quiz_id)
    question = QuizQuestion.query.get_or_404(question_id)
    
    if not can_edit_course(current_user, course):
        abort(403)
    
    if quiz.tutorial_id != course_id or question.quiz_id != quiz_id:
        abort(404)
    
    form = QuizQuestionForm(obj=question)
    
    if request.method == 'GET':
        # Pre-populate multiple choice options
        if question.options:
            try:
                options_list = json.loads(question.options)
                for option in options_list:
                    opt_id = option.get('id', '').lower()
                    opt_text = option.get('text', '')
                    if opt_id == 'a':
                        form.option_a.data = opt_text
                    elif opt_id == 'b':
                        form.option_b.data = opt_text
                    elif opt_id == 'c':
                        form.option_c.data = opt_text
                    elif opt_id == 'd':
                        form.option_d.data = opt_text
            except json.JSONDecodeError:
                pass
    
    if form.validate_on_submit():
        question.question_text = form.question_text.data
        question.question_type = form.question_type.data
        
        # Update options JSON for multiple choice
        if form.question_type.data == 'multiple_choice':
            options_list = []
            if form.option_a.data:
                options_list.append({'id': 'a', 'text': form.option_a.data})
            if form.option_b.data:
                options_list.append({'id': 'b', 'text': form.option_b.data})
            if form.option_c.data:
                options_list.append({'id': 'c', 'text': form.option_c.data})
            if form.option_d.data:
                options_list.append({'id': 'd', 'text': form.option_d.data})
            question.options = json.dumps(options_list)
        else:
            question.options = None
        
        question.correct_answer = form.correct_answer.data
        question.explanation = form.explanation.data
        question.points = form.points.data
        question.order_index = form.order_index.data
        
        db.session.commit()
        
        flash('Question updated successfully!', 'success')
        return redirect(url_for('instructor.edit_quiz', course_id=course_id, quiz_id=quiz_id))
    
    return render_template('instructor/quiz_question_form.html', form=form, course=course, 
                         quiz=quiz, question=question, mode='edit')


@instructor_bp.route('/courses/<int:course_id>/quizzes/<int:quiz_id>/questions/<int:question_id>/delete', methods=['POST'])
@login_required
@instructor_required
def delete_quiz_question(course_id, quiz_id, question_id):
    """Delete a quiz question."""
    course = NewTutorial.query.get_or_404(course_id)
    quiz = Quiz.query.get_or_404(quiz_id)
    question = QuizQuestion.query.get_or_404(question_id)
    
    if not can_edit_course(current_user, course):
        abort(403)
    
    if quiz.tutorial_id != course_id or question.quiz_id != quiz_id:
        abort(404)
    
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully.', 'success')
    return redirect(url_for('instructor.edit_quiz', course_id=course_id, quiz_id=quiz_id))


# Test Case Management API endpoints
@instructor_bp.route('/api/exercises/<int:exercise_id>/test-cases', methods=['GET'])
@login_required
@instructor_required
def get_test_cases(exercise_id):
    """Get test cases for an exercise (API endpoint)."""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check permissions
    if not can_edit_course(current_user, exercise.tutorial):
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        test_cases = json.loads(exercise.test_cases) if exercise.test_cases else []
        return jsonify({'success': True, 'test_cases': test_cases})
    except json.JSONDecodeError:
        return jsonify({'success': False, 'error': 'Invalid test cases format'}), 400


@instructor_bp.route('/api/exercises/<int:exercise_id>/test-cases', methods=['POST'])
@login_required
@instructor_required
def add_test_case(exercise_id):
    """Add a test case to an exercise (API endpoint)."""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check permissions
    if not can_edit_course(current_user, exercise.tutorial):
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    
    if not data or not all(k in data for k in ['description', 'input', 'expected_output']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Load existing test cases
        test_cases = json.loads(exercise.test_cases) if exercise.test_cases else []
        
        # Add new test case
        new_test_case = {
            'id': len(test_cases) + 1,
            'description': data['description'],
            'input': data['input'],
            'expected_output': data['expected_output'],
            'is_hidden': data.get('is_hidden', False),
            'points': data.get('points', 1)
        }
        
        test_cases.append(new_test_case)
        
        # Save back to exercise
        exercise.test_cases = json.dumps(test_cases)
        db.session.commit()
        
        return jsonify({'success': True, 'test_case': new_test_case})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@instructor_bp.route('/api/exercises/<int:exercise_id>/test-cases/<int:test_case_id>', methods=['DELETE'])
@login_required
@instructor_required
def delete_test_case(exercise_id, test_case_id):
    """Delete a test case from an exercise (API endpoint)."""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check permissions
    if not can_edit_course(current_user, exercise.tutorial):
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        # Load existing test cases
        test_cases = json.loads(exercise.test_cases) if exercise.test_cases else []
        
        # Remove test case by id
        test_cases = [tc for tc in test_cases if tc.get('id') != test_case_id]
        
        # Re-index
        for idx, tc in enumerate(test_cases):
            tc['id'] = idx + 1
        
        # Save back to exercise
        exercise.test_cases = json.dumps(test_cases)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@instructor_bp.route('/api/exercises/<int:exercise_id>/test-cases/<int:test_case_id>', methods=['PUT'])
@login_required
@instructor_required
def update_test_case(exercise_id, test_case_id):
    """Update a test case in an exercise (API endpoint)."""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check permissions
    if not can_edit_course(current_user, exercise.tutorial):
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    
    try:
        # Load existing test cases
        test_cases = json.loads(exercise.test_cases) if exercise.test_cases else []
        
        # Find and update test case
        for tc in test_cases:
            if tc.get('id') == test_case_id:
                tc['description'] = data.get('description', tc.get('description'))
                tc['input'] = data.get('input', tc.get('input'))
                tc['expected_output'] = data.get('expected_output', tc.get('expected_output'))
                tc['is_hidden'] = data.get('is_hidden', tc.get('is_hidden', False))
                tc['points'] = data.get('points', tc.get('points', 1))
                break
        
        # Save back to exercise
        exercise.test_cases = json.dumps(test_cases)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
