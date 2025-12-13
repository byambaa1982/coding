"""
SQL Practice Routes
Handles SQL practice editor, exercises, and challenges
"""
from flask import render_template, request, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
import uuid
import logging
from datetime import datetime

from app.sql_practice import sql_practice_bp
from app.sql_practice.forms import SQLQueryForm, SQLExerciseSubmissionForm
from app.sql_practice.executor import SQLExecutor
from app.sql_practice.validators import SQLValidator
from app.models import Exercise, ExerciseSubmission, TutorialEnrollment, NewTutorial, Lesson
from app.extensions import db

logger = logging.getLogger(__name__)


@sql_practice_bp.route('/editor')
@login_required
def editor():
    """SQL practice editor"""
    form = SQLQueryForm()
    
    # Generate session ID if not exists
    if 'sql_session_id' not in session:
        session['sql_session_id'] = str(uuid.uuid4())
    
    return render_template('sql_practice/editor.html', form=form)


@sql_practice_bp.route('/execute', methods=['POST'])
@login_required
def execute_query():
    """Execute SQL query"""
    form = SQLQueryForm()
    
    if not form.validate_on_submit():
        return jsonify({
            'success': False,
            'errors': [str(e) for e in form.errors.values()]
        }), 400
    
    query = form.query.data
    
    # Get or create session ID
    if 'sql_session_id' not in session:
        session['sql_session_id'] = str(uuid.uuid4())
    
    session_id = session['sql_session_id']
    
    # Create executor
    executor = SQLExecutor(current_user.id, session_id)
    
    # Execute query (read-only by default for safety)
    result = executor.execute(query, read_only=True)
    
    return jsonify(result)


@sql_practice_bp.route('/execute-dml', methods=['POST'])
@login_required
def execute_dml_query():
    """Execute DML query (INSERT, UPDATE, DELETE) - for specific exercises"""
    form = SQLQueryForm()
    
    if not form.validate_on_submit():
        return jsonify({
            'success': False,
            'errors': [str(e) for e in form.errors.values()]
        }), 400
    
    query = form.query.data
    exercise_id = form.exercise_id.data
    
    # Verify user has access to this exercise
    if exercise_id:
        exercise = Exercise.query.get_or_404(exercise_id)
        # Check if user is enrolled in the tutorial
        enrollment = Enrollment.query.filter_by(
            user_id=current_user.id,
            tutorial_id=exercise.tutorial_id
        ).first()
        
        if not enrollment:
            return jsonify({
                'success': False,
                'errors': ['You must be enrolled in this course to complete exercises']
            }), 403
    
    # Get session ID
    if 'sql_session_id' not in session:
        session['sql_session_id'] = str(uuid.uuid4())
    
    session_id = session['sql_session_id']
    
    # Create executor
    executor = SQLExecutor(current_user.id, session_id)
    
    # Execute query with DML allowed
    result = executor.execute(query, read_only=False, allow_delete=True)
    
    return jsonify(result)


