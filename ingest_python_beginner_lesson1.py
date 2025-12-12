"""
Script to ingest Python Beginner Tutorial - Lesson 1 into the database.
Instructor: Byamba Enkhbat (byambaa1982@gmail.com)
Course: Free Python Programming for Beginners
"""

from app import create_app
from app.extensions import db
from app.models import TutorialUser, NewTutorial, Lesson, Exercise
from datetime import datetime


def create_instructor():
    """Create instructor user if not exists."""
    instructor = TutorialUser.query.filter_by(email='byambaa1982@gmail.com').first()
    
    if not instructor:
        instructor = TutorialUser(
            email='byambaa1982@gmail.com',
            username='byamba_enkhbat',
            full_name='Byamba Enkhbat',
            is_instructor=True,
            is_admin=True,
            email_verified=True,
            bio='Python programming instructor passionate about teaching beginners to code through hands-on practice and real-world examples.'
        )
        instructor.set_password('instructor123')
        db.session.add(instructor)
        db.session.commit()
        print(f"✅ Created instructor: {instructor.full_name} ({instructor.email})")
    else:
        print(f"✅ Instructor already exists: {instructor.full_name} ({instructor.email})")
    
    return instructor


def create_python_beginner_tutorial(instructor):
    """Create the Python Beginner Tutorial."""
    tutorial = NewTutorial.query.filter_by(slug='python-beginner-fundamentals').first()
    
    if not tutorial:
        tutorial = NewTutorial(
            instructor_id=instructor.id,
            title='Python Programming for Complete Beginners',
            slug='python-beginner-fundamentals',
            description="""Learn Python programming from scratch with this comprehensive beginner course. 
            Master fundamental concepts including syntax, variables, control flow, data structures, and functions 
            through practical exercises and real-world examples. Perfect for absolute beginners with no prior 
            programming experience. This hands-on course includes 10 practice exercises with solutions and test cases 
            to help you build confidence and coding skills.""",
            short_description='Master Python fundamentals through hands-on practice - perfect for complete beginners with zero coding experience.',
            course_type='python',
            category='Programming',
            difficulty_level='beginner',
            language='en',
            price=0.00,
            currency='USD',
            is_free=True,
            status='published',
            is_featured=True,
            estimated_duration_hours=1.0,
            total_lessons=1,
            tags='python,beginner,programming,fundamentals,free,coding,syntax,variables,functions',
            published_at=datetime.utcnow()
        )
        db.session.add(tutorial)
        db.session.commit()
        db.session.refresh(tutorial)  # Refresh to ensure we have the ID
        print(f"✅ Created tutorial: {tutorial.title} (FREE) with ID: {tutorial.id}")
    else:
        print(f"✅ Tutorial already exists: {tutorial.title} with ID: {tutorial.id}")
    
    return tutorial


