# app/tasks/execution_tasks.py
"""Celery tasks for code execution."""

import json
from datetime import datetime
from app.celery_app import celery
from app.python_practice.executor import execute_python_code


@celery.task(name='app.tasks.execution_tasks.execute_python_code_async', bind=True)
def execute_python_code_async(self, submission_id, code, test_cases, timeout=30):
    """
    Execute Python code asynchronously.
    
    Args:
        self: Celery task instance
        submission_id: ExerciseSubmission ID
        code: Python code to execute
        test_cases: List of test case dictionaries
        timeout: Execution timeout in seconds
        
    Returns:
        Execution result dictionary
    """
    from app import create_app
    from app.extensions import db
    from app.models import ExerciseSubmission
    
    app = create_app()
    
    with app.app_context():
        try:
            # Get submission
            submission = ExerciseSubmission.query.get(submission_id)
            if not submission:
                return {'error': 'Submission not found'}
            
            # Execute code
            result = execute_python_code(code, test_cases, timeout)
            
            # Update submission
            submission.status = result['status']
            submission.output = result.get('output', '')
            submission.error_message = result.get('error', '')
            submission.test_results = json.dumps(result.get('test_results', []))
            submission.tests_passed = result.get('tests_passed', 0)
            submission.tests_failed = result.get('tests_failed', 0)
            submission.execution_time_ms = result.get('execution_time_ms', 0)
            submission.executed_at = datetime.utcnow()
            
            # Calculate score
            total_tests = submission.tests_passed + submission.tests_failed
            if total_tests > 0:
                submission.score = (submission.tests_passed / total_tests) * 100
            
            db.session.commit()
            
            # Update enrollment if passed
            if submission.status == 'passed':
                submission.mark_as_passed()
            
            return result
            
        except Exception as e:
            # Log error
            print(f'Error in execute_python_code_async: {str(e)}')
            
            # Update submission with error
            if submission:
                submission.status = 'error'
                submission.error_message = f'Execution error: {str(e)}'
                submission.executed_at = datetime.utcnow()
                db.session.commit()
            
            return {'error': str(e)}


@celery.task(name='app.tasks.execution_tasks.cleanup_execution_containers')
def cleanup_execution_containers():
    """Clean up Docker containers used for code execution."""
    from app.python_practice.sandbox import sandbox
    
    try:
        sandbox.cleanup_containers()
        return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}