@sql_practice_bp.route('/schema')
@login_required
def get_schema():
    """Get database schema information"""
    try:
        if 'sql_session_id' not in session:
            session['sql_session_id'] = str(uuid.uuid4())
        
        session_id = session['sql_session_id']
        logger.info(f"Getting schema for user {current_user.id}, session {session_id}")
        
        executor = SQLExecutor(current_user.id, session_id)
        schema_info = executor.get_schema_info()
        
        logger.info(f"Schema retrieved successfully for user {current_user.id}")
        return jsonify(schema_info)
        
    except Exception as e:
        logger.error(f"Error getting schema: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@sql_practice_bp.route('/preview/<table_name>')
@login_required
def preview_table(table_name):
    """Preview table data"""
    limit = request.args.get('limit', 10, type=int)
    
    if 'sql_session_id' not in session:
        session['sql_session_id'] = str(uuid.uuid4())
    
    session_id = session['sql_session_id']
    executor = SQLExecutor(current_user.id, session_id)
    
    preview_data = executor.preview_table(table_name, limit)
    
    return jsonify(preview_data)


@sql_practice_bp.route('/reset-database', methods=['POST'])
@login_required
def reset_database():
    """Reset database to initial state"""
    if 'sql_session_id' not in session:
        return jsonify({
            'success': False,
            'error': 'No active session'
        }), 400
    
    session_id = session['sql_session_id']
    executor = SQLExecutor(current_user.id, session_id)
    
    result = executor.reset_database()
    
    return jsonify(result)


@sql_practice_bp.route('/exercise/<int:exercise_id>')
@login_required
def exercise(exercise_id):
    """SQL exercise page"""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Ensure this is a SQL exercise
    if exercise.exercise_type != 'sql':
        from flask import abort
        abort(404)
    
    # Check enrollment if exercise is part of a tutorial
    enrollment = None
    if exercise.tutorial_id:
        enrollment = TutorialEnrollment.query.filter_by(
            user_id=current_user.id,
            tutorial_id=exercise.tutorial_id,
            status='active'
        ).first()
        
        if not enrollment and not exercise.tutorial.is_free:
            from flask import flash
            flash('You need to enroll in this course first.', 'warning')
            return redirect(url_for('catalog.course_detail', slug=exercise.tutorial.slug))
    
    # Get previous submissions
    submissions = ExerciseSubmission.query.filter_by(
        user_id=current_user.id,
        exercise_id=exercise_id
    ).order_by(ExerciseSubmission.submitted_at.desc()).limit(10).all()
    
    # Get all exercises in the same lesson (subtopic)
    lesson_exercises = []
    next_exercise = None
    prev_exercise = None
    
    if exercise.lesson_id:
        lesson_exercises = Exercise.query.filter_by(
            lesson_id=exercise.lesson_id,
            exercise_type='sql'
        ).order_by(Exercise.order_index).all()
        
        # Find current position and adjacent exercises
        for idx, ex in enumerate(lesson_exercises):
            if ex.id == exercise_id:
                if idx > 0:
                    prev_exercise = lesson_exercises[idx - 1]
                if idx < len(lesson_exercises) - 1:
                    next_exercise = lesson_exercises[idx + 1]
    
    # Generate session ID
    if 'sql_session_id' not in session:
        session['sql_session_id'] = str(uuid.uuid4())
    
    form = SQLExerciseSubmissionForm()
    
    return render_template(
        'sql_practice/exercise.html',
        exercise=exercise,
        enrollment=enrollment,
        submissions=submissions,
        next_exercise=next_exercise,
        prev_exercise=prev_exercise,
        form=form
    )


@sql_practice_bp.route('/submit-exercise', methods=['POST'])
@login_required
def submit_exercise():
    """Submit SQL exercise solution"""
    form = SQLExerciseSubmissionForm()
    
    if not form.validate_on_submit():
        return jsonify({
            'success': False,
            'errors': [str(e) for e in form.errors.values()]
        }), 400
    
    exercise_id = form.exercise_id.data
    query = form.query.data
    
    # Get exercise
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check enrollment
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        tutorial_id=exercise.tutorial_id
    ).first()
    
    if not enrollment:
        return jsonify({
            'success': False,
            'errors': ['You must be enrolled in this course']
        }), 403
    
    # Get session ID
    if 'sql_session_id' not in session:
        session['sql_session_id'] = str(uuid.uuid4())
    
    session_id = session['sql_session_id']
    
    # Create executor
    executor = SQLExecutor(current_user.id, session_id)
    
    # Validate solution
    expected_result = exercise.expected_output or {}
    validation_result = executor.validate_exercise_solution(query, expected_result)
    
    # Create submission record
    submission = ExerciseSubmission(
        user_id=current_user.id,
        exercise_id=exercise_id,
        submitted_code=query,
        status='passed' if validation_result['passed'] else 'failed',
        output=validation_result.get('execution_result', {}).get('results', []),
        error_message=validation_result.get('feedback') if not validation_result['passed'] else None,
        execution_time=validation_result.get('execution_result', {}).get('execution_time', 0)
    )
    
    db.session.add(submission)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'passed': validation_result['passed'],
        'feedback': validation_result['feedback'],
        'submission_id': submission.id,
        'execution_result': validation_result.get('execution_result')
    })


@sql_practice_bp.route('/challenges')
@login_required
def challenges():
    """SQL challenges page"""
    # Get all SQL exercises across all enrolled courses
    enrollments = Enrollment.query.filter_by(user_id=current_user.id).all()
    tutorial_ids = [e.tutorial_id for e in enrollments]
    
    # Get SQL tutorials
    sql_tutorials = Tutorial.query.filter(
        Tutorial.id.in_(tutorial_ids),
        Tutorial.category == 'sql'
    ).all()
    
    # Get exercises
    exercises = Exercise.query.filter(
        Exercise.tutorial_id.in_([t.id for t in sql_tutorials]),
        Exercise.exercise_type == 'sql'
    ).order_by(Exercise.difficulty.asc()).all()
    
    # Get user's submissions
    submissions = ExerciseSubmission.query.filter_by(
        user_id=current_user.id
    ).filter(
        ExerciseSubmission.exercise_id.in_([e.id for e in exercises])
    ).all()
    
    # Create submission map
    submission_map = {}
    for sub in submissions:
        if sub.exercise_id not in submission_map or sub.status == 'passed':
            submission_map[sub.exercise_id] = sub
    
    return render_template(
        'sql_practice/challenges.html',
        exercises=exercises,
        submission_map=submission_map
    )