def create_lesson1(tutorial):
    """Create Lesson 1: Introduction to Python Programming."""
    lesson = Lesson.query.filter_by(
        tutorial_id=tutorial.id,
        slug='python-introduction-lesson1'
    ).first()
    
    if not lesson:
        lesson_content = """# Python Beginner Tutorial - Lesson 1
## Introduction to Python Programming

**Course**: Python for Beginners  
**Lesson**: 1 of 8  
**Duration**: 45-60 minutes  
**Difficulty**: Beginner  
**Prerequisites**: None

---

## 🎯 Learning Objectives

By the end of this lesson, you will be able to:
- Understand basic Python syntax and write simple programs
- Create and use variables to store data
- Use control flow statements (if/else, loops)
- Work with basic data structures (lists, dictionaries)
- Define and call functions

---

## 📚 Lesson Content

### 1. Python Syntax & Your First Program

Python is known for its clean, readable syntax. Let's start with the traditional first program:

```python
print("Hello, World!")
```

**Key Points:**
- `print()` is a built-in function that displays output
- Strings are enclosed in quotes (single `'` or double `"`)
- No semicolons needed at the end of lines!
- Indentation matters in Python (we'll see why soon)

**Try it yourself:**
```python
# This is a comment - Python ignores it
print("Welcome to Python!")
print("Python is awesome")  # You can add comments after code too
```

---

### 2. Variables - Storing Information

Variables are containers for storing data. In Python, you don't need to declare types!

```python
# Numbers
age = 25
price = 19.99
temperature = -5

# Strings (text)
name = "Alice"
city = 'New York'

# Boolean (True/False)
is_student = True
has_license = False

# Print variables
print(name)
print("Age:", age)
print(f"My name is {name} and I am {age} years old")  # f-string formatting
```

**Variable Naming Rules:**
- Must start with a letter or underscore
- Can contain letters, numbers, and underscores
- Case-sensitive (`name` ≠ `Name`)
- Use descriptive names: `student_count` not `sc`

**Basic Operations:**
```python
# Math operations
x = 10
y = 3

sum_result = x + y      # 13
difference = x - y       # 7
product = x * y          # 30
quotient = x / y         # 3.333...
integer_div = x // y     # 3 (floor division)
remainder = x % y        # 1 (modulo)
power = x ** y           # 1000 (10 to the power of 3)

# String operations
first_name = "John"
last_name = "Doe"
full_name = first_name + " " + last_name  # "John Doe" (concatenation)
greeting = "Hello " * 3  # "Hello Hello Hello "
```

---

### 3. Control Flow - Making Decisions

#### If/Else Statements

```python
age = 18

if age >= 18:
    print("You are an adult")
    print("You can vote")
else:
    print("You are a minor")
    print("You cannot vote yet")
```

**Key Points:**
- Conditions use comparison operators: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Colon `:` after the condition
- Indented code block (4 spaces) executes if condition is True

**Multiple Conditions:**
```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"Your grade is: {grade}")
```

**Logical Operators:**
```python
age = 20
has_id = True

# AND - both conditions must be True
if age >= 18 and has_id:
    print("You can enter")

# OR - at least one condition must be True
is_weekend = True
is_holiday = False

if is_weekend or is_holiday:
    print("Time to relax!")

# NOT - inverts the condition
is_raining = False
if not is_raining:
    print("Go for a walk!")
```

#### Loops - Repeating Actions

**For Loop:**
```python
# Loop through a range of numbers
for i in range(5):
    print(i)  # Prints 0, 1, 2, 3, 4

# Loop through a range with start and stop
for i in range(1, 6):
    print(i)  # Prints 1, 2, 3, 4, 5

# Loop through a range with step
for i in range(0, 10, 2):
    print(i)  # Prints 0, 2, 4, 6, 8
```

**While Loop:**
```python
count = 0
while count < 5:
    print(f"Count is: {count}")
    count += 1  # Same as count = count + 1

print("Done!")
```

**Break and Continue:**
```python
# Break - exits the loop
for i in range(10):
    if i == 5:
        break
    print(i)  # Prints 0, 1, 2, 3, 4

# Continue - skips to next iteration
for i in range(5):
    if i == 2:
        continue
    print(i)  # Prints 0, 1, 3, 4 (skips 2)
```

---

### 4. Data Structures - Organizing Data

#### Lists - Ordered Collections

```python
# Creating lists
fruits = ["apple", "banana", "orange"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", True, 3.14]

# Accessing elements (0-indexed)
print(fruits[0])   # "apple"
print(fruits[1])   # "banana"
print(fruits[-1])  # "orange" (last item)

# List length
print(len(fruits))  # 3

# Adding elements
fruits.append("grape")      # Add to end
fruits.insert(1, "mango")   # Insert at position 1

# Removing elements
fruits.remove("banana")     # Remove by value
last_fruit = fruits.pop()   # Remove and return last item

# Looping through lists
for fruit in fruits:
    print(fruit)

# List slicing
numbers = [0, 1, 2, 3, 4, 5]
print(numbers[1:4])   # [1, 2, 3]
print(numbers[:3])    # [0, 1, 2] (from start)
print(numbers[3:])    # [3, 4, 5] (to end)
```

#### Dictionaries - Key-Value Pairs

```python
# Creating dictionaries
student = {
    "name": "Alice",
    "age": 20,
    "grade": "A",
    "courses": ["Math", "Science"]
}

# Accessing values
print(student["name"])      # "Alice"
print(student.get("age"))   # 20

# Adding/Updating values
student["email"] = "alice@email.com"
student["age"] = 21

# Removing items
del student["grade"]

# Checking if key exists
if "email" in student:
    print("Email found!")

# Looping through dictionaries
for key, value in student.items():
    print(f"{key}: {value}")

# Get all keys and values
keys = student.keys()
values = student.values()
```

---

### 5. Functions - Reusable Code

Functions help you organize code and avoid repetition.

**Basic Function:**
```python
def greet():
    print("Hello!")
    print("Welcome to Python")

# Calling the function
greet()
```

**Functions with Parameters:**
```python
def greet_person(name):
    print(f"Hello, {name}!")

greet_person("Alice")
greet_person("Bob")
```

**Functions with Return Values:**
```python
def add(a, b):
    result = a + b
    return result

sum_result = add(5, 3)
print(sum_result)  # 8

# Multiple parameters
def calculate_area(length, width):
    area = length * width
    return area

room_area = calculate_area(10, 15)
print(f"Room area: {room_area} sq ft")
```

**Default Parameters:**
```python
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

greet("Alice")              # Uses default: "Hello, Alice!"
greet("Bob", "Hi")          # Custom greeting: "Hi, Bob!"
```

**Return Multiple Values:**
```python
def get_min_max(numbers):
    return min(numbers), max(numbers)

minimum, maximum = get_min_max([3, 1, 4, 1, 5, 9, 2])
print(f"Min: {minimum}, Max: {maximum}")
```

---

## 💡 Quick Reference

### Common Built-in Functions
```python
print()           # Display output
len()             # Get length of a collection
type()            # Get type of a variable
input()           # Get user input
int(), float()    # Convert to number
str()             # Convert to string
range()           # Generate sequence of numbers
sum()             # Sum of numbers
min(), max()      # Minimum/maximum value
```

### String Methods
```python
text = "Hello World"
text.lower()      # "hello world"
text.upper()      # "HELLO WORLD"
text.strip()      # Remove whitespace
text.split()      # Split into list
text.replace("Hello", "Hi")  # "Hi World"
```

---

## 🎓 Key Takeaways

✅ Python uses clean, readable syntax with meaningful indentation
✅ Variables store data without needing type declarations
✅ Control flow (if/else, loops) controls program execution
✅ Lists store ordered collections, dictionaries store key-value pairs
✅ Functions make code reusable and organized
✅ Practice is key to mastering programming!

---

## 🚀 Next Steps

Ready to practice? Complete the 10 exercises below to reinforce what you've learned!

**Coming in Lesson 2:**
- Advanced list operations and comprehensions
- Working with files (reading and writing)
- Exception handling (try/except)
- Introduction to modules and libraries

---

**Good luck with your Python journey! 🐍**
"""
        
        lesson = Lesson(
            tutorial_id=tutorial.id,
            title='Introduction to Python Programming',
            slug='python-introduction-lesson1',
            description='Learn Python syntax, variables, control flow, data structures, and functions with hands-on examples',
            content_type='text',
            content=lesson_content,
            section_name='Section 1: Python Fundamentals',
            order_index=1,
            is_free_preview=True,
            estimated_duration_minutes=60
        )
        db.session.add(lesson)
        db.session.commit()
        print(f"✅ Created lesson: {lesson.title}")
    else:
        print(f"✅ Lesson already exists: {lesson.title}")
    
    return lesson


