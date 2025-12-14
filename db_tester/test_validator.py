"""
Advanced Exercise Validator
============================
Enhanced validation with detailed error reporting and test case analysis.
"""

import sys
import os
import json
from typing import Dict, List, Tuple, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.python_practice.validators import validate_python_code
from app.python_practice.executor import execute_python_code


class ExerciseValidator:
    """Enhanced validator for Python exercises."""
    
    def __init__(self, timeout: int = 30):
        """
        Initialize validator.
        
        Args:
            timeout: Maximum execution time in seconds
        """
        self.timeout = timeout
        self.validation_errors = []
    
    def validate_code_syntax(self, code: str) -> Tuple[bool, List[str]]:
        """
        Validate code syntax and security.
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not code or not code.strip():
            errors.append("Code is empty")
            return False, errors
        
        # Use built-in validator
        is_valid, error_msg = validate_python_code(code)
        if not is_valid:
            errors.append(error_msg)
        
        return is_valid, errors
    
    def validate_test_cases(self, test_cases_json: str) -> Tuple[bool, List[Dict], List[str]]:
        """
        Validate and parse test cases.
        
        Args:
            test_cases_json: JSON string of test cases
            
        Returns:
            Tuple of (is_valid, parsed_test_cases, error_messages)
        """
        errors = []
        
        if not test_cases_json:
            errors.append("No test cases provided")
            return False, [], errors
        
        try:
            test_cases = json.loads(test_cases_json)
            
            if not isinstance(test_cases, list):
                errors.append("Test cases must be a JSON array")
                return False, [], errors
            
            if len(test_cases) == 0:
                errors.append("Test cases array is empty")
                return False, [], errors
            
            # Validate each test case structure
            for idx, test_case in enumerate(test_cases):
                if not isinstance(test_case, dict):
                    errors.append(f"Test case {idx + 1} is not a dictionary")
                    continue
                
                # Check required fields
                if 'expected' not in test_case:
                    errors.append(f"Test case {idx + 1} missing 'expected' field")
                
                # Check optional but recommended fields
                if 'description' not in test_case:
                    errors.append(f"Test case {idx + 1} missing 'description' field (warning)")
            
            return len(errors) == 0, test_cases, errors
            
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON format: {str(e)}")
            return False, [], errors
    
    def execute_and_validate(self, code: str, test_cases: List[Dict]) -> Dict[str, Any]:
        """
        Execute code and validate against test cases.
        
        Args:
            code: Python code to execute
            test_cases: List of test case dictionaries
            
        Returns:
            Dictionary containing detailed execution results
        """
        result = {
            'status': 'unknown',
            'passed': False,
            'tests_passed': 0,
            'tests_failed': 0,
            'total_tests': len(test_cases),
            'execution_time_ms': 0,
            'test_results': [],
            'errors': [],
            'output': ''
        }
        
        try:
            # Execute code
            execution_result = execute_python_code(
                code=code,
                test_cases=test_cases,
                timeout=self.timeout
            )
            
            # Update result with execution data
            result['status'] = execution_result.get('status', 'error')
            result['tests_passed'] = execution_result.get('tests_passed', 0)
            result['tests_failed'] = execution_result.get('tests_failed', 0)
            result['execution_time_ms'] = execution_result.get('execution_time_ms', 0)
            result['test_results'] = execution_result.get('test_results', [])
            result['output'] = execution_result.get('output', '')
            
            # Check for errors
            if execution_result.get('error'):
                result['errors'].append(execution_result['error'])
            
            # Determine if passed
            result['passed'] = (
                result['status'] == 'passed' and 
                result['tests_failed'] == 0 and 
                result['tests_passed'] > 0
            )
            
        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(f"Execution exception: {str(e)}")
        
        return result
    
    def analyze_test_results(self, test_results: List[Dict]) -> Dict[str, Any]:
        """
        Analyze test results for patterns and insights.
        
        Args:
            test_results: List of individual test results
            
        Returns:
            Dictionary containing analysis
        """
        analysis = {
            'total_tests': len(test_results),
            'passed_tests': 0,
            'failed_tests': 0,
            'error_tests': 0,
            'common_errors': [],
            'slowest_test': None,
            'fastest_test': None
        }
        
        error_counts = {}
        
        for idx, test in enumerate(test_results):
            if test.get('passed'):
                analysis['passed_tests'] += 1
            else:
                analysis['failed_tests'] += 1
                
                # Track error messages
                error_msg = test.get('error', 'Unknown error')
                if error_msg:
                    analysis['error_tests'] += 1
                    error_counts[error_msg] = error_counts.get(error_msg, 0) + 1
        
        # Find most common errors
        if error_counts:
            sorted_errors = sorted(error_counts.items(), 
                                 key=lambda x: x[1], 
                                 reverse=True)
            analysis['common_errors'] = [
                {'error': error, 'count': count} 
                for error, count in sorted_errors[:5]
            ]
        
        return analysis
    
    def validate_exercise_complete(self, exercise) -> Dict[str, Any]:
        """
        Complete validation of an exercise including code and test cases.
        
        Args:
            exercise: Exercise model object
            
        Returns:
            Dictionary with complete validation results
        """
        result = {
            'exercise_id': exercise.id,
            'exercise_title': exercise.title,
            'valid': False,
            'errors': [],
            'warnings': [],
            'execution_result': None
        }
        
        # Check solution code exists
        if not exercise.solution_code:
            result['errors'].append("No solution code provided")
            return result
        
        # Validate syntax
        syntax_valid, syntax_errors = self.validate_code_syntax(exercise.solution_code)
        if not syntax_valid:
            result['errors'].extend(syntax_errors)
            return result
        
        # Validate test cases
        if not exercise.test_cases:
            result['errors'].append("No test cases provided")
            return result
        
        test_valid, test_cases, test_errors = self.validate_test_cases(exercise.test_cases)
        if not test_valid:
            result['errors'].extend(test_errors)
            return result
        
        # Execute and validate
        execution_result = self.execute_and_validate(exercise.solution_code, test_cases)
        result['execution_result'] = execution_result
        
        # Check if passed
        if execution_result['passed']:
            result['valid'] = True
        else:
            result['errors'].extend(execution_result['errors'])
        
        return result


def test_single_exercise(exercise_id: int) -> Dict[str, Any]:
    """
    Test a single exercise by ID.
    
    Args:
        exercise_id: Exercise ID to test
        
    Returns:
        Dictionary with test results
    """
    from app import create_app, db
    from app.models import Exercise
    
    app = create_app()
    
    with app.app_context():
        exercise = Exercise.query.get(exercise_id)
        
        if not exercise:
            return {
                'error': f'Exercise with ID {exercise_id} not found',
                'exercise_id': exercise_id
            }
        
        if exercise.exercise_type != 'python':
            return {
                'error': f'Exercise {exercise_id} is not a Python exercise',
                'exercise_id': exercise_id,
                'exercise_type': exercise.exercise_type
            }
        
        validator = ExerciseValidator()
        result = validator.validate_exercise_complete(exercise)
        
        return result


if __name__ == '__main__':
    """Allow testing a single exercise from command line."""
    if len(sys.argv) < 2:
        print("Usage: python test_validator.py <exercise_id>")
        sys.exit(1)
    
    try:
        exercise_id = int(sys.argv[1])
        result = test_single_exercise(exercise_id)
        
        print(json.dumps(result, indent=2))
        
        if result.get('valid'):
            sys.exit(0)
        else:
            sys.exit(1)
            
    except ValueError:
        print("Error: Exercise ID must be an integer")
        sys.exit(1)
