# app/python_practice/routes.py
"""Routes for Python code practice and execution."""

import json
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.python_practice import python_practice_bp
from app.extensions import db
from app.models import (
    Exercise, ExerciseSubmission, TutorialEnrollment, NewTutorial, Lesson
)
from app.python_practice.executor import execute_python_code
from app.python_practice.validators import validate_python_code, check_rate_limit
from app.python_practice.forms import CodeSubmissionForm


@python_practice_bp.route('/exercise/<int:exercise_id>')
@login_required
def view_exercise(exercise_id):
    """Display Python exercise with code editor."""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Ensure this is a Python exercise
    if exercise.exercise_type != 'python':
        abort(404)
    
    # Check enrollment if exercise is part of a tutorial
    if exercise.tutorial_id:
        enrollment = TutorialEnrollment.query.filter_by(
            user_id=current_user.id,
            tutorial_id=exercise.tutorial_id,
            status='active'
        ).first()
        
        if not enrollment and not exercise.tutorial.is_free:
            flash('You need to enroll in this course first.', 'warning')
            return redirect(url_for('catalog.course_detail', slug=exercise.tutorial.slug))
    else:
        enrollment = None
    
    # Get user's previous submissions for this exercise
    previous_submissions = ExerciseSubmission.query.filter_by(
        user_id=current_user.id,
        exercise_id=exercise_id
    ).order_by(ExerciseSubmission.submitted_at.desc()).limit(10).all()
    
    # Parse hints from JSON
    hints = []
    if exercise.hints:
        try:
            hints = json.loads(exercise.hints)
        except json.JSONDecodeError:
            hints = []
    
    # Check if user has already solved this exercise
    has_solved = ExerciseSubmission.query.filter_by(
        user_id=current_user.id,
        exercise_id=exercise_id,
        status='passed'
    ).first() is not None
    
    return render_template('python_practice/exercise.html',
                         exercise=exercise,
                         enrollment=enrollment,
                         previous_submissions=previous_submissions,
                         hints=hints,
                         has_solved=has_solved,
                         starter_code=exercise.starter_code or '# Write your code here\n')


@python_practice_bp.route('/exercise/<int:exercise_id>/submit', methods=['POST'])
@login_required
def submit_code(exercise_id):
    """Submit Python code for execution and validation."""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Ensure this is a Python exercise
    if exercise.exercise_type != 'python':
        return jsonify({'error': 'Invalid exercise type'}), 400
    
    # Check rate limiting
    rate_limit_ok, rate_limit_msg = check_rate_limit(current_user.id)
    if not rate_limit_ok:
        return jsonify({'error': rate_limit_msg}), 429
    
    # Get submitted code
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({'error': 'No code provided'}), 400
    
    submitted_code = data.get('code', '')
    
    # Validate code for security
    is_valid, validation_msg = validate_python_code(submitted_code)
    if not is_valid:
        return jsonify({
            'status': 'error',
            'error': validation_msg,
            'is_security_violation': True
        }), 400
    
    # Get enrollment (if applicable)
    enrollment = None
    if exercise.tutorial_id:
        enrollment = TutorialEnrollment.query.filter_by(
            user_id=current_user.id,
            tutorial_id=exercise.tutorial_id,
            status='active'
        ).first()
    
    # Create submission record
    submission = ExerciseSubmission(
        user_id=current_user.id,
        exercise_id=exercise_id,
        enrollment_id=enrollment.id if enrollment else None,
        submitted_code=submitted_code,
        language='python',
        ip_address=request.remote_addr
    )
    db.session.add(submission)
    db.session.commit()
    
    # Parse test cases
    test_cases = []
    if exercise.test_cases:
        try:
            test_cases = json.loads(exercise.test_cases)
        except json.JSONDecodeError:
            test_cases = []
    
    # Execute code with test cases
    execution_result = execute_python_code(
        code=submitted_code,
        test_cases=test_cases,
        timeout=30
    )
    
    # Update submission with results
    submission.status = execution_result['status']
    submission.output = execution_result.get('output', '')
    submission.error_message = execution_result.get('error', '')
    submission.test_results = json.dumps(execution_result.get('test_results', []))
    submission.tests_passed = execution_result.get('tests_passed', 0)
    submission.tests_failed = execution_result.get('tests_failed', 0)
    submission.execution_time_ms = execution_result.get('execution_time_ms', 0)
    submission.executed_at = datetime.utcnow()
    
    # Calculate score
    total_tests = submission.tests_passed + submission.tests_failed
    if total_tests > 0:
        submission.score = (submission.tests_passed / total_tests) * 100
    else:
        submission.score = 0
    
    # Check if flagged
    if execution_result.get('is_flagged', False):
        submission.is_flagged = True
        submission.flagged_reason = execution_result.get('flagged_reason', 'Suspicious code detected')
    
    db.session.commit()
    
    # Update enrollment progress if passed
    if submission.status == 'passed':
        submission.mark_as_passed()
    
    # Prepare response
    response_data = {
        'status': submission.status,
        'output': submission.output,
        'error': submission.error_message,
        'test_results': execution_result.get('test_results', []),
        'tests_passed': submission.tests_passed,
        'tests_failed': submission.tests_failed,
        'score': float(submission.score),
        'execution_time_ms': submission.execution_time_ms,
        'submission_id': submission.id
    }
    
    return jsonify(response_data)


