## Task 1: Create and Display Multiple Variable Types

**Objective:** Practice creating variables of different data types and displaying them.

**Instructions:**
1. Create the following variables:
   - A string variable `student_name` with your name
   - An integer variable `student_id` with a 5-digit number
   - A float variable `gpa` with a decimal value between 0.0 and 4.0
   - A boolean variable `is_enrolled` set to `True`
2. Print each variable with a descriptive label
3. Use the `type()` function to verify the data type of each variable

**Expected Output Example:**
```
Student Name: John Doe (Type: <class 'str'>)
Student ID: 12345 (Type: <class 'int'>)
GPA: 3.75 (Type: <class 'float'>)
Enrolled: True (Type: <class 'bool'>)
```

**Difficulty:** Easy  
**Estimated Time:** 10 minutes

### Solution:
```python
# Task 1: Create and Display Multiple Variable Types

# Create variables of different types
student_name = "John Doe"
student_id = 12345
gpa = 3.75
is_enrolled = True

# Print each variable with descriptive label and type
print(f"Student Name: {student_name} (Type: {type(student_name)})")
print(f"Student ID: {student_id} (Type: {type(student_id)})")
print(f"GPA: {gpa} (Type: {type(gpa)})")
print(f"Enrolled: {is_enrolled} (Type: {type(is_enrolled)})")
```

---

## Task 2: Variable Naming Convention Practice

**Objective:** Understand and apply Python variable naming rules.

**Instructions:**
1. Create 5 correctly named variables following Python naming conventions:
   - Use snake_case for multi-word variables
   - Include at least one variable with numbers
   - Include at least one single-character variable
2. Try to create 3 **invalid** variable names and document the error messages:
   - One starting with a digit
   - One using a Python keyword (e.g., `class`, `for`, `if`)
   - One with special characters (e.g., `@`, `#`, `-`)
3. Write comments explaining why each invalid name fails

**Expected Deliverable:**
- A Python file with valid variables and commented-out invalid examples with explanations

**Difficulty:** Easy  
**Estimated Time:** 15 minutes

### Solution:
```python
# Task 2: Variable Naming Convention Practice

# Part 1: Valid variable names following Python conventions
first_name = "Alice"  # snake_case for multi-word
last_name = "Johnson"
user_age_21 = 21  # Variable with numbers
total_count = 100
x = 10  # Single-character variable

print("Valid variables created successfully:")
print(f"Name: {first_name} {last_name}")
print(f"Age: {user_age_21}")
print(f"Count: {total_count}")
print(f"X value: {x}")

# Part 2: Invalid variable names (commented out to prevent errors)

# INVALID 1: Starting with a digit
# 1st_place = "Gold"  
# Error: SyntaxError: invalid decimal literal
# Explanation: Variable names cannot start with a number

# INVALID 2: Using Python keyword
# class = "Math101"  
# Error: SyntaxError: invalid syntax
# Explanation: 'class' is a reserved Python keyword

# INVALID 3: Using special characters
# user@email = "test@example.com"  
# Error: SyntaxError: invalid syntax
# Explanation: Special characters like @, #, - are not allowed in variable names

print("\nInvalid examples documented in comments above")
```

---

## Task 3: Type Conversion Challenge

**Objective:** Master type conversion between different data types.

**Instructions:**0
1. Create the following variables:
   - `price_string = "29.99"`
   - `quantity = 5`
   - `discount_rate = 0.10`
2. Convert and calculate:
   - Convert `price_string` to a float
   - Calculate total price: `price * quantity`
   - Calculate discount amount: `total * discount_rate`
   - Calculate final price: `total - discount`
3. Convert the final price to an integer (rounded down)
4. Convert the final price to a string and display it with a currency symbol

**Expected Output:**
```
Original Price: $29.99
Quantity: 5
Total: $149.95
Discount (10%): $14.995
Final Price: $134.955
Final Price (Integer): $134
Final Price (String): "The total cost is $134.95"
```

**Difficulty:** Easy  
**Estimated Time:** 15 minutes

### Solution:
```python
# Task 3: Type Conversion Challenge

# Create the initial variables
price_string = "29.99"
quantity = 5
discount_rate = 0.10

# Convert price_string to float
price = float(price_string)

# Calculate total price
total = price * quantity

# Calculate discount amount
discount = total * discount_rate

# Calculate final price
final_price = total - discount

# Convert final price to integer (rounded down)
final_price_int = int(final_price)

# Convert to string with currency symbol
final_price_str = f"The total cost is ${final_price:.2f}"

# Display all results
print(f"Original Price: ${price}")
print(f"Quantity: {quantity}")
print(f"Total: ${total}")
print(f"Discount (10%): ${discount}")
print(f"Final Price: ${final_price}")
print(f"Final Price (Integer): ${final_price_int}")
print(f'Final Price (String): "{final_price_str}"')
```

---