def create_exercises(tutorial, lesson):
    """Create the 10 practice exercises for Lesson 1."""
    exercises_data = [
        {
            'title': 'Exercise 1: Variables and Math',
            'slug': 'exercise-1-variables-math',
            'description': 'Practice using variables and basic math operations',
            'difficulty': 'easy',
            'order_index': 1,
            'instructions': """Create a program that:
1. Stores your name, age, and favorite number in variables
2. Calculates what year you were born (current year - age)
3. Calculates double your favorite number
4. Prints all results with descriptive messages

Expected Output:
```
Name: Alice
Age: 25
Birth Year: 2000
Favorite Number: 7
Double: 14
```""",
            'starter_code': """# Your code here
name = "Alice"
age = 25
# ... complete the rest""",
            'solution_code': """name = "Alice"
age = 25
favorite_number = 7

current_year = 2025
birth_year = current_year - age
double_favorite = favorite_number * 2

print(f"Name: {name}")
print(f"Age: {age}")
print(f"Birth Year: {birth_year}")
print(f"Favorite Number: {favorite_number}")
print(f"Double: {double_favorite}")""",
            'test_cases': [
                {'input': '', 'expected_output': 'Name:', 'description': 'Prints name'},
                {'input': '', 'expected_output': 'Age:', 'description': 'Prints age'},
                {'input': '', 'expected_output': 'Birth Year:', 'description': 'Calculates birth year'},
            ]
        },
        {
            'title': 'Exercise 2: Temperature Converter',
            'slug': 'exercise-2-temperature-converter',
            'description': 'Create a function to convert Celsius to Fahrenheit',
            'difficulty': 'easy',
            'order_index': 2,
            'instructions': """Write a function `celsius_to_fahrenheit()` that:
- Takes a temperature in Celsius as parameter
- Converts it to Fahrenheit using formula: F = (C × 9/5) + 32
- Returns the Fahrenheit temperature
- Test with 0, 25, and 100 degrees Celsius

Expected Output:
```
0°C = 32.0°F
25°C = 77.0°F
100°C = 212.0°F
```""",
            'starter_code': """def celsius_to_fahrenheit(celsius):
    # Your code here
    pass

# Test
temperatures = [0, 25, 100]
for temp in temperatures:
    result = celsius_to_fahrenheit(temp)
    print(f"{temp}°C = {result}°F")""",
            'solution_code': """def celsius_to_fahrenheit(celsius):
    fahrenheit = (celsius * 9/5) + 32
    return fahrenheit

# Test
temperatures = [0, 25, 100]
for temp in temperatures:
    result = celsius_to_fahrenheit(temp)
    print(f"{temp}°C = {result}°F")""",
            'test_cases': [
                {'input': '0', 'expected_output': '32.0', 'description': 'Converts 0°C to 32°F'},
                {'input': '100', 'expected_output': '212.0', 'description': 'Converts 100°C to 212°F'},
            ]
        },
        {
            'title': 'Exercise 3: Grade Calculator',
            'slug': 'exercise-3-grade-calculator',
            'description': 'Build a function that converts numeric scores to letter grades',
            'difficulty': 'medium',
            'order_index': 3,
            'instructions': """Create a function `calculate_grade()` that:
- Takes a score (0-100) as parameter
- Returns the letter grade:
  - A: 90-100
  - B: 80-89
  - C: 70-79
  - D: 60-69
  - F: 0-59
- Test with scores: 95, 82, 71, 65, 55""",
            'starter_code': """def calculate_grade(score):
    # Your code here
    pass

# Test
scores = [95, 82, 71, 65, 55]
for score in scores:
    grade = calculate_grade(score)
    print(f"Score {score}: Grade {grade}")""",
            'solution_code': """def calculate_grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

# Test
scores = [95, 82, 71, 65, 55]
for score in scores:
    grade = calculate_grade(score)
    print(f"Score {score}: Grade {grade}")""",
            'test_cases': [
                {'input': '95', 'expected_output': 'A', 'description': 'Returns A for 95'},
                {'input': '85', 'expected_output': 'B', 'description': 'Returns B for 85'},
                {'input': '75', 'expected_output': 'C', 'description': 'Returns C for 75'},
            ]
        },
        {
            'title': 'Exercise 4: Shopping List',
            'slug': 'exercise-4-shopping-list',
            'description': 'Practice working with lists',
            'difficulty': 'medium',
            'order_index': 4,
            'instructions': """Create a program that:
1. Creates an empty list called `shopping_list`
2. Adds at least 5 items to the list
3. Prints the total number of items
4. Prints each item with its position number
5. Removes one item from the list
6. Prints the updated list""",
            'starter_code': """shopping_list = []
# Your code here""",
            'solution_code': """shopping_list = []
shopping_list.append("Apples")
shopping_list.append("Bread")
shopping_list.append("Milk")
shopping_list.append("Eggs")
shopping_list.append("Cheese")

print(f"Shopping List ({len(shopping_list)} items):")
for i, item in enumerate(shopping_list, 1):
    print(f"{i}. {item}")

shopping_list.remove("Milk")

print(f"\\nAfter removing Milk:")
print(f"Shopping List ({len(shopping_list)} items):")
for i, item in enumerate(shopping_list, 1):
    print(f"{i}. {item}")""",
            'test_cases': []
        },
        {
            'title': 'Exercise 5: Even Numbers',
            'slug': 'exercise-5-even-numbers',
            'description': 'Print all even numbers in a range',
            'difficulty': 'medium',
            'order_index': 5,
            'instructions': """Write a function `print_even_numbers()` that:
- Takes two parameters: start and end
- Prints all even numbers between start and end (inclusive)
- Uses a for loop
- Test with start=1, end=20""",
            'starter_code': """def print_even_numbers(start, end):
    # Your code here
    pass

print_even_numbers(1, 20)""",
            'solution_code': """def print_even_numbers(start, end):
    print(f"Even numbers from {start} to {end}:")
    for number in range(start, end + 1):
        if number % 2 == 0:
            print(number, end=" ")
    print()

print_even_numbers(1, 20)""",
            'test_cases': []
        },
        {
            'title': 'Exercise 6: Student Record',
            'slug': 'exercise-6-student-record',
            'description': 'Work with dictionaries to store student information',
            'difficulty': 'medium',
            'order_index': 6,
            'instructions': """Create a program that:
1. Creates a dictionary for a student with keys: name, age, grade, subjects (list)
2. Prints each key-value pair
3. Adds a new key "email" with a value
4. Updates the grade
5. Prints the final dictionary""",
            'starter_code': """# Your code here
student = {}""",
            'solution_code': """student = {
    "name": "John Doe",
    "age": 16,
    "grade": 10,
    "subjects": ["Math", "Science", "English"]
}

for key, value in student.items():
    print(f"{key}: {value}")

student["email"] = "john@school.com"
student["grade"] = 11

print("\\nAfter updates:")
for key, value in student.items():
    print(f"{key}: {value}")""",
            'test_cases': []
        },
        {
            'title': 'Exercise 7: FizzBuzz Classic',
            'slug': 'exercise-7-fizzbuzz',
            'description': 'Solve the classic FizzBuzz programming challenge',
            'difficulty': 'hard',
            'order_index': 7,
            'instructions': """Write a program that:
- Loops through numbers 1 to 30
- For multiples of 3, print "Fizz"
- For multiples of 5, print "Buzz"
- For multiples of both 3 and 5, print "FizzBuzz"
- Otherwise, print the number""",
            'starter_code': """# Your code here
for number in range(1, 31):
    pass""",
            'solution_code': """for number in range(1, 31):
    if number % 3 == 0 and number % 5 == 0:
        print("FizzBuzz")
    elif number % 3 == 0:
        print("Fizz")
    elif number % 5 == 0:
        print("Buzz")
    else:
        print(number)""",
            'test_cases': []
        },
        {
            'title': 'Exercise 8: Sum Calculator',
            'slug': 'exercise-8-sum-calculator',
            'description': 'Calculate sum and count positive/negative numbers',
            'difficulty': 'hard',
            'order_index': 8,
            'instructions': """Create a function `calculate_sum()` that:
- Takes a list of numbers as parameter
- Returns the sum of all numbers
- Also returns the count of positive and negative numbers
- Test with list: [5, -3, 8, -1, 0, 12, -7, 4]""",
            'starter_code': """def calculate_sum(numbers):
    # Your code here
    pass

result = calculate_sum([5, -3, 8, -1, 0, 12, -7, 4])
print(f"Sum: {result['sum']}")
print(f"Positive numbers: {result['positive']}")
print(f"Negative numbers: {result['negative']}")""",
            'solution_code': """def calculate_sum(numbers):
    total = sum(numbers)
    positive_count = sum(1 for n in numbers if n > 0)
    negative_count = sum(1 for n in numbers if n < 0)
    
    return {
        "sum": total,
        "positive": positive_count,
        "negative": negative_count
    }

result = calculate_sum([5, -3, 8, -1, 0, 12, -7, 4])
print(f"Sum: {result['sum']}")
print(f"Positive numbers: {result['positive']}")
print(f"Negative numbers: {result['negative']}")""",
            'test_cases': []
        },
        {
            'title': 'Exercise 9: Word Counter',
            'slug': 'exercise-9-word-counter',
            'description': 'Count word occurrences in a sentence',
            'difficulty': 'hard',
            'order_index': 9,
            'instructions': """Write a function `count_words()` that:
- Takes a sentence (string) as parameter
- Returns a dictionary with each word and its count
- Ignore case (treat "Hello" and "hello" as the same)
- Test with: "Hello world hello Python world" """,
            'starter_code': """def count_words(sentence):
    # Your code here
    pass

result = count_words("Hello world hello Python world")
print(result)""",
            'solution_code': """def count_words(sentence):
    words = sentence.lower().split()
    word_count = {}
    
    for word in words:
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1
    
    return word_count

result = count_words("Hello world hello Python world")
print(result)""",
            'test_cases': []
        },
        {
            'title': 'Exercise 10: Mini Calculator',
            'slug': 'exercise-10-mini-calculator',
            'description': 'Build a calculator with basic operations',
            'difficulty': 'hard',
            'order_index': 10,
            'instructions': """Create a calculator program that:
1. Defines functions: `add()`, `subtract()`, `multiply()`, `divide()`
2. Each function takes two numbers as parameters
3. Divide function should handle division by zero
4. Create a main function that tests all operations
5. Print results in a formatted way""",
            'starter_code': """def add(a, b):
    pass

def subtract(a, b):
    pass

def multiply(a, b):
    pass

def divide(a, b):
    pass

def main():
    # Your code here
    pass

main()""",
            'solution_code': """def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error: Cannot divide by zero"
    return a / b

def main():
    x, y = 10, 5
    print("Calculator Results:")
    print(f"{x} + {y} = {add(x, y)}")
    print(f"{x} - {y} = {subtract(x, y)}")
    print(f"{x} * {y} = {multiply(x, y)}")
    print(f"{x} / {y} = {divide(x, y)}")
    print(f"{x} / 0 = {divide(x, 0)}")

main()""",
            'test_cases': []
        }
    ]
    
    created_count = 0
    for ex_data in exercises_data:
        existing = Exercise.query.filter_by(
            tutorial_id=tutorial.id,
            slug=ex_data['slug']
        ).first()
        
        if not existing:
            # Combine description and instructions for the description field
            full_description = f"{ex_data['description']}\n\n{ex_data['instructions']}"
            
            exercise = Exercise(
                tutorial_id=tutorial.id,
                lesson_id=lesson.id,
                title=ex_data['title'],
                slug=ex_data['slug'],
                description=full_description,
                exercise_type='python',
                difficulty=ex_data['difficulty'],
                starter_code=ex_data['starter_code'],
                solution_code=ex_data['solution_code'],
                hints='Try breaking down the problem into smaller steps. Review the lesson examples if you get stuck.',
                order_index=ex_data['order_index'],
                points=10 if ex_data['difficulty'] == 'easy' else 20 if ex_data['difficulty'] == 'medium' else 30
            )
            db.session.add(exercise)
            created_count += 1
    
    if created_count > 0:
        db.session.commit()
        print(f"✅ Created {created_count} exercises")
    else:
        print(f"✅ All exercises already exist")


