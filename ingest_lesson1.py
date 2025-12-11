"""
Script to ingest Lesson 1: Welcome to Python Programming into the database.
This is a test ingestion based on PYTHON_BEGINNER_TUTORIAL_PLAN.md
"""

from app import create_app
from app.extensions import db
from app.models import TutorialUser, NewTutorial, Lesson
from datetime import datetime


def create_test_instructor():
    """Create a test instructor user if not exists."""
    instructor = TutorialUser.query.filter_by(email='instructor@test.com').first()
    
    if not instructor:
        instructor = TutorialUser(
            email='instructor@test.com',
            username='python_instructor',
            full_name='Python Content Creator',
            is_instructor=True,
            is_admin=True,
            email_verified=True,
            bio='Expert Python instructor with 10+ years of teaching experience'
        )
        instructor.set_password('instructor123')
        db.session.add(instructor)
        db.session.commit()
        print(f"✅ Created instructor: {instructor.email}")
    else:
        print(f"✅ Instructor already exists: {instructor.email}")
    
    return instructor


def create_python_beginner_tutorial(instructor):
    """Create the Python Beginner Tutorial."""
    # Check if tutorial already exists
    tutorial = NewTutorial.query.filter_by(slug='python-programming-fundamentals').first()
    
    if not tutorial:
        tutorial = NewTutorial(
            instructor_id=instructor.id,
            title='Python Programming Fundamentals for Absolute Beginners',
            slug='python-programming-fundamentals',
            description="""Master Python programming from scratch with no prior experience needed. 
            This comprehensive beginner course covers everything from basic syntax to building real applications.
            Through hands-on exercises and interactive practice, you'll develop solid programming fundamentals 
            and build confidence to tackle real-world Python projects.""",
            short_description='Learn Python programming from zero to building real applications - perfect for complete beginners.',
            course_type='python',
            category='Programming Fundamentals',
            difficulty_level='beginner',
            language='en',
            price=19.99,
            currency='USD',
            is_free=False,
            status='published',
            is_featured=True,
            estimated_duration_hours=12.5,
            total_lessons=1,  # Starting with just Lesson 1 for testing
            tags='python,beginner,programming,fundamentals,coding',
            published_at=datetime.utcnow()
        )
        db.session.add(tutorial)
        db.session.commit()
        print(f"✅ Created tutorial: {tutorial.title}")
    else:
        print(f"✅ Tutorial already exists: {tutorial.title}")
    
    return tutorial


