"""
Usage Examples for Exercise Testing Suite
==========================================
This file demonstrates various ways to use the testing framework.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Example 1: Test a Single Course and Lesson
# ===========================================
def example_test_single_course():
    """Test all exercises in a specific course and lesson."""
    from db_tester.test_python_exercises import ExerciseTester
    
    print("\n" + "="*80)
    print("EXAMPLE 1: Test Single Course/Lesson")
    print("="*80 + "\n")
    
    # Create tester for course 5, lesson 6
    tester = ExerciseTester(course_id=5, lesson_id=6)
    
    # Run tests
    results, summary = tester.run_tests()
    
    # Print summary
    tester.print_summary(summary)
    
    # Save reports
    tester.save_report(results, summary)
    
    return summary


# Example 2: Test a Single Exercise
# ==================================
def example_test_single_exercise():
    """Test a single exercise by ID."""
    from db_tester.test_validator import test_single_exercise
    
    print("\n" + "="*80)
    print("EXAMPLE 2: Test Single Exercise")
    print("="*80 + "\n")
    
    # Test exercise ID 27
    result = test_single_exercise(27)
    
    print(f"Exercise: {result.get('exercise_title', 'N/A')}")
    print(f"Valid: {result.get('valid', False)}")
    print(f"Errors: {result.get('errors', [])}")
    
    if result.get('execution_result'):
        exec_result = result['execution_result']
        print(f"Status: {exec_result['status']}")
        print(f"Tests Passed: {exec_result['tests_passed']}/{exec_result['total_tests']}")
    
    return result


# Example 3: Batch Test Multiple Courses
# =======================================
def example_batch_test():
    """Test multiple course/lesson pairs in batch."""
    from db_tester.batch_tester import BatchTester
    
    print("\n" + "="*80)
    print("EXAMPLE 3: Batch Test Multiple Courses")
    print("="*80 + "\n")
    
    # Create batch tester
    tester = BatchTester()
    
    # Define courses to test
    course_lesson_pairs = [
        (5, 6),  # Course 5, Lesson 6
        # Add more as needed
    ]
    
    # Run batch tests
    all_results = tester.test_specific_courses(course_lesson_pairs)
    
    # Generate summary
    batch_summary = tester.generate_batch_summary(all_results)
    tester.print_batch_summary(batch_summary)
    
    # Save batch report
    tester.save_batch_report(all_results, batch_summary)
    
    return batch_summary


# Example 4: List All Available Courses
# ======================================
def example_list_courses():
    """List all courses that have Python exercises."""
    from db_tester.batch_tester import BatchTester
    
    print("\n" + "="*80)
    print("EXAMPLE 4: List Available Courses")
    print("="*80 + "\n")
    
    tester = BatchTester()
    courses = tester.get_all_courses_with_exercises()
    
    print(f"Found {len(courses)} course(s) with Python exercises:\n")
    
    for course in courses:
        print(f"📚 Course ID {course['course_id']}: {course['course_title']}")
        print(f"   Lessons: {len(course['lessons'])}")
        
        for lesson in course['lessons']:
            print(f"   └─ Lesson ID {lesson['lesson_id']}: {lesson['lesson_title']}")
            print(f"      Exercises: {lesson['exercise_count']}")
        print()
    
    return courses


# Example 5: Custom Validation Logic
# ===================================
def example_custom_validation():
    """Use the validator directly for custom validation."""
    from db_tester.test_validator import ExerciseValidator
    
    print("\n" + "="*80)
    print("EXAMPLE 5: Custom Validation")
    print("="*80 + "\n")
    
    # Create validator
    validator = ExerciseValidator(timeout=30)
    
    # Test code syntax
    test_code = """
def hello_world():
    return "Hello, World!"
