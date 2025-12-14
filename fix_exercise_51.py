"""Fix test cases for exercise 51."""

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
    print(f"Description: {exercise.description}")
    print(f"\nCurrent test_cases (invalid): {exercise.test_cases}")
    
    # Based on the description "testing. So print hi", create appropriate test case
    proper_test_cases = [
        {
            "type": "assert_output",
            "description": "Should print 'hi'",
            "expected": "hi\n"  # Python print adds newline
        }
    ]
    
    print(f"\n{'='*60}")
    print("Creating proper test cases:")
    print(json.dumps(proper_test_cases, indent=2))
    
    # Update the exercise
    exercise.test_cases = json.dumps(proper_test_cases)
    
    # Also fix the starter code if needed
    if exercise.starter_code == "print":
        print("\n⚠️  Starter code is incomplete: 'print'")
        print("Updating to: '# Write your code here\\nprint(\"hi\")'")
        exercise.starter_code = "# Write your code here\nprint(\"hi\")"
    
    db.session.commit()
    
    print("\n✅ Exercise updated successfully!")
    print("\nTest the exercise now at:")
    print(f"http://127.0.0.1:5000/python-practice/exercise/{exercise_id}?course_id=1&lesson_id=14")