@sql_practice_bp.route('/schema-viewer')
@login_required
def schema_viewer():
    """Database schema visualization"""
    if 'sql_session_id' not in session:
        session['sql_session_id'] = str(uuid.uuid4())
    
    return render_template('sql_practice/schema_viewer.html')


@sql_practice_bp.route('/validate-syntax', methods=['POST'])
@login_required
def validate_syntax():
    """Validate SQL syntax without execution"""
    data = request.get_json()
    query = data.get('query', '')
    
    validator = SQLValidator()
    result = validator.validate_query(query, read_only=True)
    
    return jsonify(result)


@sql_practice_bp.route('/course/<int:enrollment_id>/subtopics')
@login_required
def course_subtopics(enrollment_id):
    """Display all subtopics (lessons) for a SQL course with progress."""
    enrollment = TutorialEnrollment.query.filter_by(
        id=enrollment_id,
        user_id=current_user.id,
        status='active'
    ).first_or_404()
    
    tutorial = enrollment.tutorial
    
    # Get all lessons for this tutorial (these are the subtopics)
    lessons = Lesson.query.filter_by(
        tutorial_id=tutorial.id
    ).order_by(Lesson.order_index).all()
    
    # Build lesson progress data
    lessons_with_progress = []
    for lesson in lessons:
        # Get all exercises for this lesson
        exercises = Exercise.query.filter_by(
            lesson_id=lesson.id,
            exercise_type='sql'
        ).all()
        
        total_exercises = len(exercises)
        if total_exercises == 0:
            continue  # Skip lessons without exercises
        
        # Count completed exercises
        completed_exercises = 0
        for exercise in exercises:
            has_solved = ExerciseSubmission.query.filter_by(
                user_id=current_user.id,
                exercise_id=exercise.id,
                status='passed'
            ).first() is not None
            if has_solved:
                completed_exercises += 1
        
        # Calculate progress percentage
        progress_percentage = (completed_exercises / total_exercises * 100) if total_exercises > 0 else 0
        is_completed = completed_exercises == total_exercises
        
        lessons_with_progress.append({
            'lesson': lesson,
            'total_exercises': total_exercises,
            'completed_exercises': completed_exercises,
            'progress_percentage': progress_percentage,
            'is_completed': is_completed
        })
    
    return render_template('sql_practice/course_subtopics.html',
                         enrollment=enrollment,
                         tutorial=tutorial,
                         lessons=lessons_with_progress)


@sql_practice_bp.route('/lesson/<int:lesson_id>/exercises')
@login_required
def lesson_exercises(lesson_id):
    """Display all SQL exercises for a lesson."""
    lesson = Lesson.query.get_or_404(lesson_id)
    tutorial = lesson.tutorial
    
    # Check enrollment
    enrollment = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        tutorial_id=tutorial.id,
        status='active'
    ).first()
    
    if not enrollment:
        from flask import flash
        flash('You need to enroll in this course first.', 'warning')
        return redirect(url_for('catalog.course_detail', slug=tutorial.slug))
    
    # Get SQL exercises for this lesson
    exercises = Exercise.query.filter_by(
        lesson_id=lesson_id,
        exercise_type='sql'
    ).order_by(Exercise.order_index).all()
    
    # Get user's progress for each exercise
    exercises_with_progress = []
    for exercise in exercises:
        best_submission = ExerciseSubmission.query.filter_by(
            user_id=current_user.id,
            exercise_id=exercise.id
        ).order_by(ExerciseSubmission.score.desc()).first()
        
        has_solved = ExerciseSubmission.query.filter_by(
            user_id=current_user.id,
            exercise_id=exercise.id,
            status='passed'
        ).first() is not None
        
        exercises_with_progress.append({
            'exercise': exercise,
            'best_score': float(best_submission.score) if best_submission else 0,
            'has_solved': has_solved,
            'attempt_count': ExerciseSubmission.query.filter_by(
                user_id=current_user.id,
                exercise_id=exercise.id
            ).count()
        })
    
    return render_template('sql_practice/lesson_exercises.html',
                         lesson=lesson,
                         tutorial=tutorial,
                         enrollment=enrollment,
                         exercises=exercises_with_progress)