@python_practice_bp.route('/exercise/<int:exercise_id>/solution')
@login_required
def view_solution(exercise_id):
    """View solution for an exercise (only after multiple attempts)."""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check if user has attempted at least 3 times
    attempt_count = ExerciseSubmission.query.filter_by(
        user_id=current_user.id,
        exercise_id=exercise_id
    ).count()
    
    if attempt_count < 3:
        return jsonify({
            'error': 'You need at least 3 attempts before viewing the solution',
            'attempts': attempt_count,
            'required': 3
        }), 403
    
    if not exercise.solution_code:
        return jsonify({'error': 'No solution available for this exercise'}), 404
    
    return jsonify({
        'solution': exercise.solution_code
    })


@python_practice_bp.route('/exercise/<int:exercise_id>/hints')
@login_required
def get_hints(exercise_id):
    """Get hints for an exercise."""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    hints = []
    if exercise.hints:
        try:
            hints = json.loads(exercise.hints)
        except json.JSONDecodeError:
            hints = []
    
    return jsonify({'hints': hints})


@python_practice_bp.route('/exercise/<int:exercise_id>/submissions')
@login_required
def get_submissions(exercise_id):
    """Get user's submission history for an exercise."""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    submissions = ExerciseSubmission.query.filter_by(
        user_id=current_user.id,
        exercise_id=exercise_id
    ).order_by(ExerciseSubmission.submitted_at.desc()).limit(20).all()
    
    submissions_data = []
    for sub in submissions:
        submissions_data.append({
            'id': sub.id,
            'status': sub.status,
            'score': float(sub.score),
            'tests_passed': sub.tests_passed,
            'tests_failed': sub.tests_failed,
            'execution_time_ms': sub.execution_time_ms,
            'submitted_at': sub.submitted_at.isoformat(),
            'code_preview': sub.submitted_code[:100] + '...' if len(sub.submitted_code) > 100 else sub.submitted_code
        })
    
    return jsonify({'submissions': submissions_data})


@python_practice_bp.route('/lesson/<int:lesson_id>/exercises')
@login_required
def lesson_exercises(lesson_id):
    """Display all Python exercises for a lesson."""
    lesson = Lesson.query.get_or_404(lesson_id)
    tutorial = lesson.tutorial
    
    # Check enrollment
    enrollment = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        tutorial_id=tutorial.id,
        status='active'
    ).first()
    
    if not enrollment:
        flash('You need to enroll in this course first.', 'warning')
        return redirect(url_for('catalog.course_detail', slug=tutorial.slug))
    
    # Get Python exercises for this lesson
    exercises = Exercise.query.filter_by(
        lesson_id=lesson_id,
        exercise_type='python'
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
    
    return render_template('python_practice/lesson_exercises.html',
                         lesson=lesson,
                         tutorial=tutorial,
                         enrollment=enrollment,
                         exercises=exercises_with_progress)
