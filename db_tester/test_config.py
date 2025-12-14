"""
Test Configuration and Utilities
=================================
Configuration settings and utility functions for exercise testing.
"""

import os
from typing import Dict, Any

# Test Configuration
TEST_CONFIG = {
    # Course and Lesson to test
    'COURSE_ID': 5,
    'LESSON_ID': 6,
    
    # Execution settings
    'TIMEOUT_SECONDS': 30,
    'MAX_RETRIES': 3,
    
    # Report settings
    'SAVE_REPORTS': True,
    'REPORT_FORMAT': 'json',  # 'json' or 'html'
    'VERBOSE': True,
    
    # Output directory for reports
    'REPORTS_DIR': os.path.join(os.path.dirname(__file__), 'reports')
}


class TestResult:
    """Data class for storing test results."""
    
    def __init__(self):
        self.exercise_id: int = None
        self.exercise_title: str = ""
        self.passed: bool = False
        self.tests_passed: int = 0
        self.tests_failed: int = 0
        self.errors: list = []
        self.execution_time_ms: int = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'exercise_id': self.exercise_id,
            'exercise_title': self.exercise_title,
            'passed': self.passed,
            'tests_passed': self.tests_passed,
            'tests_failed': self.tests_failed,
            'errors': self.errors,
            'execution_time_ms': self.execution_time_ms
        }
    
    @property
    def total_tests(self) -> int:
        """Get total number of tests."""
        return self.tests_passed + self.tests_failed
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.tests_passed / self.total_tests) * 100


def format_execution_time(milliseconds: int) -> str:
    """
    Format execution time for display.
    
    Args:
        milliseconds: Time in milliseconds
        
    Returns:
        Formatted string (e.g., "1.5s" or "250ms")
    """
    if milliseconds >= 1000:
        seconds = milliseconds / 1000
        return f"{seconds:.2f}s"
    return f"{milliseconds}ms"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format percentage for display.
    
    Args:
        value: Percentage value (0-100)
        decimals: Number of decimal places
        
    Returns:
        Formatted string (e.g., "95.5%")
    """
    return f"{value:.{decimals}f}%"


def print_test_header(course_title: str, lesson_title: str, 
                     exercise_count: int):
    """
    Print formatted test header.
    
    Args:
        course_title: Course title
        lesson_title: Lesson title
        exercise_count: Number of exercises to test
    """
    print(f"\n{'='*80}")
    print(f"Python Exercise QA Testing")
    print(f"{'='*80}")
    print(f"Course: {course_title}")
    print(f"Lesson: {lesson_title}")
    print(f"Exercises: {exercise_count}")
    print(f"{'='*80}\n")


def print_test_result(exercise_num: int, total_exercises: int, 
                     title: str, passed: bool, tests_passed: int,
                     total_tests: int, execution_time: int):
    """
    Print formatted test result.
    
    Args:
        exercise_num: Current exercise number
        total_exercises: Total number of exercises
        title: Exercise title
        passed: Whether validation passed
        tests_passed: Number of tests passed
        total_tests: Total number of tests
        execution_time: Execution time in ms
    """
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"[{exercise_num}/{total_exercises}] {title}")
    print(f"    Status: {status}")
    print(f"    Tests: {tests_passed}/{total_tests} passed")
    print(f"    Time: {format_execution_time(execution_time)}")


def create_reports_directory():
    """Create reports directory if it doesn't exist."""
    reports_dir = TEST_CONFIG['REPORTS_DIR']
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        print(f"Created reports directory: {reports_dir}")
