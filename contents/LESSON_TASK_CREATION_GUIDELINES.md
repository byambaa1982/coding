# Lesson Task Creation Guidelines

**Purpose:** This document provides comprehensive guidelines for creating and upserting lesson tasks into the database. Follow these rules to ensure consistency and quality across all tutorial content.

---

## Database Structure

### Key Tables and Relationships

```
NewTutorial (new_tutorials)
├── id: Primary key
├── title: Tutorial title
├── course_type: 'python' or 'sql'
└── lessons (relationship)

Lesson (lessons)
├── id: Primary key
├── tutorial_id: Foreign key to NewTutorial
├── title: Lesson title
├── content: Lesson content (markdown/text)
└── exercises (relationship)

Exercise (exercises)
├── id: Primary key
├── tutorial_id: Foreign key to NewTutorial
├── lesson_id: Foreign key to Lesson
├── title: Exercise/task title
├── slug: URL-friendly identifier
├── description: Full task description
├── exercise_type: 'python' or 'sql'
├── difficulty: 'easy', 'medium', or 'hard'
├── starter_code: Initial code provided to students
├── solution_code: Complete working solution
├── test_cases: JSON array of test cases
├── hints: JSON array of hints
├── order_index: Task ordering
└── points: Points awarded (10=easy, 15=medium, 20=hard)
```

---

## File Organization Rules

### 1. File Location
**ALWAYS** create task files in the `contents/` directory.

**Naming Convention:**
```
contents/lesson{lesson_id}_{topic_slug}_tasks.md
```

**Examples:**
- `contents/lesson6_variables_datatypes_tasks.md`
- `contents/lesson7_control_flow_tasks.md`
- `contents/lesson8_functions_basics_tasks.md`

### 2. File Structure
Each task file must contain **ONLY** the tasks, no additional sections.

```markdown
## Task 1: [Task Title]

**Objective:** [One sentence describing the learning goal]

**Instructions:**
[Numbered list of clear steps]

**Expected Output:**
[Simple, clear example - keep it minimal]

**Difficulty:** [Easy/Medium/Hard]
**Estimated Time:** [X minutes]

### Solution:
```python
[Complete working solution code]
```

---

## Task 2: [Next Task Title]
[... repeat structure]
```

---

## Task Creation Guidelines

### 3. Task Complexity Rules

#### ✅ DO:
- Keep tasks focused on ONE concept
- Use simple, relatable examples
- Make expected output **SHORT and CLEAR** (3-5 lines maximum)
- Provide clear, step-by-step instructions
- Ensure beginners can understand without frustration

#### ❌ DON'T:
- Create multi-step complex outputs
- Mix too many concepts in one task
- Use confusing or abstract examples
- Make expected output longer than 7 lines
- Assume advanced knowledge

### 4. Expected Output Guidelines

**Bad Example (Too Complex):**
```
Original Price: $29.99
Quantity: 5
Total: $149.95
Discount (10%): $14.995
Final Price: $134.955
Final Price (Integer): $134
Final Price (String): "The total cost is $134.95"
```
❌ 7 lines, too many calculations, confusing decimals

**Good Example (Simple):**
```
Price: $29.99
Total: $149.95
Final: $134.96
```
✅ 3 lines, clear and focused

### 5. Difficulty Distribution

For each lesson, create **5 tasks** with this distribution:
- **3 Easy tasks** (10 points each)
- **2 Medium tasks** (15 points each)
- **0 Hard tasks** (save hard tasks for advanced lessons)

**Easy Task Characteristics:**
- Single concept focus
- 10-15 minutes completion time
- 3-5 lines of expected output
- Minimal calculation or logic

**Medium Task Characteristics:**
- Combines 2-3 related concepts
- 20-25 minutes completion time
- 5-7 lines of expected output
- Some calculation or conditional logic

---

## Solution Code Requirements

### 6. Solution Code Must:

1. **Be Complete and Runnable**
   - No placeholders like `# TODO` or `pass`
   - Include all necessary imports
   - Handle edge cases if mentioned in instructions

2. **Produce EXACT Expected Output**
   - Test before upserting
   - Match formatting, spacing, and punctuation
   - Use same variable names as instructions

