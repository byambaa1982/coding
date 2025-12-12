# Python Beginner Tutorial - Lesson 1
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

## 🎯 Practice Exercises

### Exercise 1: Variables and Math (Easy)
Create a program that:
1. Stores your name, age, and favorite number in variables
2. Calculates what year you were born (current year - age)
3. Calculates double your favorite number
4. Prints all results with descriptive messages

**Expected Output:**
```
Name: Alice
Age: 25
Birth Year: 2000
Favorite Number: 7
Double: 14
```

**Test Your Code:**
```python
# Your code here
name = "Alice"
age = 25
# ... complete the rest
```

---

### Exercise 2: Temperature Converter (Easy)
Write a function `celsius_to_fahrenheit()` that:
- Takes a temperature in Celsius as parameter
- Converts it to Fahrenheit using formula: `F = (C × 9/5) + 32`
- Returns the Fahrenheit temperature
- Test with 0, 25, and 100 degrees Celsius

**Expected Output:**
```
0°C = 32.0°F
25°C = 77.0°F
100°C = 212.0°F
```

---

### Exercise 3: Grade Calculator (Medium)
Create a function `calculate_grade()` that:
- Takes a score (0-100) as parameter
- Returns the letter grade:
  - A: 90-100
  - B: 80-89
  - C: 70-79
  - D: 60-69
  - F: 0-59
- Test with scores: 95, 82, 71, 65, 55

**Expected Output:**
```
Score 95: Grade A
Score 82: Grade B
Score 71: Grade C
Score 65: Grade D
Score 55: Grade F
```

---

### Exercise 4: Shopping List (Medium)
Create a program that:
1. Creates an empty list called `shopping_list`
2. Adds at least 5 items to the list
3. Prints the total number of items
4. Prints each item with its position number
5. Removes one item from the list
6. Prints the updated list

**Expected Output:**
```
Shopping List (5 items):
1. Apples
2. Bread
3. Milk
4. Eggs
5. Cheese

After removing Milk:
Shopping List (4 items):
1. Apples
2. Bread
3. Eggs
4. Cheese
```

---

### Exercise 5: Even Numbers (Medium)
Write a function `print_even_numbers()` that:
- Takes two parameters: start and end
- Prints all even numbers between start and end (inclusive)
- Uses a for loop
- Test with start=1, end=20

**Expected Output:**
```
Even numbers from 1 to 20:
2 4 6 8 10 12 14 16 18 20
```

---

### Exercise 6: Student Record (Medium)
Create a program that:
1. Creates a dictionary for a student with keys: name, age, grade, subjects (list)
2. Prints each key-value pair
3. Adds a new key "email" with a value
4. Updates the grade
5. Prints the final dictionary

**Expected Output:**
```
name: John Doe
age: 16
grade: 10
subjects: ['Math', 'Science', 'English']

After updates:
name: John Doe
age: 16
grade: 11
subjects: ['Math', 'Science', 'English']
email: john@school.com
```

---

### Exercise 7: FizzBuzz Classic (Hard)
Write a program that:
- Loops through numbers 1 to 30
- For multiples of 3, print "Fizz"
- For multiples of 5, print "Buzz"
- For multiples of both 3 and 5, print "FizzBuzz"
- Otherwise, print the number

**Expected Output:**
```
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
...
```

---

### Exercise 8: Sum Calculator (Hard)
Create a function `calculate_sum()` that:
- Takes a list of numbers as parameter
- Returns the sum of all numbers
- Also returns the count of positive and negative numbers
- Test with list: [5, -3, 8, -1, 0, 12, -7, 4]

**Expected Output:**
```
Sum: 18
Positive numbers: 4
Negative numbers: 3
```

---

### Exercise 9: Word Counter (Hard)
Write a function `count_words()` that:
- Takes a sentence (string) as parameter
- Returns a dictionary with each word and its count
- Ignore case (treat "Hello" and "hello" as the same)
- Test with: "Hello world hello Python world"

**Expected Output:**
```
{
    'hello': 2,
    'world': 2,
    'python': 1
}
```

---