def main():
    """Main function to run the ingestion."""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("🚀 Starting Python Beginner Tutorial - Lesson 1 Ingestion")
        print("="*80 + "\n")
        
        try:
            # Step 1: Create instructor
            print("Step 1: Creating instructor account...")
            instructor = create_instructor()
            
            # Step 2: Create tutorial
            print("\nStep 2: Creating Python Beginner Tutorial (FREE)...")
            tutorial = create_python_beginner_tutorial(instructor)
            
            # Step 3: Create Lesson 1
            print("\nStep 3: Creating Lesson 1: Introduction to Python Programming...")
            lesson = create_lesson1(tutorial)
            
            # Step 4: Create Exercises
            print("\nStep 4: Creating 10 practice exercises...")
            create_exercises(tutorial, lesson)
            
            print("\n" + "="*80)
            print("✅ SUCCESS! Python Beginner Tutorial ingestion completed")
            print("="*80)
            print(f"\n📊 Summary:")
            print(f"   Instructor: {instructor.full_name} ({instructor.email})")
            print(f"   Tutorial: {tutorial.title}")
            print(f"   Price: FREE (${tutorial.price})")
            print(f"   Tutorial ID: {tutorial.id}")
            print(f"   Tutorial Slug: {tutorial.slug}")
            print(f"   Lesson ID: {lesson.id}")
            print(f"   Lesson Slug: {lesson.slug}")
            print(f"   Duration: {lesson.estimated_duration_minutes} minutes")
            print(f"   Exercises: 10 practice exercises (easy, medium, hard)")
            print(f"\n🔗 Access URL: /catalog/course/{tutorial.slug}/lesson/{lesson.slug}")
            print(f"🎓 Course Type: Python Beginner")
            print(f"🆓 Free Preview: Yes")
            
        except Exception as e:
            print(f"\n❌ ERROR during ingestion: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            raise
        
        print("\n" + "="*80)


if __name__ == '__main__':
    main()
