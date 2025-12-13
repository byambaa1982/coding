"""
Update mock course lessons with actual educational content.
Adds comprehensive learning material to each lesson in the Python Fundamentals course.
"""

from app import create_app
from app.models import Lesson
from app.extensions import db

app = create_app()

# Educational content for each lesson
LESSON_CONTENT = {
    "Introduction to Python": """
<h2>Welcome to Python Programming!</h2>

<h3>What is Python?</h3>
<p>Python is a high-level, interpreted programming language known for its simplicity and readability. Created by Guido van Rossum and first released in 1991, Python has become one of the most popular programming languages in the world.</p>

<h3>Why Learn Python?</h3>
<ul>
    <li><strong>Easy to Learn:</strong> Python syntax is clean and intuitive, making it perfect for beginners.</li>
    <li><strong>Versatile:</strong> Used in web development, data science, AI, automation, and more.</li>
    <li><strong>Large Community:</strong> Extensive libraries and frameworks, plus helpful community support.</li>
    <li><strong>High Demand:</strong> One of the most sought-after skills in the job market.</li>
</ul>

<h3>Python Philosophy</h3>
<p>The Zen of Python emphasizes:</p>
<ul>
    <li>Beautiful is better than ugly</li>
    <li>Simple is better than complex</li>
    <li>Readability counts</li>
</ul>

<h3>Your First Python Program</h3>
<pre><code>print("Hello, World!")</code></pre>
<p>That is it! One line to output text to the screen. Compare this to other languages that require multiple lines of boilerplate code.</p>

<h3>Setting Up Python</h3>
<ol>
    <li>Download Python from python.org</li>
    <li>Install Python (check Add to PATH)</li>
    <li>Verify installation: <code>python --version</code></li>
    <li>Use IDLE, VS Code, or any text editor</li>
</ol>
""",

    "Variables and Data Types": """
<h2>Variables and Data Types</h2>

<h3>What are Variables?</h3>
<p>Variables are containers that store data values. Think of them as labeled boxes where you can put information and retrieve it later.</p>

<h3>Creating Variables</h3>
<pre><code># Python uses simple assignment
name = "Alice"
age = 25
height = 5.6
is_student = True</code></pre>

<p><strong>Note:</strong> Python is dynamically typed - you do not need to declare the type!</p>

<h3>Basic Data Types</h3>

<h4>1. Numbers</h4>
<ul>
    <li><strong>Integer (int):</strong> Whole numbers
        <pre><code>count = 10
negative = -5</code></pre>
    </li>
    <li><strong>Float:</strong> Decimal numbers
        <pre><code>price = 19.99
temperature = -3.5</code></pre>
    </li>
</ul>

<h4>2. Strings (str)</h4>
<p>Text data enclosed in quotes:</p>
<pre><code>name = "Alice"
message = 'Hello, World!'
multi_line = \"\"\"This is a
multi-line string\"\"\"</code></pre>

<h4>3. Boolean (bool)</h4>
<p>True or False values:</p>
<pre><code>is_active = True
is_completed = False</code></pre>

<h3>Type Checking</h3>
<pre><code>x = 42
print(type(x))  # Output: &lt;class 'int'&gt;

name = "Python"
print(type(name))  # Output: &lt;class 'str'&gt;</code></pre>

<h3>Type Conversion</h3>
<pre><code># String to integer
age = int("25")

# Integer to string
count_str = str(100)

# String to float
price = float("19.99")</code></pre>

<h3>Variable Naming Rules</h3>
<ul>
    <li>Start with letter or underscore</li>
    <li>Can contain letters, numbers, underscores</li>
    <li>Case-sensitive (Age and age are different)</li>
    <li>Use descriptive names: user_age not x</li>
    <li>Use snake_case for multiple words</li>
</ul>
""",

    "Basic Operations and Expressions": """
<h2>Basic Operations and Expressions</h2>

<h3>Arithmetic Operations</h3>
<p>Python supports all standard mathematical operations:</p>

<pre><code># Addition
result = 10 + 5  # 15

# Subtraction
result = 10 - 5  # 5

# Multiplication
result = 10 * 5  # 50

# Division (always returns float)
result = 10 / 3  # 3.333...

# Floor Division (rounds down)
result = 10 // 3  # 3

# Modulus (remainder)
result = 10 % 3  # 1

# Exponentiation
result = 2 ** 3  # 8 (2 to the power of 3)</code></pre>

<h3>Comparison Operations</h3>
<p>Compare values and get True or False:</p>

<pre><code># Equal to
5 == 5  # True
5 == 3  # False

# Not equal to
5 != 3  # True

# Greater than
10 > 5  # True

# Less than
3 < 10  # True

# Greater than or equal
5 >= 5  # True

# Less than or equal
3 <= 5  # True</code></pre>

<h3>Logical Operations</h3>
<p>Combine boolean expressions:</p>

<pre><code># AND - both must be True
age = 25
has_license = True
can_drive = age >= 18 and has_license  # True

# OR - at least one must be True
is_weekend = False
is_holiday = True
can_relax = is_weekend or is_holiday  # True

# NOT - inverts the boolean
is_raining = False
is_sunny = not is_raining  # True</code></pre>

<h3>String Operations</h3>
<pre><code># Concatenation
greeting = "Hello" + " " + "World"  # "Hello World"

# Repetition
stars = "*" * 10  # "**********"

# String formatting
name = "Alice"
age = 25
message = f"My name is {name} and I am {age} years old."</code></pre>
""",

    "Conditional Statements (if/else)": """
<h2>Conditional Statements (if/else)</h2>

<h3>Making Decisions in Code</h3>
<p>Conditional statements allow your program to make decisions and execute different code based on conditions.</p>

<h3>Basic if Statement</h3>
<pre><code>age = 18

if age >= 18:
    print("You are an adult")
    print("You can vote")</code></pre>

<p><strong>Note:</strong> Indentation matters in Python! Code inside the if block must be indented.</p>

<h3>if-else Statement</h3>
<pre><code>temperature = 25

if temperature > 30:
    print("It is hot outside")
else:
    print("Temperature is comfortable")</code></pre>

<h3>if-elif-else Statement</h3>
<p>Handle multiple conditions:</p>

<pre><code>score = 85

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

print(f"Your grade is: {grade}")</code></pre>

<h3>Nested Conditionals</h3>
<pre><code>age = 20
has_license = True

if age >= 18:
    if has_license:
        print("You can drive")
    else:
        print("You need a license")
else:
    print("You are too young to drive")</code></pre>

<h3>Multiple Conditions</h3>
<pre><code>age = 25
income = 50000

if age >= 18 and income > 30000:
    print("Eligible for credit card")

if age < 13 or age > 65:
    print("Discounted ticket price")</code></pre>
""",

    "Loops - While Loop": """
<h2>Loops - While Loop</h2>

<h3>What are Loops?</h3>
<p>Loops allow you to repeat code multiple times without writing it over and over. The while loop continues executing as long as a condition is True.</p>

<h3>Basic While Loop</h3>
<pre><code>count = 1

while count <= 5:
    print(f"Count is: {count}")
    count += 1

# Output:
# Count is: 1
# Count is: 2
# Count is: 3
# Count is: 4
# Count is: 5</code></pre>

<h3>Loop Control Statements</h3>

<h4>break - Exit the loop</h4>
<pre><code>number = 1
while number <= 10:
    if number == 5:
        break  # Stop when we reach 5
    print(number)
    number += 1

# Output: 1, 2, 3, 4</code></pre>

<h4>continue - Skip current iteration</h4>
<pre><code>number = 0
while number < 5:
    number += 1
    if number == 3:
        continue  # Skip printing 3
    print(number)

# Output: 1, 2, 4, 5</code></pre>

<h3>Common While Loop Patterns</h3>

<h4>Countdown</h4>
<pre><code>countdown = 5
while countdown > 0:
    print(countdown)
    countdown -= 1
print("Blast off!")</code></pre>

<h4>Sum of Numbers</h4>
<pre><code>total = 0
number = 1

while number <= 10:
    total += number
    number += 1

print(f"Sum of 1 to 10 is: {total}")  # 55</code></pre>
""",

    "Loops - For Loop": """
<h2>Loops - For Loop</h2>

<h3>What is a For Loop?</h3>
<p>The for loop iterates over a sequence (list, string, range, etc.) and executes code for each item. It is more concise than while loops for many tasks.</p>

<h3>Basic For Loop with Range</h3>
<pre><code>for i in range(5):
    print(i)

# Output: 0, 1, 2, 3, 4</code></pre>

<h3>Range Function</h3>
<p>Generates a sequence of numbers:</p>

<pre><code># range(stop) - starts at 0
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

# range(start, stop)
for i in range(2, 6):
    print(i)  # 2, 3, 4, 5

# range(start, stop, step)
for i in range(0, 10, 2):
    print(i)  # 0, 2, 4, 6, 8

# Counting down
for i in range(5, 0, -1):
    print(i)  # 5, 4, 3, 2, 1</code></pre>

<h3>Iterating Over Strings</h3>
<pre><code>message = "Python"

for char in message:
    print(char)

# Output: P, y, t, h, o, n</code></pre>

<h3>Iterating Over Lists</h3>
<pre><code>fruits = ["apple", "banana", "orange"]

for fruit in fruits:
    print(f"I like {fruit}")</code></pre>

<h3>Loop Control in For Loops</h3>

<h4>break - Exit loop early</h4>
<pre><code>numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]

for num in numbers:
    if num == 5:
        break
    print(num)

# Output: 1, 2, 3, 4</code></pre>

<h4>continue - Skip iteration</h4>
<pre><code>for num in range(1, 6):
    if num == 3:
        continue
    print(num)

# Output: 1, 2, 4, 5 (skips 3)</code></pre>
""",

    "Functions Basics": """
<h2>Functions Basics</h2>

<h3>What are Functions?</h3>
<p>Functions are reusable blocks of code that perform specific tasks. They help organize code, avoid repetition, and make programs easier to understand.</p>

<h3>Defining a Function</h3>
<pre><code>def greet():
    print("Hello, World!")

# Call the function
greet()  # Output: Hello, World!</code></pre>

<h3>Function Parameters</h3>
<p>Parameters allow you to pass data into functions:</p>

<pre><code>def greet(name):
    print(f"Hello, {name}!")

greet("Alice")  # Output: Hello, Alice!
greet("Bob")    # Output: Hello, Bob!</code></pre>

<h3>Return Values</h3>
<p>Functions can return values using the return statement:</p>

<pre><code>def add(a, b):
    return a + b

result = add(10, 5)
print(result)  # Output: 15</code></pre>

<h3>Default Parameters</h3>
<pre><code>def greet(name="Guest"):
    print(f"Hello, {name}!")

greet("Alice")  # Output: Hello, Alice!
greet()         # Output: Hello, Guest!</code></pre>

<h3>Multiple Return Values</h3>
<pre><code>def get_min_max(numbers):
    return min(numbers), max(numbers)

minimum, maximum = get_min_max([1, 5, 3, 9, 2])
print(f"Min: {minimum}, Max: {maximum}")</code></pre>
""",

    "Lists and Tuples": """
<h2>Lists and Tuples</h2>

<h3>What are Lists?</h3>
<p>Lists are ordered, mutable (changeable) collections that can store multiple items. Lists are one of the most versatile data structures in Python.</p>

<h3>Creating Lists</h3>
<pre><code># Empty list
empty_list = []

# List with items
fruits = ["apple", "banana", "orange"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]</code></pre>

<h3>Accessing List Elements</h3>
<pre><code>fruits = ["apple", "banana", "orange", "grape"]

# Indexing (starts at 0)
print(fruits[0])   # apple
print(fruits[2])   # orange

# Negative indexing (from end)
print(fruits[-1])  # grape (last item)
print(fruits[-2])  # orange (second from end)</code></pre>

<h3>Modifying Lists</h3>
<pre><code>fruits = ["apple", "banana", "orange"]

# Change an item
fruits[1] = "blueberry"

# Add items
fruits.append("grape")          # Add to end
fruits.insert(1, "mango")       # Insert at index
fruits.extend(["kiwi", "pear"]) # Add multiple items

# Remove items
fruits.remove("apple")   # Remove by value
popped = fruits.pop()    # Remove last item
del fruits[1]            # Delete by index</code></pre>

<h3>Tuples</h3>
<p>Tuples are like lists but immutable (cannot be changed after creation). Use parentheses instead of brackets.</p>

<pre><code># Creating tuples
empty_tuple = ()
coordinates = (10, 20)
mixed = (1, "hello", 3.14)

# Accessing (same as lists)
print(coordinates[0])  # 10

# Tuples are immutable
# coordinates[0] = 15  # ERROR! Cannot modify</code></pre>
""",

    "Dictionaries and Sets": """
<h2>Dictionaries and Sets</h2>

<h3>What are Dictionaries?</h3>
<p>Dictionaries store data in key-value pairs. They are like real dictionaries where you look up a word (key) to get its definition (value). Dictionaries are unordered, mutable, and very fast for lookups.</p>

<h3>Creating Dictionaries</h3>
<pre><code># Empty dictionary
empty_dict = {}

# Dictionary with data
person = {
    "name": "Alice",
    "age": 25,
    "city": "New York"
}</code></pre>

<h3>Accessing Dictionary Values</h3>
<pre><code>person = {"name": "Alice", "age": 25, "city": "New York"}

# Using square brackets
print(person["name"])  # Alice

# Using get() - safer
print(person.get("name"))   # Alice
print(person.get("email"))  # None (no error)</code></pre>

<h3>Modifying Dictionaries</h3>
<pre><code>person = {"name": "Alice", "age": 25}

# Add or update items
person["email"] = "alice@example.com"
person["age"] = 26  # Update existing key

# Remove items
del person["age"]           # Delete key
email = person.pop("email") # Remove and return value</code></pre>

<h3>Sets</h3>
<p>Sets are unordered collections of unique items. They are useful for removing duplicates and mathematical set operations.</p>

<h3>Creating Sets</h3>
<pre><code># Empty set (must use set(), not {})
empty_set = set()

# Set with items
fruits = {"apple", "banana", "orange"}
numbers = {1, 2, 3, 4, 5}

# From list (removes duplicates)
numbers_list = [1, 2, 2, 3, 3, 3, 4]
unique_numbers = set(numbers_list)  # {1, 2, 3, 4}</code></pre>

<h3>Set Operations</h3>
<pre><code>set1 = {1, 2, 3, 4, 5}
set2 = {4, 5, 6, 7, 8}

# Union (all elements)
union = set1 | set2  # {1, 2, 3, 4, 5, 6, 7, 8}

# Intersection (common elements)
intersection = set1 & set2  # {4, 5}

# Difference (in set1 but not set2)
difference = set1 - set2  # {1, 2, 3}</code></pre>
"""
}