3. **Follow Best Practices**
   - Use clear variable names
   - Include helpful comments
   - Follow PEP 8 style guide
   - Keep it simple for beginners

4. **Be Self-Contained**
   - Don't depend on external files
   - Use only standard library (unless specified)
   - Work with Python 3.8+

### 7. Testing Solutions

**ALWAYS test solution code before upserting:**

```python
# Create test file
python -c "[paste solution code]"

# Verify output matches expected output exactly
```

**Example Testing Script:**
```python
# contents/test_lesson_solutions.py
from upsert_lesson_tasks import TaskParser

parser = TaskParser('contents/lesson6_variables_datatypes_tasks.md')
tasks = parser.parse()

for task in tasks:
    print(f"Testing Task {task['order_index']}...")
    # Extract and run solution code
    # Compare with expected output
```

---

## Upsert Workflow

### 8. Step-by-Step Process

**Step 1: Identify Lesson Information**
```python
# Query database for lesson details
from app import create_app
from app.models import NewTutorial, Lesson

app = create_app()
with app.app_context():
    tutorial = NewTutorial.query.get(COURSE_ID)
    lesson = Lesson.query.get(LESSON_ID)
    
    print(f"Tutorial: {tutorial.title}")
    print(f"Lesson: {lesson.title}")
    print(f"Type: {tutorial.course_type}")
```

**Step 2: Create Markdown File**
- File location: `contents/lesson{lesson_id}_{topic}_tasks.md`
- Include all 5 tasks with solutions
- Follow structure exactly as shown above

**Step 3: Test Before Upserting**
```bash
# Run test suite
python db_tester/test_upsert_lesson{lesson_id}.py
```

**Step 4: Run Upsert Script**
```bash
# Only after all tests pass
python upsert_lesson{lesson_id}_tasks.py
```

**Step 5: Verify Database**
```python
# Check exercises were created/updated correctly
exercises = Exercise.query.filter_by(lesson_id=LESSON_ID).all()
for ex in exercises:
    print(f"{ex.order_index}. {ex.title} ({ex.difficulty})")
```

---

## Task Templates

### 9. Template for Easy Task

```markdown
## Task X: [Simple Action with Clear Goal]

**Objective:** Practice [single concept].

**Instructions:**
1. Create [specific item]
2. [Simple action]
3. Print [clear output]

**Expected Output:**
```
[2-4 lines of simple output]
```

**Difficulty:** Easy  
**Estimated Time:** 10-15 minutes

### Solution:
```python
# Task X: [Title]

# Step 1
[code]

# Step 2
[code]

# Step 3
print([simple output])
```
```

### 10. Template for Medium Task

```markdown
## Task X: [Combine Related Concepts]

**Objective:** Combine [concept A] and [concept B] to solve a problem.

**Instructions:**
1. Create [items related to both concepts]
2. Perform [calculation or logic]
3. Display [formatted result]

**Expected Output:**
```
[4-6 lines with some formatting]
```

**Difficulty:** Medium  
**Estimated Time:** 20-25 minutes

### Solution:
```python
# Task X: [Title]

# Setup
[initialization code]

# Processing
[logic code with comments]

# Output
print([formatted results])
```
```

---

## Common Mistakes to Avoid

### ❌ DON'T:

1. **Complex Calculations**
   ```python
   # Bad: Too many steps
   total = price * quantity
   tax = total * 0.08
   discount = total * 0.15
   shipping = 5.99 if total < 50 else 0
   final = total + tax - discount + shipping
   ```

2. **Long Output Requirements**
   ```python
   # Bad: 15+ lines of output
   print("="*50)
   print("DETAILED REPORT")
   print("="*50)
   # ... 12 more lines
   ```

3. **Ambiguous Instructions**
   ```markdown
   # Bad: Unclear what to do
   "Create some variables and do something with them"
   ```

4. **Missing or Broken Solution Code**
   ```python
   # Bad: Incomplete solution
   def solve():
       # TODO: implement this
       pass
   ```

### ✅ DO:

