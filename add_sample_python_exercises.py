# add_sample_python_exercises.py
"""Add sample Python exercises for testing Phase 5."""

import json
from app import create_app
from app.extensions import db
from app.models import Exercise, NewTutorial, Lesson


def add_sample_exercises():
    """Add sample Python exercises."""
    app = create_app()
    
    with app.app_context():
        print("Adding sample Python exercises...")
        
        try:
            # Get a tutorial (or create a sample one)
            tutorial = NewTutorial.query.filter_by(course_type='python').first()
            
            if not tutorial:
                print("Creating sample Python tutorial...")
                tutorial = NewTutorial(
                    title='Python Fundamentals',
                    slug='python-fundamentals',
                    description='Learn Python programming from scratch',
                    course_type='python',
                    category='Programming',
                    difficulty_level='beginner',
                    price=29.99,
                    status='published',
                    instructor_id=1  # Adjust as needed
                )
                db.session.add(tutorial)
                db.session.commit()
            
            # Get or create a lesson
            lesson = Lesson.query.filter_by(tutorial_id=tutorial.id).first()
            
            if not lesson:
                print("Creating sample lesson...")
                lesson = Lesson(
                    tutorial_id=tutorial.id,
                    title='Python Basics',
                    slug='python-basics',
                    description='Introduction to Python programming',
                    content_type='text',
                    order_index=1
                )
                db.session.add(lesson)
                db.session.commit()
            
            # Exercise 1: Hello World
            exercise1 = Exercise(
                tutorial_id=tutorial.id,
                lesson_id=lesson.id,
                title='Hello World',
                slug='hello-world',
                description='''<h5>Your First Python Program</h5>
                <p>Write a function called <code>greet()</code> that returns the string "Hello, World!".</p>
                <p><strong>Example:</strong></p>
                <pre>greet() -> "Hello, World!"</pre>''',
                exercise_type='python',
                difficulty='easy',
                starter_code='''def greet():
    # Write your code here
    pass
''',
                solution_code='''def greet():
    return "Hello, World!"
''',
                test_cases=json.dumps([
                    {
                        'test_number': 1,
                        'description': 'Function returns correct greeting',
                        'function_name': 'greet',
                        'input': [],
                        'expected': 'Hello, World!'
                    }
                ]),
                hints=json.dumps([
                    'Use the return statement to return a string.',
                    'The string should be exactly "Hello, World!" with proper capitalization and punctuation.'
                ]),
                order_index=1,
                points=10
            )
            
            # Exercise 2: Add Two Numbers
            exercise2 = Exercise(
                tutorial_id=tutorial.id,
                lesson_id=lesson.id,
                title='Add Two Numbers',
                slug='add-two-numbers',
                description='''<h5>Basic Arithmetic</h5>
                <p>Write a function called <code>add_numbers(a, b)</code> that takes two numbers and returns their sum.</p>
                <p><strong>Examples:</strong></p>
                <pre>add_numbers(2, 3) -> 5
add_numbers(10, 15) -> 25
add_numbers(-5, 5) -> 0</pre>''',
                exercise_type='python',
                difficulty='easy',
                starter_code='''def add_numbers(a, b):
    # Write your code here
    pass
''',
                solution_code='''def add_numbers(a, b):
    return a + b
''',
                test_cases=json.dumps([
                    {
                        'test_number': 1,
                        'description': 'Add positive numbers',
                        'function_name': 'add_numbers',
                        'input': [2, 3],
                        'expected': 5
                    },
                    {
                        'test_number': 2,
                        'description': 'Add larger numbers',
                        'function_name': 'add_numbers',
                        'input': [10, 15],
                        'expected': 25
                    },
                    {
                        'test_number': 3,
                        'description': 'Add negative and positive',
                        'function_name': 'add_numbers',
                        'input': [-5, 5],
                        'expected': 0
                    }
                ]),
                hints=json.dumps([
                    'Use the + operator to add two numbers.',
                    'Remember to return the result, not print it.'
                ]),
                order_index=2,
                points=10
            )
            
            # Exercise 3: Check Even or Odd
            exercise3 = Exercise(
                tutorial_id=tutorial.id,
                lesson_id=lesson.id,
                title='Even or Odd',
                slug='even-or-odd',
                description='''<h5>Conditional Logic</h5>
                <p>Write a function called <code>is_even(number)</code> that returns <code>True</code> if the number is even, and <code>False</code> if it's odd.</p>
                <p><strong>Examples:</strong></p>
                <pre>is_even(4) -> True
is_even(7) -> False
is_even(0) -> True
is_even(-2) -> True</pre>''',
                exercise_type='python',
                difficulty='easy',
                starter_code='''def is_even(number):
    # Write your code here
    pass
''',
                solution_code='''def is_even(number):
    return number % 2 == 0
''',
                test_cases=json.dumps([
                    {
                        'test_number': 1,
                        'description': 'Test even positive number',
                        'function_name': 'is_even',
                        'input': [4],
                        'expected': True
                    },
                    {
                        'test_number': 2,
                        'description': 'Test odd positive number',
                        'function_name': 'is_even',
                        'input': [7],
                        'expected': False
                    },
                    {
                        'test_number': 3,
                        'description': 'Test zero',
                        'function_name': 'is_even',
                        'input': [0],
                        'expected': True
                    },
                    {
                        'test_number': 4,
                        'description': 'Test negative even number',
                        'function_name': 'is_even',
                        'input': [-2],
                        'expected': True
                    }
                ]),
                hints=json.dumps([
                    'Use the modulo operator (%) to find the remainder of division by 2.',
                    'If the remainder is 0, the number is even.'
                ]),
                order_index=3,
                points=15
            )
            
            # Exercise 4: Sum of List
            exercise4 = Exercise(
                tutorial_id=tutorial.id,
                lesson_id=lesson.id,
                title='Sum of List',
                slug='sum-of-list',
                description='''<h5>Working with Lists</h5>
                <p>Write a function called <code>sum_list(numbers)</code> that takes a list of numbers and returns their sum.</p>
                <p><strong>Examples:</strong></p>
                <pre>sum_list([1, 2, 3, 4, 5]) -> 15
sum_list([10, 20, 30]) -> 60
sum_list([]) -> 0</pre>''',
                exercise_type='python',
                difficulty='medium',
                starter_code='''def sum_list(numbers):
    # Write your code here
    pass
''',
                solution_code='''def sum_list(numbers):
    return sum(numbers)
    
# Alternative solution without using sum():
# def sum_list(numbers):
#     total = 0
#     for num in numbers:
#         total += num
#     return total
''',
                test_cases=json.dumps([
                    {
                        'test_number': 1,
                        'description': 'Sum small list',
                        'function_name': 'sum_list',
                        'input': [[1, 2, 3, 4, 5]],
                        'expected': 15
                    },
                    {
                        'test_number': 2,
                        'description': 'Sum larger numbers',
                        'function_name': 'sum_list',
                        'input': [[10, 20, 30]],
                        'expected': 60
                    },
                    {
                        'test_number': 3,
                        'description': 'Sum empty list',
                        'function_name': 'sum_list',
                        'input': [[]],
                        'expected': 0
                    }
                ]),
                hints=json.dumps([
                    'You can use Python\'s built-in sum() function.',
                    'Alternatively, use a for loop to iterate through the list and add each number to a total.'
                ]),
                order_index=4,
                points=20
            )
            
            # Exercise 5: Reverse String
            exercise5 = Exercise(
                tutorial_id=tutorial.id,
                lesson_id=lesson.id,
                title='Reverse String',
                slug='reverse-string',
                description='''<h5>String Manipulation</h5>
                <p>Write a function called <code>reverse_string(text)</code> that takes a string and returns it reversed.</p>
                <p><strong>Examples:</strong></p>
                <pre>reverse_string("hello") -> "olleh"
reverse_string("Python") -> "nohtyP"
reverse_string("") -> ""</pre>''',
                exercise_type='python',
                difficulty='medium',
                starter_code='''def reverse_string(text):
    # Write your code here
    pass
''',
                solution_code='''def reverse_string(text):
    return text[::-1]
    
# Alternative solutions:
# def reverse_string(text):
#     return ''.join(reversed(text))
#
# def reverse_string(text):
#     result = ''
#     for char in text:
#         result = char + result
#     return result
''',
                test_cases=json.dumps([
                    {
                        'test_number': 1,
                        'description': 'Reverse simple word',
                        'function_name': 'reverse_string',
                        'input': ['hello'],
                        'expected': 'olleh'
                    },
                    {
                        'test_number': 2,
                        'description': 'Reverse capitalized word',
                        'function_name': 'reverse_string',
                        'input': ['Python'],
                        'expected': 'nohtyP'
                    },
                    {
                        'test_number': 3,
                        'description': 'Reverse empty string',
                        'function_name': 'reverse_string',
                        'input': [''],
                        'expected': ''
                    }
                ]),
                hints=json.dumps([
                    'Python strings can be sliced using the notation string[start:end:step].',
                    'Use [::-1] to reverse a string.',
                    'Alternatively, you can use the reversed() function or a loop.'
                ]),
                order_index=5,
                points=20
            )
            
            # Add all exercises
            exercises = [exercise1, exercise2, exercise3, exercise4, exercise5]
            
            for exercise in exercises:
                existing = Exercise.query.filter_by(slug=exercise.slug).first()
                if not existing:
                    db.session.add(exercise)
                    print(f"✓ Added exercise: {exercise.title}")
                else:
                    print(f"- Exercise already exists: {exercise.title}")
            
            db.session.commit()
            print("\n✓ Sample Python exercises added successfully!")
            print(f"\nTotal exercises: {Exercise.query.filter_by(exercise_type='python').count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error adding exercises: {str(e)}")
            raise


if __name__ == '__main__':
    add_sample_exercises()
