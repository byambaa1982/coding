"""
Exercise QA Testing Suite
==========================
Professional testing framework for validating Python exercises.

This package provides comprehensive testing tools for ensuring exercise quality:
- Individual exercise validation
- Course/lesson batch testing
- Detailed JSON and HTML reporting
- Security and performance validation

Quick Start:
-----------
    # Test single course/lesson
    python db_tester/test_python_exercises.py
    
    # Test specific exercise
    python db_tester/test_validator.py 27
    
    # Batch test multiple courses
    python db_tester/batch_tester.py specific
    
    # List available courses
    python db_tester/batch_tester.py list

Usage Examples:
--------------
    from db_tester.test_python_exercises import ExerciseTester
    
    # Test course 5, lesson 6
    tester = ExerciseTester(course_id=5, lesson_id=6)
    results, summary = tester.run_tests()
    tester.print_summary(summary)
    tester.save_report(results, summary)

Modules:
--------
- test_python_exercises: Main test runner for course/lesson validation
- test_validator: Enhanced validation with detailed error reporting
- batch_tester: Batch testing for multiple courses/lessons
- html_report: HTML report generator with visual formatting
- test_config: Configuration settings and utility functions
"""

__version__ = '1.0.0'
__author__ = 'QA Testing Team'
__all__ = [
    'ExerciseTester',
    'ExerciseValidator',
    'BatchTester',
    'generate_html_report'
]

# Import main classes for easy access
try:
    from .test_python_exercises import ExerciseTester
    from .test_validator import ExerciseValidator
    from .batch_tester import BatchTester
    from .html_report import generate_html_report
except ImportError:
    # Allow imports to fail during initial setup
    pass
