"""
Batch Exercise Tester
=====================
Test multiple courses and lessons in batch mode.
Useful for validating entire content libraries.
"""

import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Tuple, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import NewTutorial, Lesson, Exercise
from test_python_exercises import ExerciseTester


class BatchTester:
    """Batch testing for multiple courses and lessons."""
    
    def __init__(self):
        """Initialize batch tester."""
        self.app = create_app()
        self.batch_results = []
    
    def get_all_courses_with_exercises(self) -> List[Dict[str, Any]]:
        """
        Get all courses that have Python exercises.
        
        Returns:
            List of course dictionaries with lesson information
        """
        with self.app.app_context():
            # Get all courses that have Python exercises
            courses = db.session.query(NewTutorial).join(Exercise).filter(
                Exercise.exercise_type == 'python'
            ).distinct().all()
            
            course_list = []
            for course in courses:
                # Get lessons with Python exercises
                lessons = db.session.query(Lesson).join(Exercise).filter(
                    Exercise.tutorial_id == course.id,
                    Exercise.exercise_type == 'python'
                ).distinct().all()
                
                course_info = {
                    'course_id': course.id,
                    'course_title': course.title,
                    'lessons': [
                        {
                            'lesson_id': lesson.id,
                            'lesson_title': lesson.title,
                            'exercise_count': Exercise.query.filter_by(
                                tutorial_id=course.id,
                                lesson_id=lesson.id,
                                exercise_type='python'
                            ).count()
                        }
                        for lesson in lessons
                    ]
                }
                course_list.append(course_info)
            
            return course_list
    
    def test_course_lesson(self, course_id: int, lesson_id: int) -> Dict[str, Any]:
        """
        Test a specific course and lesson.
        
        Args:
            course_id: Course ID
            lesson_id: Lesson ID
            
        Returns:
            Test results and summary
        """
        print(f"\n{'='*80}")
        print(f"Testing Course ID: {course_id}, Lesson ID: {lesson_id}")
        print(f"{'='*80}\n")
        
        tester = ExerciseTester(course_id=course_id, lesson_id=lesson_id)
        results, summary = tester.run_tests()
        
        return {
            'course_id': course_id,
            'lesson_id': lesson_id,
            'results': results,
            'summary': summary
        }
    
    def test_all_courses(self) -> List[Dict[str, Any]]:
        """
        Test all courses and lessons in the system.
        
        Returns:
            List of all test results
        """
        courses = self.get_all_courses_with_exercises()
        
        print(f"\n{'#'*80}")
        print(f"BATCH TESTING - All Courses")
        print(f"{'#'*80}")
        print(f"Found {len(courses)} course(s) with Python exercises\n")
        
        all_results = []
        
        for course in courses:
            print(f"\n📚 Course: {course['course_title']}")
            print(f"   Lessons: {len(course['lessons'])}")
            
            for lesson in course['lessons']:
                result = self.test_course_lesson(
                    course['course_id'],
                    lesson['lesson_id']
                )
                all_results.append(result)
        
        return all_results
    
    def test_specific_courses(self, course_lesson_pairs: List[Tuple[int, int]]) -> List[Dict[str, Any]]:
        """
        Test specific course/lesson pairs.
        
        Args:
            course_lesson_pairs: List of (course_id, lesson_id) tuples
            
        Returns:
            List of test results
        """
        print(f"\n{'#'*80}")
        print(f"BATCH TESTING - Specific Courses")
        print(f"{'#'*80}")
        print(f"Testing {len(course_lesson_pairs)} course/lesson pair(s)\n")
        
        all_results = []
        
        for course_id, lesson_id in course_lesson_pairs:
            result = self.test_course_lesson(course_id, lesson_id)
            all_results.append(result)
        
        return all_results
    
    def generate_batch_summary(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary across all batch tests.
        
        Args:
            all_results: List of all test results
            
        Returns:
            Overall summary statistics
        """
        total_exercises = 0
        total_passed = 0
        total_failed = 0
        total_tests = 0
        total_tests_passed = 0
        total_tests_failed = 0
        total_execution_time = 0
        
        courses_tested = set()
        lessons_tested = 0
        
        for result in all_results:
            summary = result['summary']
            courses_tested.add(summary['course_id'])
            lessons_tested += 1
            
            total_exercises += summary['total_exercises']
            total_passed += summary['passed_exercises']
            total_failed += summary['failed_exercises']
            total_tests += summary['total_test_cases']
            total_tests_passed += summary['total_tests_passed']
            total_tests_failed += summary['total_tests_failed']
            total_execution_time += summary['total_execution_time_ms']
        
        batch_summary = {
            'test_date': datetime.utcnow().isoformat(),
            'courses_tested': len(courses_tested),
            'lessons_tested': lessons_tested,
            'total_exercises': total_exercises,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'overall_success_rate': (total_passed / total_exercises * 100) if total_exercises > 0 else 0,
            'total_test_cases': total_tests,
            'total_tests_passed': total_tests_passed,
            'total_tests_failed': total_tests_failed,
            'total_execution_time_ms': total_execution_time,
            'avg_execution_time_per_exercise': total_execution_time / total_exercises if total_exercises > 0 else 0
        }
        
        return batch_summary
    
    def print_batch_summary(self, batch_summary: Dict[str, Any]):
        """
        Print batch test summary.
        
        Args:
            batch_summary: Batch summary statistics
        """
        print(f"\n{'#'*80}")
        print(f"BATCH TEST SUMMARY")
        print(f"{'#'*80}")
        print(f"Test Date: {batch_summary['test_date']}")
        print(f"{'-'*80}")
        print(f"Courses Tested: {batch_summary['courses_tested']}")
        print(f"Lessons Tested: {batch_summary['lessons_tested']}")
        print(f"Total Exercises: {batch_summary['total_exercises']}")
        print(f"{'-'*80}")
        print(f"✅ Passed: {batch_summary['total_passed']}")
        print(f"❌ Failed: {batch_summary['total_failed']}")
        print(f"Overall Success Rate: {batch_summary['overall_success_rate']:.1f}%")
        print(f"{'-'*80}")
        print(f"Total Test Cases: {batch_summary['total_test_cases']}")
        print(f"Tests Passed: {batch_summary['total_tests_passed']}")
        print(f"Tests Failed: {batch_summary['total_tests_failed']}")
        print(f"{'-'*80}")
        print(f"Total Execution Time: {batch_summary['total_execution_time_ms']}ms")
        print(f"Avg per Exercise: {batch_summary['avg_execution_time_per_exercise']:.1f}ms")
        print(f"{'#'*80}\n")
    
    def save_batch_report(self, all_results: List[Dict[str, Any]], 
                         batch_summary: Dict[str, Any], filename: str = None):
        """
        Save batch test report.
        
        Args:
            all_results: List of all test results
            batch_summary: Batch summary statistics
            filename: Optional custom filename
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'batch_test_report_{timestamp}.json'
        
        report_path = os.path.join(os.path.dirname(__file__), filename)
        
        report = {
            'batch_summary': batch_summary,
            'individual_results': all_results
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Batch report saved to: {report_path}\n")


def main():
    """Main entry point for batch testing."""
    print("Python Exercise Batch Tester")
    print("="*80)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = 'specific'  # Default mode
    
    tester = BatchTester()
    
    if mode == 'all':
        # Test all courses and lessons
        print("\nMode: Test ALL courses and lessons")
        all_results = tester.test_all_courses()
        
    elif mode == 'list':
        # List all available courses and lessons
        print("\nMode: List available courses and lessons\n")
        courses = tester.get_all_courses_with_exercises()
        
        for course in courses:
            print(f"📚 Course ID {course['course_id']}: {course['course_title']}")
            for lesson in course['lessons']:
                print(f"   └─ Lesson ID {lesson['lesson_id']}: {lesson['lesson_title']}")
                print(f"      ({lesson['exercise_count']} exercises)")
        
        print(f"\nTotal: {len(courses)} course(s)")
        return
        
    elif mode == 'specific':
        # Test specific course/lesson pairs (default)
        print("\nMode: Test specific courses")
        
        # Define course/lesson pairs to test
        # Modify this list to test different courses
        course_lesson_pairs = [
            (5, 6),  # Course 5, Lesson 6
            # Add more pairs as needed:
            # (5, 7),  # Course 5, Lesson 7
            # (6, 1),  # Course 6, Lesson 1
        ]
        
        print(f"Testing {len(course_lesson_pairs)} course/lesson pair(s):")
        for course_id, lesson_id in course_lesson_pairs:
            print(f"  - Course {course_id}, Lesson {lesson_id}")
        
        all_results = tester.test_specific_courses(course_lesson_pairs)
        
    else:
        print(f"❌ Unknown mode: {mode}")
        print("\nUsage:")
        print("  python batch_tester.py              # Test specific courses (default)")
        print("  python batch_tester.py specific     # Test specific courses")
        print("  python batch_tester.py all          # Test all courses")
        print("  python batch_tester.py list         # List available courses")
        sys.exit(1)
    
    # Generate and print batch summary
    if mode != 'list':
        batch_summary = tester.generate_batch_summary(all_results)
        tester.print_batch_summary(batch_summary)
        
        # Save batch report
        tester.save_batch_report(all_results, batch_summary)
        
        # Exit with appropriate code
        if batch_summary['total_failed'] > 0:
            print("⚠️  Some exercises failed validation!")
            sys.exit(1)
        else:
            print("✅ All exercises passed validation!")
            sys.exit(0)


if __name__ == '__main__':
    main()
