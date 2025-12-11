# Phase 5 Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### Prerequisites
- Python 3.8+
- MySQL database running
- Redis (optional, for Celery)

### Step-by-Step Setup

#### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

#### 2. Create Database Tables
```powershell
python create_phase5_tables.py
```

#### 3. Add Sample Exercises
```powershell
python add_sample_python_exercises.py
```

#### 4. Run the Application
```powershell
python app.py
```

#### 5. Test It!
Open your browser and navigate to:
```
http://localhost:5000/python-practice/exercise/1
```

You should see the Python code editor with the "Hello World" exercise!

---

## 🧪 Testing the Code Editor

### Test Exercise 1: Hello World
1. Navigate to `/python-practice/exercise/1`
2. You'll see starter code:
   ```python
   def greet():
       # Write your code here
       pass
   ```
3. Replace with:
   ```python
   def greet():
       return "Hello, World!"
   ```
4. Click "Run Code"
5. ✅ You should see "Test Passed" with a green checkmark!

### Test Exercise 2: Add Two Numbers
1. Navigate to `/python-practice/exercise/2`
2. Complete the function:
   ```python
   def add_numbers(a, b):
       return a + b
   ```
3. Run the code
4. ✅ All 3 tests should pass!

---

## 🔧 Advanced Setup (Optional)

### Setup Redis + Celery for Async Execution

#### 1. Start Redis
```powershell
# Using Docker (recommended)
docker run -d -p 6379:6379 redis:alpine

# OR install Redis for Windows
# Download from: https://github.com/microsoftarchive/redis/releases
```

#### 2. Start Celery Worker
```powershell
celery -A app.celery_app:celery worker --loglevel=info --pool=solo
```

#### 3. Start Celery Beat (periodic tasks)
```powershell
celery -A app.celery_app:celery beat --loglevel=info
```

### Setup Docker Sandbox (Production)

#### 1. Build Sandbox Image
```powershell
cd sandbox/python
docker build -t python-sandbox:latest .
cd ../..
```

#### 2. Test Docker Execution
```python
from app.python_practice.sandbox import PythonSandbox

sandbox = PythonSandbox()
sandbox.connect()
result = sandbox.execute('print("Hello from Docker!")')
print(result)
```

---

## 🎓 Usage Examples

### Creating a New Exercise

```python
from app import create_app
from app.extensions import db
from app.models import Exercise
import json

app = create_app()

with app.app_context():
    exercise = Exercise(
        tutorial_id=1,
        lesson_id=1,
        title='Find Maximum',
        slug='find-maximum',
        description='Write a function that finds the maximum number in a list',
        exercise_type='python',
        difficulty='easy',
        starter_code='def find_max(numbers):\n    pass',
        solution_code='def find_max(numbers):\n    return max(numbers)',
        test_cases=json.dumps([
            {
                'test_number': 1,
                'description': 'Find max in positive numbers',
                'function_name': 'find_max',
                'input': [[1, 5, 3, 9, 2]],
                'expected': 9
            },
            {
                'test_number': 2,
                'description': 'Find max with negative numbers',
                'function_name': 'find_max',
                'input': [[-5, -2, -10, -1]],
                'expected': -1
            }
        ]),
        hints=json.dumps([
            'Use Python\'s built-in max() function',
            'Or loop through the list to find the largest number'
        ]),
        points=15
    )
    
    db.session.add(exercise)
    db.session.commit()
    print(f"Exercise created with ID: {exercise.id}")
```

### Checking User Progress

```python
from app.models import ExerciseSubmission, TutorialUser

user = TutorialUser.query.get(1)
submissions = ExerciseSubmission.query.filter_by(
    user_id=user.id,
    status='passed'
).all()

print(f"{user.email} has passed {len(submissions)} exercises")
```

---

## 🐛 Troubleshooting

### Issue: Code won't execute
**Solution**: Check if Python is in your PATH
```powershell
python --version
```

### Issue: Monaco Editor not loading
**Solution**: Check browser console for CDN errors. Ensure internet connection.

### Issue: Database error
**Solution**: Verify MySQL is running and credentials are correct in `.env`
```
DB_HOST=your_host
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
```

### Issue: Rate limit error
**Solution**: Rate limiter resets after 1 minute. Or manually reset:
```python
from app.python_practice.rate_limiter import code_execution_limiter
code_execution_limiter.reset('user_1')
```

---

## 📚 API Reference

### Submit Code
```
POST /python-practice/exercise/<id>/submit
Content-Type: application/json

{
    "code": "def greet():\n    return 'Hello, World!'"
}

Response:
{
    "status": "passed",
    "output": "",
    "error": "",
    "test_results": [...],
    "tests_passed": 1,
    "tests_failed": 0,
    "score": 100.0,
    "execution_time_ms": 45
}
```

### Get Hints
```
GET /python-practice/exercise/<id>/hints

Response:
{
    "hints": [
        "Use the return statement",
        "Remember to return a string"
    ]
}
```

### View Solution
```
GET /python-practice/exercise/<id>/solution

Response:
{
    "solution": "def greet():\n    return 'Hello, World!'"
}
```

---

## 🎯 Performance Tips

1. **Database Indexing**: Ensure indexes on `user_id`, `exercise_id`, `status`
2. **Caching**: Use Redis to cache test cases and exercise data
3. **Connection Pooling**: Configure SQLAlchemy pool size
4. **Celery Queues**: Separate queues for different task priorities
5. **Docker Pooling**: Pre-warm Docker containers for faster execution

---

## ✅ Feature Checklist

Core Features:
- [x] Code editor with syntax highlighting
- [x] Code execution with test validation
- [x] Security validation
- [x] Rate limiting
- [x] Hints system
- [x] Solution viewing
- [x] Progress tracking
- [x] Error handling
- [x] Mobile responsive

Advanced Features (TODO):
- [ ] Real-time collaboration
- [ ] Code debugging tools
- [ ] Performance profiling
- [ ] Code linting
- [ ] Git integration
- [ ] Plagiarism detection
- [ ] AI-powered hints

---

## 🎉 Success!

You now have a fully functional Python code practice environment! Users can:
- ✅ Write and execute Python code
- ✅ Get instant feedback on their solutions
- ✅ Learn from hints and solutions
- ✅ Track their progress
- ✅ Practice with validated exercises

Next: Implement Phase 6 (SQL Practice Environment) 🚀