"""
    
    is_valid, errors = validator.validate_code_syntax(test_code)
    print(f"Code Syntax Valid: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    
    # Test JSON test cases
    test_cases_json = '''
    [
        {
            "description": "Test hello_world function",
            "function_name": "hello_world",
            "input": {},
            "expected": "Hello, World!"
        }
    ]
    '''
    
    is_valid, test_cases, errors = validator.validate_test_cases(test_cases_json)
    print(f"\nTest Cases Valid: {is_valid}")
    print(f"Number of Test Cases: {len(test_cases)}")
    if errors:
        print(f"Errors: {errors}")
    
    # Execute and validate
    if is_valid and len(test_cases) > 0:
        result = validator.execute_and_validate(test_code, test_cases)
        print(f"\nExecution Status: {result['status']}")
        print(f"Passed: {result['passed']}")
        print(f"Tests Passed: {result['tests_passed']}/{result['total_tests']}")


# Example 6: Generate HTML Report
# ================================
def example_html_report():
    """Generate HTML report for test results."""
    from db_tester.test_python_exercises import ExerciseTester
    from db_tester.html_report import generate_html_report
    
    print("\n" + "="*80)
    print("EXAMPLE 6: Generate HTML Report")
    print("="*80 + "\n")
    
    # Run tests
    tester = ExerciseTester(course_id=5, lesson_id=6)
    results, summary = tester.run_tests()
    
    # Generate HTML report
    report_path = os.path.join(os.path.dirname(__file__), 'example_report.html')
    generate_html_report(results, summary, report_path)
    
    print(f"HTML report generated: {report_path}")
    print("Open this file in a web browser to view the visual report.")


# Example 7: Filter and Analyze Results
# ======================================
def example_analyze_results():
    """Analyze test results to find patterns."""
    from db_tester.test_python_exercises import ExerciseTester
    
    print("\n" + "="*80)
    print("EXAMPLE 7: Analyze Test Results")
    print("="*80 + "\n")
    
    # Run tests
    tester = ExerciseTester(course_id=5, lesson_id=6)
    results, summary = tester.run_tests()
    
    # Find failed exercises
    failed_exercises = [r for r in results if not r['validation_passed']]
    print(f"Failed Exercises: {len(failed_exercises)}")
    
    for exercise in failed_exercises:
        print(f"\n❌ {exercise['exercise_title']} (ID: {exercise['exercise_id']})")
        print(f"   Difficulty: {exercise['difficulty']}")
        print(f"   Tests Passed: {exercise['tests_passed']}/{exercise['total_tests']}")
        
        if exercise['errors']:
            print(f"   Errors:")
            for error in exercise['errors']:
                print(f"     - {error}")
    
    # Find slow exercises (>1 second)
    slow_exercises = [r for r in results if r['execution_time_ms'] > 1000]
    print(f"\nSlow Exercises (>1s): {len(slow_exercises)}")
    
    for exercise in slow_exercises:
        print(f"   - {exercise['exercise_title']}: {exercise['execution_time_ms']}ms")
    
    # Calculate average difficulty
    difficulty_counts = {}
    for r in results:
        diff = r['difficulty']
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
    
    print(f"\nDifficulty Distribution:")
    for diff, count in difficulty_counts.items():
        print(f"   {diff.capitalize()}: {count} exercise(s)")


# Example 8: CI/CD Integration
# =============================
def example_ci_cd_integration():
    """Example of using tests in CI/CD pipeline."""
    from db_tester.test_python_exercises import ExerciseTester
    
    print("\n" + "="*80)
    print("EXAMPLE 8: CI/CD Integration")
    print("="*80 + "\n")
    
    # Run tests
    tester = ExerciseTester(course_id=5, lesson_id=6)
    results, summary = tester.run_tests()
    
    # Check if all tests passed
    if summary['failed_exercises'] == 0:
        print("✅ All tests passed - Ready for deployment!")
        return 0
    else:
        print(f"❌ {summary['failed_exercises']} exercise(s) failed")
        print("Fix issues before deploying to production.")
        
        # List failed exercises
        for result in results:
            if not result['validation_passed']:
                print(f"   - {result['exercise_title']} (ID: {result['exercise_id']})")
        
        return 1


# Main Menu
# =========
def main():
    """Interactive menu to run examples."""
    print("\n" + "="*80)
    print("Exercise Testing Suite - Usage Examples")
    print("="*80)
    
    examples = {
        '1': ('Test Single Course/Lesson', example_test_single_course),
        '2': ('Test Single Exercise', example_test_single_exercise),
        '3': ('Batch Test Multiple Courses', example_batch_test),
        '4': ('List Available Courses', example_list_courses),
        '5': ('Custom Validation Logic', example_custom_validation),
        '6': ('Generate HTML Report', example_html_report),
        '7': ('Analyze Test Results', example_analyze_results),
        '8': ('CI/CD Integration Example', example_ci_cd_integration),
    }
    
    print("\nAvailable Examples:\n")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. Exit")
    
    while True:
        choice = input("\nSelect an example to run (0-8): ").strip()
        
        if choice == '0':
            print("\nGoodbye!")
            break
        
        if choice in examples:
            name, func = examples[choice]
            try:
                func()
            except Exception as e:
                print(f"\n❌ Error running example: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print("Invalid choice. Please try again.")


if __name__ == '__main__':
    main()