def update_lessons_with_content():
    """Update all lessons in the Python Fundamentals course with educational content."""
    
    with app.app_context():
        print("\n" + "="*60)
        print("UPDATING LESSON CONTENT")
        print("="*60)
        
        # Find the Python Fundamentals course
        lessons = Lesson.query.filter(
            Lesson.title.in_(LESSON_CONTENT.keys())
        ).all()
        
        if not lessons:
            print("No lessons found to update.")
            print("   Make sure you have run seed_mock_course_data.py first.")
            return
        
        print(f"\nFound {len(lessons)} lessons to update\n")
        
        updated_count = 0
        for lesson in lessons:
            if lesson.title in LESSON_CONTENT:
                content = LESSON_CONTENT[lesson.title]
                lesson.content = content
                lesson.content_type = 'html'
                db.session.add(lesson)
                updated_count += 1
                print(f"Updated: {lesson.title}")
                print(f"   Content length: {len(content)} characters")
        
        db.session.commit()
        
        print(f"\n" + "="*60)
        print(f"SUCCESS! Updated {updated_count} lessons with content")
        print("="*60)
        print("\nYour lessons now contain:")
        print("  - Comprehensive explanations")
        print("  - Code examples with comments")
        print("  - Common patterns and best practices")
        print("  - Visual formatting with headers and lists")
        print("\nStudents can now read these lessons before attempting exercises!")
        print("="*60 + "\n")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("LESSON CONTENT UPDATER")
    print("="*60)
    print("\nThis script will add educational content to your mock course lessons.")
    print("Each lesson will get comprehensive Python programming content including:")
    print("  - What the concept is and why it is important")
    print("  - Detailed explanations with examples")
    print("  - Code snippets you can learn from")
    print("  - Common patterns and use cases")
    print("  - Best practices")
    
    response = input("\nContinue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        update_lessons_with_content()
    else:
        print("Operation cancelled.")
