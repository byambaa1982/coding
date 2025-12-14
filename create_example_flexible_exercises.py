"""
Create example exercises with flexible test cases.
Run this to add example exercises to the database.
"""

from app import create_app
from app.extensions import db
from app.models import Exercise, Lesson
import json

app = create_app()

with app.app_context():
    # Get a lesson to attach exercises to
    lesson = Lesson.query.first()
    if not lesson:
        print("❌ No lessons found. Create a lesson first.")
        exit(1)
    
    print(f"Adding exercises to lesson: {lesson.title}")
    print(f"Tutorial: {lesson.tutorial.title if lesson.tutorial else 'N/A'}")
    
    # Example 1: Case-insensitive output
    ex1 = Exercise(
        tutorial_id=lesson.tutorial_id,
        lesson_id=lesson.id,
        title="Greeting Exercise (Case Insensitive)",
        slug="greeting-case-insensitive",
        description="Write a program that prints 'hello'. You can use any case (Hello, HELLO, hello, etc.)",
        exercise_type="python",
        difficulty="easy",
        points=10,
        order_index=100,
        starter_code="# Write your code here\nprint('hello')",
        test_cases=json.dumps([
            {
                "type": "assert_output",
                "description": "Should print 'hello' (case insensitive)",
                "expected": "hello",
                "case_sensitive": False,
                "strip_whitespace": True
            }
        ])
    )
    
    # Example 2: Function-based (user can choose any values)
    ex2 = Exercise(
        tutorial_id=lesson.tutorial_id,
        lesson_id=lesson.id,
        title="Get Second Item Function",
        slug="get-second-item",
        description="""Create a function called 'get_second' that takes a list and returns the second item (index 1).
        
Example:
get_second(['cat', 'dog', 'bird']) should return 'dog'
get_second([10, 20, 30]) should return 20""",
        exercise_type="python",
        difficulty="easy",
        points=15,
        order_index=101,
        starter_code="""# Write your function here
def get_second(items):
    # Your code here
    pass
""",
        test_cases=json.dumps([
            {
                "type": "assert_function",
                "description": "Test with animal names",
                "function_name": "get_second",
                "input": [["cat", "dog", "bird"]],
                "expected": "dog"
            },
            {
                "type": "assert_function",
                "description": "Test with numbers",
                "function_name": "get_second",
                "input": [[1, 2, 3]],
                "expected": 2
            },
            {
                "type": "assert_function",
                "description": "Test with fruits",
                "function_name": "get_second",
                "input": [["apple", "banana", "cherry"]],
                "expected": "banana"
            }
        ])
    )
    
    # Example 3: Variable checking (flexible content)
    ex3 = Exercise(
        tutorial_id=lesson.tutorial_id,
        lesson_id=lesson.id,
        title="Create Animal List",
        slug="create-animal-list",
        description="""Create a list called 'animals' with exactly 3 animal names of your choice.
        
Examples of valid solutions:
- animals = ['cat', 'dog', 'bird']
- animals = ['elephant', 'lion', 'tiger']
- animals = ['fish', 'rabbit', 'hamster']""",
        exercise_type="python",
        difficulty="easy",
        points=10,
        order_index=102,
        starter_code="# Create your list here\nanimals = ",
        test_cases=json.dumps([
            {
                "type": "assert_variable_exists",
                "description": "Variable 'animals' should exist",
                "variable_name": "animals"
            },
            {
                "type": "assert_variable_type",
                "description": "Variable 'animals' should be a list",
                "variable_name": "animals",
                "expected_type": "list"
            },
            {
                "type": "assert_variable_length",
                "description": "List should have exactly 3 items",
                "variable_name": "animals",
                "expected_length": 3
            }
        ])
    )
    
    # Example 4: Contains check (flexible output)
    ex4 = Exercise(
        tutorial_id=lesson.tutorial_id,
        lesson_id=lesson.id,
        title="Print Your Name",
        slug="print-your-name",
        description="Write a program that prints your name. Any name is acceptable!",
        exercise_type="python",
        difficulty="easy",
        points=5,
        order_index=103,
        starter_code="# Write your code here\nname = 'Your Name'\nprint(name)",
        test_cases=json.dumps([
            {
                "type": "assert_custom",
                "description": "Should print at least one word",
                "code": "len(captured_output.getvalue().strip()) > 0"
            }
        ])
    )
    
    # Example 5: Multiple acceptable answers
    ex5 = Exercise(
        tutorial_id=lesson.tutorial_id,
        lesson_id=lesson.id,
        title="Greeting Function (Multiple Styles)",
        slug="greeting-multiple-styles",
        description="""Create a function called 'greet' that takes a name and returns a greeting.
        
Acceptable formats:
- "Hello, [name]!"
- "Hi, [name]!"
- "Hey, [name]!"
        
Example:
greet("Alice") could return "Hello, Alice!" or "Hi, Alice!" or "Hey, Alice!"
""",
        exercise_type="python",
        difficulty="easy",
        points=15,
        order_index=104,
        starter_code="""# Write your function here
def greet(name):
    # Your code here
    pass
""",
        test_cases=json.dumps([
            {
                "type": "assert_function",
                "description": "Should return a valid greeting for Alice",
                "function_name": "greet",
                "input": ["Alice"],
                "expected_any_of": [
                    "Hello, Alice!",
                    "Hi, Alice!",
                    "Hey, Alice!"
                ]
            },
            {
                "type": "assert_function",
                "description": "Should return a valid greeting for Bob",
                "function_name": "greet",
                "input": ["Bob"],
                "expected_any_of": [
                    "Hello, Bob!",
                    "Hi, Bob!",
                    "Hey, Bob!"
                ]
            }
        ])
    )
    
    # Add all exercises
    exercises = [ex1, ex2, ex3, ex4, ex5]
    for ex in exercises:
        db.session.add(ex)
    
    db.session.commit()
    
    print("\n✅ Successfully added 5 example exercises:")
    for ex in exercises:
        print(f"   - {ex.title}")
        print(f"     Test approach: {json.loads(ex.test_cases)[0]['type']}")
    
    print("\n📝 These exercises demonstrate different test approaches:")
    print("   1. Case-insensitive output")
    print("   2. Function-based (tests behavior, not specific values)")
    print("   3. Variable checking (flexible content)")
    print("   4. Custom validation")
    print("   5. Multiple acceptable answers")