1. **Simple, Clear Calculations**
   ```python
   # Good: Focused and simple
   total = price * quantity
   final = total - discount
   print(f"Total: ${final:.2f}")
   ```

2. **Concise Output**
   ```python
   # Good: 3-5 lines
   print(f"Name: {name}")
   print(f"Age: {age}")
   print(f"City: {city}")
   ```

3. **Crystal Clear Instructions**
   ```markdown
   # Good: Step-by-step clarity
   1. Create a variable `name` with your name
   2. Create a variable `age` with your age
   3. Print both variables with labels
   ```

4. **Complete Working Solution**
   ```python
   # Good: Fully implemented and tested
   name = "Alice"
   age = 25
   print(f"Name: {name}")
   print(f"Age: {age}")
   ```

---

## Reusable Scripts

### 11. Generic Upsert Script Template

Save as: `upsert_lesson_tasks.py` (can be reused)

```python
"""
Generic Lesson Task Upserter
Usage: python upsert_lesson_tasks.py <lesson_id> <course_id> <markdown_file>
"""
import sys
from upsert_lesson6_tasks import TaskParser, TaskUpserter
from app import create_app

def main():
    if len(sys.argv) != 4:
        print("Usage: python upsert_lesson_tasks.py <lesson_id> <course_id> <markdown_file>")
        sys.exit(1)
    
    lesson_id = int(sys.argv[1])
    course_id = int(sys.argv[2])
    markdown_file = sys.argv[3]
    
    app = create_app()
    
    with app.app_context():
        parser = TaskParser(markdown_file)
        tasks = parser.parse()
        
        upserter = TaskUpserter(app, course_id=course_id, lesson_id=lesson_id)
        results = upserter.upsert_all(tasks)
        
        # Print summary
        successful = [r for r in results if r['success']]
        print(f"✓ Created/Updated: {len(successful)} tasks")

if __name__ == '__main__':
    main()
```

**Usage Example:**
```bash
python upsert_lesson_tasks.py 7 5 contents/lesson7_control_flow_tasks.md
```

---

## Quality Checklist

### Before Upserting, Verify:

- [ ] File is in `contents/` directory
- [ ] File name follows `lesson{id}_{topic}_tasks.md` pattern
- [ ] Exactly 5 tasks included
- [ ] 3 easy + 2 medium difficulty distribution
- [ ] Each task has clear objective
- [ ] Instructions are step-by-step and numbered
- [ ] Expected output is 3-5 lines (7 max)
- [ ] Solution code is complete and tested
- [ ] Solution code produces EXACT expected output
- [ ] All solutions run without errors
- [ ] Difficulty levels are appropriate
- [ ] Estimated times are realistic
- [ ] No complex or frustrating requirements
- [ ] db_tester tests pass 100%
- [ ] Database query confirms course_id and lesson_id exist

---

## Quick Reference Commands

```bash
# 1. Check lesson exists
python -c "from app import create_app; from app.models import Lesson; app=create_app(); ctx=app.app_context(); ctx.push(); lesson=Lesson.query.get(LESSON_ID); print(lesson.title if lesson else 'Not found')"

# 2. Create task file
# Edit: contents/lesson{id}_topic_tasks.md

# 3. Test parsing
python db_tester/test_upsert_lesson{id}.py

# 4. Run upsert
python upsert_lesson{id}_tasks.py

# 5. Verify results
python -c "from app import create_app; from app.models import Exercise; app=create_app(); ctx=app.app_context(); ctx.push(); exs=Exercise.query.filter_by(lesson_id=LESSON_ID).all(); [print(f'{e.order_index}. {e.title}') for e in exs]"
```

---

## Summary

**Golden Rules:**
1. ✅ Always use `contents/` folder
2. ✅ Always include complete solution code
3. ✅ Always test solutions produce expected output
4. ✅ Keep tasks simple - students should succeed, not give up
5. ✅ Keep output short - 3-5 lines maximum
6. ✅ Test everything before upserting
7. ✅ Follow 3 easy + 2 medium difficulty pattern

**Remember:** The goal is to help students learn and build confidence, not to frustrate them with overly complex tasks!

---

**Last Updated:** December 14, 2025  
**Version:** 1.0
