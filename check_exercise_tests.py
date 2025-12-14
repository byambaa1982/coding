"""Check and add test cases for exercise."""

from app import create_app
from app.extensions import db
from app.models import Exercise
import json

app = create_app()

with app.app_context():
    exercise_id = 51
    exercise = Exercise.query.get(exercise_id)
    
    if not exercise:
        print(f"❌ Exercise {exercise_id} not found!")
        exit(1)
    
    print(f"\n📝 Exercise: {exercise.title}")
    print(f"Description: {exercise.description[:100]}...")
    print(f"\nStarter Code:")
    print(exercise.starter_code if exercise.starter_code else "None")
    print(f"\n{'='*60}")
    
    # Check test cases
    print(f"\nTest Cases:")
    if exercise.test_cases:
        try:
            test_cases = json.loads(exercise.test_cases)
            print(f"✅ Found test cases data")
            print(f"Type: {type(test_cases)}")
            print(f"Content: {test_cases}")
            print(f"\n{'='*60}")
            
            # Try to parse as list
            if isinstance(test_cases, list):
                print(f"Test cases is a list with {len(test_cases)} items")
                for i, test in enumerate(test_cases, 1):
                    print(f"\n  Test {i}:")
                    print(f"    Type: {type(test)}")
                    print(f"    Content: {test}")
                    if isinstance(test, dict):
                        print(f"    Description: {test.get('description', 'N/A')}")
                        print(f"    Test Type: {test.get('type', 'N/A')}")
                        if test.get('input'):
                            print(f"    Input: {test.get('input')}")
                        if test.get('expected'):
                            print(f"    Expected: {test.get('expected')}")
            else:
                print(f"⚠️  Test cases is not a list, it's: {type(test_cases)}")
                print(f"Content: {test_cases}")
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing test cases: {e}")
            print(f"Raw test_cases content: {exercise.test_cases}")
    else:
        print("❌ No test cases defined!")
        print("\n" + "="*60)
        print("This is why the test results don't show up!")
        print("\nWould you like to add sample test cases? (for demonstration)")
        print("\nExample test cases structure:")
        print(json.dumps([
            {
                "type": "assert_output",
                "description": "Test basic output",
                "expected": "Hello, World!"
            },
            {
                "type": "assert_function",
                "description": "Test function returns correct value",
                "function_name": "add",
                "input": [2, 3],
                "expected": 5
            }
        ], indent=2))
        
        print("\n" + "="*60)
        print("\nTo add test cases, use the instructor panel:")
        print(f"http://localhost:5000/instructor/exercise/{exercise_id}/edit")
        print("\nOr update directly in database:")
        print(f"UPDATE exercises SET test_cases = '[...]' WHERE id = {exercise_id};")
