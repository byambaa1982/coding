"""
QA Testing Script for Python Exercises
========================================
This script validates that all Python exercises in a course/lesson have correct
solution code that passes all test cases.

Usage:
    python db_tester/test_python_exercises.py

Tests:
    - Validates solution code for all exercises in course_id=5, lesson_id=6
    - Executes solution against all test cases
    - Reports pass/fail status for each exercise
    - Generates detailed test report
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Exercise, Lesson, NewTutorial
from app.python_practice.validators import validate_python_code
from app.python_practice.executor import execute_python_code


class ExerciseTester:
    """Test harness for validating Python exercises."""
    
    def __init__(self, course_id: int, lesson_id: int):
        """
        Initialize tester for specific course and lesson.
        
        Args:
            course_id: Tutorial/Course ID
            lesson_id: Lesson ID within the course
        """
        self.course_id = course_id
        self.lesson_id = lesson_id
        self.app = create_app()
        self.results = []
        
    def get_exercises(self) -> List[Exercise]:
        """
        Fetch all Python exercises for the specified course and lesson.
        
        Returns:
            List of Exercise objects
        """
        with self.app.app_context():
            exercises = Exercise.query.filter_by(
                tutorial_id=self.course_id,
                lesson_id=self.lesson_id,
                exercise_type='python'
            ).order_by(Exercise.order_index).all()
            
            return exercises
    
    def validate_exercise(self, exercise: Exercise) -> Dict[str, Any]:
        """
        Validate a single exercise by running its solution code.
        
        Args:
            exercise: Exercise object to validate
            
        Returns:
            Dictionary containing test results
        """
        result = {
            'exercise_id': exercise.id,
            'exercise_title': exercise.title,
            'exercise_slug': exercise.slug,
            'difficulty': exercise.difficulty,
            'order_index': exercise.order_index,
            'has_solution': bool(exercise.solution_code),
            'has_test_cases': bool(exercise.test_cases),
            'validation_passed': False,
            'execution_status': None,
            'tests_passed': 0,
            'tests_failed': 0,
            'total_tests': 0,
            'execution_time_ms': 0,
            'errors': [],
            'test_details': []
        }
        
        # Check if solution code exists
        if not exercise.solution_code:
            result['errors'].append('No solution code provided')
            return result
        
        # Check if test cases exist
        if not exercise.test_cases:
            result['errors'].append('No test cases provided')
            return result
        
        # Validate solution code for security
        is_valid, validation_msg = validate_python_code(exercise.solution_code)
        if not is_valid:
            result['errors'].append(f'Code validation failed: {validation_msg}')
            return result
        
        # Parse test cases
        try:
            test_cases = json.loads(exercise.test_cases)
            result['total_tests'] = len(test_cases)
        except json.JSONDecodeError as e:
            result['errors'].append(f'Failed to parse test cases: {str(e)}')
            return result
        
        # Execute solution code with test cases
        try:
            execution_result = execute_python_code(
                code=exercise.solution_code,
                test_cases=test_cases,
                timeout=30
            )
            
            result['execution_status'] = execution_result['status']
            result['tests_passed'] = execution_result.get('tests_passed', 0)
            result['tests_failed'] = execution_result.get('tests_failed', 0)
            result['execution_time_ms'] = execution_result.get('execution_time_ms', 0)
            result['test_details'] = execution_result.get('test_results', [])
            
            # Check if validation passed
            if execution_result['status'] == 'passed' and result['tests_failed'] == 0:
                result['validation_passed'] = True
            else:
                if execution_result.get('error'):
                    result['errors'].append(execution_result['error'])
                if execution_result.get('output'):
                    result['output'] = execution_result['output']
                    
        except Exception as e:
            result['errors'].append(f'Execution exception: {str(e)}')
        
        return result
    
    def run_tests(self) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        Run tests on all exercises in the course/lesson.
        
        Returns:
            Tuple of (individual results, summary statistics)
        """
        with self.app.app_context():
            # Get lesson info
            lesson = Lesson.query.get(self.lesson_id)
            course = NewTutorial.query.get(self.course_id)
            
            if not lesson:
                print(f"❌ ERROR: Lesson ID {self.lesson_id} not found")
                return [], {}
            
            if not course:
                print(f"❌ ERROR: Course ID {self.course_id} not found")
                return [], {}
            
            print(f"\n{'='*80}")
            print(f"QA Testing Python Exercises")
            print(f"{'='*80}")
            print(f"Course: {course.title} (ID: {self.course_id})")
            print(f"Lesson: {lesson.title} (ID: {self.lesson_id})")
            print(f"{'='*80}\n")
            
            # Get all exercises
            exercises = self.get_exercises()
            
            if not exercises:
                print(f"⚠️  WARNING: No Python exercises found for this course/lesson")
                return [], {}
            
            print(f"Found {len(exercises)} Python exercise(s) to test\n")
            
            # Test each exercise
            results = []
            for idx, exercise in enumerate(exercises, 1):
                print(f"[{idx}/{len(exercises)}] Testing: {exercise.title}")
                print(f"    Exercise ID: {exercise.id}")
                print(f"    Difficulty: {exercise.difficulty}")
                
                result = self.validate_exercise(exercise)
                results.append(result)
                
                # Print result
                if result['validation_passed']:
                    print(f"    ✅ PASSED - {result['tests_passed']}/{result['total_tests']} tests passed")
                else:
                    print(f"    ❌ FAILED - {result['tests_passed']}/{result['total_tests']} tests passed")
                    if result['errors']:
                        for error in result['errors']:
                            print(f"       Error: {error}")
                
                print(f"    Execution time: {result['execution_time_ms']}ms\n")
            
            # Generate summary
            summary = self._generate_summary(results, course, lesson)
            
            return results, summary
    
    def _generate_summary(self, results: List[Dict], course: NewTutorial, 
                         lesson: Lesson) -> Dict[str, Any]:
        """
        Generate summary statistics from test results.
        
        Args:
            results: List of individual test results
            course: NewTutorial object
            lesson: Lesson object
            
        Returns:
            Dictionary containing summary statistics
        """
        total_exercises = len(results)
        passed_exercises = sum(1 for r in results if r['validation_passed'])
        failed_exercises = total_exercises - passed_exercises
        
        total_tests = sum(r['total_tests'] for r in results)
        total_tests_passed = sum(r['tests_passed'] for r in results)
        total_tests_failed = sum(r['tests_failed'] for r in results)
        
        total_execution_time = sum(r['execution_time_ms'] for r in results)
        
        summary = {
            'course_id': self.course_id,
            'course_title': course.title,
            'lesson_id': self.lesson_id,
            'lesson_title': lesson.title,
            'test_date': datetime.utcnow().isoformat(),
            'total_exercises': total_exercises,
            'passed_exercises': passed_exercises,
            'failed_exercises': failed_exercises,
            'success_rate': (passed_exercises / total_exercises * 100) if total_exercises > 0 else 0,
            'total_test_cases': total_tests,
            'total_tests_passed': total_tests_passed,
            'total_tests_failed': total_tests_failed,
            'total_execution_time_ms': total_execution_time,
            'avg_execution_time_ms': total_execution_time / total_exercises if total_exercises > 0 else 0
        }
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """
        Print test summary to console.
        
        Args:
            summary: Summary statistics dictionary
        """
        print(f"\n{'='*80}")
        print(f"TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Course: {summary['course_title']} (ID: {summary['course_id']})")
        print(f"Lesson: {summary['lesson_title']} (ID: {summary['lesson_id']})")
        print(f"Test Date: {summary['test_date']}")
        print(f"{'-'*80}")
        print(f"Total Exercises: {summary['total_exercises']}")
        print(f"✅ Passed: {summary['passed_exercises']}")
        print(f"❌ Failed: {summary['failed_exercises']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"{'-'*80}")
        print(f"Total Test Cases: {summary['total_test_cases']}")
        print(f"Tests Passed: {summary['total_tests_passed']}")
        print(f"Tests Failed: {summary['total_tests_failed']}")
        print(f"{'-'*80}")
        print(f"Total Execution Time: {summary['total_execution_time_ms']}ms")
        print(f"Avg Execution Time: {summary['avg_execution_time_ms']:.1f}ms per exercise")
        print(f"{'='*80}\n")
    
    def save_report(self, results: List[Dict], summary: Dict[str, Any], 
                   filename: str = None):
        """
        Save detailed test report to JSON file.
        
        Args:
            results: List of individual test results
            summary: Summary statistics
            filename: Optional custom filename
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'test_report_course{self.course_id}_lesson{self.lesson_id}_{timestamp}.json'
        
        report_path = os.path.join(os.path.dirname(__file__), filename)
        
        report = {
            'summary': summary,
            'detailed_results': results
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Detailed report saved to: {report_path}\n")


def main():
    """Main entry point for the test script."""
    # Configuration - Change these to test different courses/lessons
    COURSE_ID = 5
    LESSON_ID = 6
    
    # Create tester instance
    tester = ExerciseTester(course_id=COURSE_ID, lesson_id=LESSON_ID)
    
    # Run tests
    results, summary = tester.run_tests()
    
    # Print summary
    if summary:
        tester.print_summary(summary)
        
        # Save detailed report
        tester.save_report(results, summary)
        
        # Exit with appropriate code
        if summary['failed_exercises'] > 0:
            print("⚠️  Some exercises failed validation!")
            sys.exit(1)
        else:
            print("✅ All exercises passed validation!")
            sys.exit(0)
    else:
        print("❌ No tests were run")
        sys.exit(1)


if __name__ == '__main__':
    main()