def create_lesson1(tutorial):
    """Create Lesson 1: Welcome to Python Programming."""
    # Check if lesson already exists
    lesson = Lesson.query.filter_by(
        tutorial_id=tutorial.id,
        slug='welcome-to-python-programming'
    ).first()
    
    if not lesson:
        lesson_content = """
# Welcome to Python Programming

## What is Python?

Python is a powerful, beginner-friendly programming language used by millions of developers worldwide. 
Created by Guido van Rossum in 1991, Python emphasizes code readability and simplicity, making it 
the perfect first programming language.

### Why Learn Python?

1. **Easy to Learn**: Python's syntax is clear and intuitive, similar to writing in English
2. **Versatile**: Used in web development, data science, AI, automation, and more
3. **High Demand**: One of the most sought-after skills in the job market
4. **Great Community**: Millions of developers ready to help and share knowledge
5. **Powerful Libraries**: Thousands of pre-built tools for any task you can imagine

## Real-World Applications of Python

### Web Development
Companies like Instagram, Spotify, and Netflix use Python to build their web applications using 
frameworks like Django and Flask.

### Data Science & AI
Python is the #1 language for data analysis, machine learning, and artificial intelligence. 
Libraries like pandas, NumPy, and TensorFlow power cutting-edge research.

### Automation
Python can automate repetitive tasks - from organizing files to sending emails to web scraping.

### Game Development
Games like Battlefield 2 and EVE Online use Python for game logic and tools.

### Scientific Computing
NASA, CERN, and research institutions use Python for scientific calculations and simulations.

## Your First Python Program: "Hello, World!"

Every programmer's journey begins with a simple program that displays "Hello, World!" on the screen.

```python
print("Hello, World!")
```

That's it! Just one line of code. When you run this program, Python will display:

```
Hello, World!
```

### Understanding the Code

- `print()` is a built-in Python **function** that displays text
- The text inside quotes is called a **string** - a piece of text data
- The parentheses `()` tell Python to execute the function
- You can use single quotes `'` or double quotes `"` for strings

### Try It Yourself

Let's customize your first program:

```python
print("Hello, my name is [Your Name]!")
print("I'm learning Python!")
print("This is exciting!")
```

Notice how each `print()` statement displays text on a new line.

## Setting Up Your Python Environment

### Installing Python

1. **Visit**: https://www.python.org/downloads/
2. **Download**: The latest Python 3.x version (Python 3.11 or newer recommended)
3. **Install**: Run the installer
   - ✅ Check "Add Python to PATH" (important!)
   - Click "Install Now"

### Verifying Installation

Open your terminal (Command Prompt on Windows, Terminal on Mac/Linux) and type:

```bash
python --version
```

You should see something like: `Python 3.11.5`

### Python Interactive Shell

Python comes with an interactive shell where you can type code and see results immediately.

To open it, type in your terminal:

```bash
python
```

You'll see something like:

```
Python 3.11.5 (main, ...)
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

The `>>>` is called the **Python prompt** - it's waiting for your commands!

Try typing:

```python
>>> print("Hello, World!")
Hello, World!
>>> 2 + 2
4
>>> "Python" + " is " + "awesome!"
'Python is awesome!'
```

To exit the shell, type:

```python
>>> exit()
```

### Writing Python Files

Instead of using the interactive shell, you can write Python code in files with a `.py` extension.

1. Create a file called `hello.py`
2. Write your code:
   ```python
   print("Hello from a Python file!")
   ```
3. Run it from terminal:
   ```bash
   python hello.py
   ```

## Python Development Tools

### Text Editors and IDEs

- **VS Code** (Recommended for beginners): Free, powerful, great Python support
- **PyCharm**: Professional Python IDE with many features
- **IDLE**: Comes bundled with Python, simple and lightweight
- **Jupyter Notebook**: Great for learning and data science

For this course, we'll use the built-in interactive code editor on our platform, 
but feel free to practice in any environment you prefer!

## What's Next?

In the next lesson, we'll learn about:
- **Variables**: Storing and managing data
- **Data Types**: Understanding different kinds of information (numbers, text, etc.)
- **Basic Operations**: Performing calculations and manipulations

## Key Takeaways

✅ Python is a beginner-friendly, powerful programming language  
✅ Python is used in web development, data science, AI, automation, and more  
✅ Your first program: `print("Hello, World!")`  
✅ The interactive shell lets you try code instantly  
✅ Python files end with `.py` extension  
✅ You're ready to start your programming journey!

## Practice Challenge

Before moving to the next lesson, make sure you can:

1. ✅ Open the Python interactive shell
2. ✅ Run `print("Hello, World!")`
3. ✅ Print your own custom message
4. ✅ Exit the shell with `exit()`

**Congratulations!** 🎉 You've taken your first step into the world of programming. 
In the next lesson, we'll start writing real code to solve problems!

---

**Lesson Duration**: 30 minutes  
**Difficulty**: Beginner  
**Prerequisites**: None
"""
        
        lesson = Lesson(
            tutorial_id=tutorial.id,
            title='Welcome to Python Programming',
            slug='welcome-to-python-programming',
            description='Introduction to Python programming, installation, and your first program',
            content_type='text',
            content=lesson_content,
            section_name='Section 1: Getting Started with Python',
            order_index=1,
            is_free_preview=True,  # Make first lesson free
            estimated_duration_minutes=30
        )
        db.session.add(lesson)
        db.session.commit()
        print(f"✅ Created lesson: {lesson.title}")
    else:
        print(f"✅ Lesson already exists: {lesson.title}")
    
    return lesson


def main():
    """Main function to run the ingestion."""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("🚀 Starting Lesson 1 Ingestion for Python Beginner Tutorial")
        print("="*70 + "\n")
        
        try:
            # Step 1: Create instructor
            print("Step 1: Creating test instructor...")
            instructor = create_test_instructor()
            
            # Step 2: Create tutorial
            print("\nStep 2: Creating Python Beginner Tutorial...")
            tutorial = create_python_beginner_tutorial(instructor)
            
            # Step 3: Create Lesson 1
            print("\nStep 3: Creating Lesson 1: Welcome to Python Programming...")
            lesson = create_lesson1(tutorial)
            
            print("\n" + "="*70)
            print("✅ SUCCESS! Lesson 1 ingestion completed")
            print("="*70)
            print(f"\nTutorial ID: {tutorial.id}")
            print(f"Tutorial Slug: {tutorial.slug}")
            print(f"Lesson ID: {lesson.id}")
            print(f"Lesson Slug: {lesson.slug}")
            print(f"\n📚 Tutorial: {tutorial.title}")
            print(f"📖 Lesson: {lesson.title}")
            print(f"⏱️  Duration: {lesson.estimated_duration_minutes} minutes")
            print(f"🆓 Free Preview: {lesson.is_free_preview}")
            print(f"\n🔗 Access at: /catalog/course/{tutorial.slug}/lesson/{lesson.slug}")
            
        except Exception as e:
            print(f"\n❌ ERROR during ingestion: {str(e)}")
            db.session.rollback()
            raise
        
        print("\n" + "="*70)


if __name__ == '__main__':
    main()