## Task 4: Boolean Logic and Comparisons

**Objective:** Practice using boolean variables and logical operations.

**Instructions:**
1. Create variables representing a user profile:
   - `age = 25`
   - `has_license = True`
   - `has_insurance = False`
   - `years_driving = 3`
2. Create boolean expressions that check:
   - Is the user old enough to drive? (`age >= 18`)
   - Can the user legally drive? (has license AND is old enough)
   - Is the user fully compliant? (has license AND has insurance)
   - Is the user an experienced driver? (years driving >= 5)
3. Store each result in a descriptive boolean variable
4. Print a summary report with all checks

**Expected Output:**
```
=== Driver Profile Check ===
Age: 25
Old Enough to Drive: True
Legally Can Drive: True
Fully Compliant: False (Missing insurance)
Experienced Driver: False
```

**Difficulty:** Medium  
**Estimated Time:** 20 minutes

### Solution:
```python
# Task 4: Boolean Logic and Comparisons

# Create variables representing a user profile
age = 25
has_license = True
has_insurance = False
years_driving = 3

# Create boolean expressions for each check
old_enough_to_drive = age >= 18
can_legally_drive = has_license and old_enough_to_drive
fully_compliant = has_license and has_insurance
experienced_driver = years_driving >= 5

# Print summary report
print("=== Driver Profile Check ===")
print(f"Age: {age}")
print(f"Old Enough to Drive: {old_enough_to_drive}")
print(f"Legally Can Drive: {can_legally_drive}")

# Add note for compliance status
if fully_compliant:
    print(f"Fully Compliant: {fully_compliant}")
else:
    print(f"Fully Compliant: {fully_compliant} (Missing insurance)")

print(f"Experienced Driver: {experienced_driver}")
```

---

## Task 5: Build a Personal Information Manager

**Objective:** Combine all concepts to create a practical mini-application.

**Instructions:**
1. Create a program that stores information about a person:
   - Basic info: `first_name`, `last_name`, `age`, `email`
   - Physical attributes: `height_cm` (float), `weight_kg` (float)
   - Status flags: `is_student`, `is_employed`, `is_citizen`
   - Address: `street`, `city`, `zip_code` (can be string or int)
2. Calculate additional information:
   - Full name (combining first and last name)
   - BMI = weight / (height_m * height_m), where height_m = height_cm / 100
   - Age category: "Minor" if under 18, "Adult" if 18-64, "Senior" if 65+
3. Create a formatted profile display that shows:
   - All personal information
   - Calculated BMI with 2 decimal places
   - Age category
   - Employment/Student status
4. Use proper variable types for each piece of data
5. Include type checking for at least 3 variables

**Expected Output Example:**
```
===== PERSONAL PROFILE =====
Name: Jane Smith
Email: jane.smith@example.com
Age: 28 (Adult)
Height: 165.0 cm
Weight: 60.5 kg
BMI: 22.22

Status:
- Student: No
- Employed: Yes
- Citizen: Yes

Address:
123 Main Street
New York, 10001

===== TYPE INFORMATION =====
Name type: <class 'str'>
Age type: <class 'int'>
BMI type: <class 'float'>
============================
```

**Difficulty:** Medium  
**Estimated Time:** 25 minutes

### Solution:
```python
# Task 5: Build a Personal Information Manager

# Part 1: Create variables for person information
# Basic info
first_name = "Jane"
last_name = "Smith"
age = 28
email = "jane.smith@example.com"

# Physical attributes
height_cm = 165.0
weight_kg = 60.5

# Status flags
is_student = False
is_employed = True
is_citizen = True

# Address
street = "123 Main Street"
city = "New York"
zip_code = "10001"

# Part 2: Calculate additional information
# Full name
full_name = f"{first_name} {last_name}"

# BMI calculation
height_m = height_cm / 100
bmi = weight_kg / (height_m * height_m)

# Age category
if age < 18:
    age_category = "Minor"
elif age <= 64:
    age_category = "Adult"
else:
    age_category = "Senior"

# Part 3: Display formatted profile
print("===== PERSONAL PROFILE =====")
print(f"Name: {full_name}")
print(f"Email: {email}")
print(f"Age: {age} ({age_category})")
print(f"Height: {height_cm} cm")
print(f"Weight: {weight_kg} kg")
print(f"BMI: {bmi:.2f}")
print()
print("Status:")
print(f"- Student: {'Yes' if is_student else 'No'}")
print(f"- Employed: {'Yes' if is_employed else 'No'}")
print(f"- Citizen: {'Yes' if is_citizen else 'No'}")
print()
print("Address:")
print(street)
print(f"{city}, {zip_code}")
print()

# Part 4: Type checking for at least 3 variables
print("===== TYPE INFORMATION =====")
print(f"Name type: {type(full_name)}")
print(f"Age type: {type(age)}")
print(f"BMI type: {type(bmi)}")
print("============================")
```
