"""
Test Lesson 6 Task Upsert Script
=================================
Test the task upsert script before running it on the actual database.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from upsert_lesson6_tasks import TaskParser, TaskUpserter
from app import create_app
from app.models import Exercise, NewTutorial, Lesson
from app.extensions import db


class TestTaskUpserter:
    """Test suite for task upserter."""
    
    def __init__(self):
        self.app = create_app()
        self.results = []
        self.markdown_file = os.path.join(
            os.path.dirname(__file__),
            '..',
            'contents',
            'lesson6_variables_datatypes_tasks.md'
        )
    
    def test_file_exists(self):
        """Test 1: Check if markdown file exists."""
        print("\n" + "="*80)
        print("TEST 1: File Existence")
        print("="*80)
        
        exists = os.path.exists(self.markdown_file)
        status = "✓ PASS" if exists else "✗ FAIL"
        print(f"{status}: Markdown file {'exists' if exists else 'not found'}")
        print(f"Path: {self.markdown_file}")
        
        self.results.append({
            'test': 'File Existence',
            'passed': exists,
            'details': f"File: {self.markdown_file}"
        })
        
        return exists
    
    def test_parse_tasks(self):
        """Test 2: Parse tasks from markdown."""
        print("\n" + "="*80)
        print("TEST 2: Task Parsing")
        print("="*80)
        
        try:
            parser = TaskParser(self.markdown_file)
            tasks = parser.parse()
            
            passed = len(tasks) == 5
            status = "✓ PASS" if passed else "✗ FAIL"
            
            print(f"{status}: Found {len(tasks)} tasks (expected 5)")
            
            if tasks:
                print("\nParsed tasks:")
                for i, task in enumerate(tasks, 1):
                    print(f"  {i}. {task['title']}")
                    print(f"     - Difficulty: {task['difficulty']}")
                    print(f"     - Points: {task['points']}")
                    print(f"     - Estimated time: {task['estimated_minutes']} min")
            
            # Check difficulty distribution
            print("\nDifficulty distribution:")
            easy_count = sum(1 for t in tasks if t['difficulty'] == 'easy')
            medium_count = sum(1 for t in tasks if t['difficulty'] == 'medium')
            hard_count = sum(1 for t in tasks if t['difficulty'] == 'hard')
            
            print(f"  - Easy: {easy_count} (expected 3)")
            print(f"  - Medium: {medium_count} (expected 2)")
            print(f"  - Hard: {hard_count} (expected 0)")
            
            difficulty_check = easy_count == 3 and medium_count == 2 and hard_count == 0
            
            self.results.append({
                'test': 'Task Parsing',
                'passed': passed and difficulty_check,
                'details': f"Tasks parsed: {len(tasks)}, Difficulty correct: {difficulty_check}"
            })
            
            return tasks if passed else []
            
        except Exception as e:
            print(f"✗ FAIL: Error parsing tasks: {str(e)}")
            self.results.append({
                'test': 'Task Parsing',
                'passed': False,
                'details': f"Error: {str(e)}"
            })
            return []
    
    def test_database_connection(self):
        """Test 3: Check database connection."""
        print("\n" + "="*80)
        print("TEST 3: Database Connection")
        print("="*80)
        
        try:
            with self.app.app_context():
                # Test query
                tutorial = NewTutorial.query.get(5)
                lesson = Lesson.query.get(6)
                
                passed = tutorial is not None and lesson is not None
                status = "✓ PASS" if passed else "✗ FAIL"
                
                if tutorial:
                    print(f"{status}: Connected to database")
                    print(f"  - Tutorial 5: {tutorial.title}")
                    if lesson:
                        print(f"  - Lesson 6: {lesson.title}")
                    else:
                        print(f"  - Lesson 6: NOT FOUND")
                else:
                    print(f"{status}: Tutorial 5 not found in database")
                
                self.results.append({
                    'test': 'Database Connection',
                    'passed': passed,
                    'details': f"Tutorial: {tutorial.title if tutorial else 'Not found'}, Lesson: {lesson.title if lesson else 'Not found'}"
                })
                
                return passed
                
        except Exception as e:
            print(f"✗ FAIL: Database connection error: {str(e)}")
            self.results.append({
                'test': 'Database Connection',
                'passed': False,
                'details': f"Error: {str(e)}"
            })
            return False
    
    def test_slug_generation(self):
        """Test 4: Check slug generation."""
        print("\n" + "="*80)
        print("TEST 4: Slug Generation")
        print("="*80)
        
        try:
            with self.app.app_context():
                upserter = TaskUpserter(self.app)
                
                test_cases = [
                    ("Create and Display Multiple Variable Types", 1, "lesson6-task1-create-and-display-multiple-variable-types"),
                    ("Variable Naming Convention Practice", 2, "lesson6-task2-variable-naming-convention-practice"),
                    ("Type Conversion Challenge", 3, "lesson6-task3-type-conversion-challenge"),
                ]
                
                all_passed = True
                for title, order, expected_slug in test_cases:
                    slug = upserter.generate_slug(title, order)
                    passed = slug == expected_slug
                    all_passed = all_passed and passed
                    status = "✓" if passed else "✗"
                    print(f"{status} '{title}' -> '{slug}'")
                
                status = "✓ PASS" if all_passed else "✗ FAIL"
                print(f"\n{status}: Slug generation test")
                
                self.results.append({
                    'test': 'Slug Generation',
                    'passed': all_passed,
                    'details': f"All slug tests passed: {all_passed}"
                })
                
                return all_passed
                
        except Exception as e:
            print(f"✗ FAIL: Slug generation error: {str(e)}")
            self.results.append({
                'test': 'Slug Generation',
                'passed': False,
                'details': f"Error: {str(e)}"
            })
            return False
    
    def test_dry_run(self):
        """Test 5: Perform dry run without committing."""
        print("\n" + "="*80)
        print("TEST 5: Dry Run (No Commit)")
        print("="*80)
        
        try:
            with self.app.app_context():
                parser = TaskParser(self.markdown_file)
                tasks = parser.parse()
                
                if not tasks:
                    print("✗ FAIL: No tasks to test")
                    self.results.append({
                        'test': 'Dry Run',
                        'passed': False,
                        'details': 'No tasks parsed'
                    })
                    return False
                
                # Check existing exercises
                existing_exercises = Exercise.query.filter_by(lesson_id=6).all()
                print(f"Current exercises in Lesson 6: {len(existing_exercises)}")
                
                if existing_exercises:
                    print("\nExisting exercises:")
                    for ex in existing_exercises:
                        print(f"  - ID {ex.id}: {ex.title} (order: {ex.order_index})")
                
                print(f"\nReady to upsert {len(tasks)} tasks:")
                for task in tasks:
                    print(f"  - Task {task['order_index']}: {task['title']} ({task['difficulty']})")
                
                print("\n✓ PASS: Dry run completed successfully")
                print("  Note: No changes were made to the database")
                
                self.results.append({
                    'test': 'Dry Run',
                    'passed': True,
                    'details': f"Ready to upsert {len(tasks)} tasks, {len(existing_exercises)} existing exercises"
                })
                
                return True
                
        except Exception as e:
            print(f"✗ FAIL: Dry run error: {str(e)}")
            import traceback
            traceback.print_exc()
            self.results.append({
                'test': 'Dry Run',
                'passed': False,
                'details': f"Error: {str(e)}"
            })
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("\n" + "="*80)
        print("LESSON 6 TASK UPSERT - TEST SUITE")
        print("="*80)
        print(f"Testing file: {self.markdown_file}")
        
        # Run tests in order
        self.test_file_exists()
        self.test_parse_tasks()
        self.test_database_connection()
        self.test_slug_generation()
        self.test_dry_run()
        
        # Print summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)
        
        print(f"\nTotal tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success rate: {(passed/total*100):.1f}%")
        
        print("\nDetailed results:")
        for i, result in enumerate(self.results, 1):
            status = "✓ PASS" if result['passed'] else "✗ FAIL"
            print(f"  {i}. {result['test']}: {status}")
            print(f"     {result['details']}")
        
        all_passed = passed == total
        
        if all_passed:
            print("\n" + "="*80)
            print("✓ ALL TESTS PASSED - READY TO RUN UPSERT")
            print("="*80)
            print("\nTo run the actual upsert, execute:")
            print("  python upsert_lesson6_tasks.py")
        else:
            print("\n" + "="*80)
            print("✗ SOME TESTS FAILED - FIX ISSUES BEFORE RUNNING UPSERT")
            print("="*80)
        
        return all_passed


def main():
    """Run the test suite."""
    tester = TestTaskUpserter()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
