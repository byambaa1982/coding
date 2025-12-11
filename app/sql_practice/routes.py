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
from app.models import Exercise, ExerciseSubmission
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
    
    # Check if user is enrolled
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        tutorial_id=exercise.tutorial_id
    ).first()
    
    if not enrollment:
        return redirect(url_for('catalog.tutorial_detail', tutorial_id=exercise.tutorial_id))
    
    # Get previous submissions
    submissions = ExerciseSubmission.query.filter_by(
        user_id=current_user.id,
        exercise_id=exercise_id
    ).order_by(ExerciseSubmission.submitted_at.desc()).limit(10).all()
    
    # Generate session ID
    if 'sql_session_id' not in session:
        session['sql_session_id'] = str(uuid.uuid4())
    
    form = SQLExerciseSubmissionForm()
    
    return render_template(
        'sql_practice/exercise.html',
        exercise=exercise,
        submissions=submissions,
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