### Exercise 10: Mini Calculator (Challenge)
Create a calculator program that:
1. Defines functions: `add()`, `subtract()`, `multiply()`, `divide()`
2. Each function takes two numbers as parameters
3. Divide function should handle division by zero
4. Create a main function that tests all operations
5. Print results in a formatted way

**Expected Output:**
```
Calculator Results:
10 + 5 = 15
10 - 5 = 5
10 * 5 = 50
10 / 5 = 2.0
10 / 0 = Error: Cannot divide by zero
```

---

## 🧪 Test Cases

### For Exercise 2 (Temperature Converter):
```python
assert celsius_to_fahrenheit(0) == 32.0
assert celsius_to_fahrenheit(25) == 77.0
assert celsius_to_fahrenheit(100) == 212.0
assert celsius_to_fahrenheit(-40) == -40.0
```

### For Exercise 3 (Grade Calculator):
```python
assert calculate_grade(95) == "A"
assert calculate_grade(85) == "B"
assert calculate_grade(75) == "C"
assert calculate_grade(65) == "D"
assert calculate_grade(55) == "F"
assert calculate_grade(100) == "A"
assert calculate_grade(0) == "F"
```

### For Exercise 5 (Even Numbers):
```python
# Should print: 2 4 6 8 10
# When called: print_even_numbers(1, 10)
```

### For Exercise 8 (Sum Calculator):
```python
result = calculate_sum([5, -3, 8, -1, 0, 12, -7, 4])
assert result["sum"] == 18
assert result["positive"] == 4
assert result["negative"] == 3
```

---

## 🎓 Solutions

### Exercise 1 Solution:
```python
name = "Alice"
age = 25
favorite_number = 7

current_year = 2025
birth_year = current_year - age
double_favorite = favorite_number * 2

print(f"Name: {name}")
print(f"Age: {age}")
print(f"Birth Year: {birth_year}")
print(f"Favorite Number: {favorite_number}")
print(f"Double: {double_favorite}")
```

### Exercise 2 Solution:
```python
def celsius_to_fahrenheit(celsius):
    fahrenheit = (celsius * 9/5) + 32
    return fahrenheit

# Test
temperatures = [0, 25, 100]
for temp in temperatures:
    result = celsius_to_fahrenheit(temp)
    print(f"{temp}°C = {result}°F")
```

### Exercise 3 Solution:
```python
def calculate_grade(score):
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
    print(f"Score {score}: Grade {grade}")
```

### Exercise 7 Solution (FizzBuzz):
```python
for number in range(1, 31):
    if number % 3 == 0 and number % 5 == 0:
        print("FizzBuzz")
    elif number % 3 == 0:
        print("Fizz")
    elif number % 5 == 0:
        print("Buzz")
    else:
        print(number)
```

### Exercise 10 Solution (Mini Calculator):
```python
def add(a, b):
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

main()
```

---

## 🚀 Next Steps

Congratulations on completing Lesson 1! You've learned:
✅ Python syntax and basic operations
✅ Variables and data types
✅ Control flow (if/else, loops)
✅ Data structures (lists, dictionaries)
✅ Functions and return values

**Ready for Lesson 2?**
In the next lesson, you'll learn:
- Advanced list operations and comprehensions
- Working with files (reading and writing)
- Exception handling (try/except)
- Object-Oriented Programming basics
- Using Python modules and libraries

**Practice Tips:**
1. Complete all exercises before moving on
2. Experiment with the code - break it and fix it!
3. Try creating your own variations of the exercises
4. Code every day, even if just for 15 minutes

---

## 📝 Glossary

- **Variable**: A container for storing data values
- **Function**: A reusable block of code that performs a specific task
- **Parameter**: A variable in a function definition
- **Argument**: The actual value passed to a function
- **Loop**: A structure that repeats code multiple times
- **List**: An ordered, mutable collection of items
- **Dictionary**: A collection of key-value pairs
- **String**: A sequence of characters (text)
- **Boolean**: A data type with two values: True or False
- **Condition**: An expression that evaluates to True or False
- **Indentation**: Spaces at the beginning of a line (crucial in Python!)

---

**Good luck with your Python journey! 🐍**
