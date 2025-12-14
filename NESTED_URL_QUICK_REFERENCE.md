# Quick Reference: New Nested URL Structure

## URL Patterns

### ✅ New Nested URLs (RECOMMENDED)
```
/python-practice/course/3/subtopics                     → All lessons in course 3
/python-practice/course/3/subtopics/5                   → Exercises in lesson 5
/python-practice/course/3/subtopics/5/exercise/0        → First exercise (order_index=0)
```

### ⚠️ Legacy URLs (Still work, but redirect)
```
/python-practice/lesson/5/exercises                     → Redirects to new structure
/python-practice/exercise/24                            → Still works as before
```

## Template Usage Examples

### Link to course subtopics page
```jinja2
<a href="{{ url_for('python_practice.course_subtopics', course_id=tutorial.id) }}">
    View All Lessons
</a>
```

### Link to lesson exercises
```jinja2
<a href="{{ url_for('python_practice.course_subtopics', 
                    course_id=tutorial.id, 
                    lesson_id=lesson.id) }}">
    View Exercises
</a>
```

### Link to specific exercise (by order)
```jinja2
<a href="{{ url_for('python_practice.course_subtopics', 
                    course_id=tutorial.id, 
                    lesson_id=lesson.id, 
                    exercise_order=exercise.order_index) }}">
    Exercise {{ exercise.order_index + 1 }}
</a>
```

### Legacy exercise link (still works)
```jinja2
<a href="{{ url_for('python_practice.view_exercise', exercise_id=exercise.id) }}">
    View Exercise
</a>
```

## Python Code Examples

### Redirect to lesson exercises
```python
from flask import redirect, url_for

# New way
return redirect(url_for('python_practice.course_subtopics', 
                       course_id=3, 
                       lesson_id=5))

# Old way (still works)
return redirect(url_for('python_practice.lesson_exercises', lesson_id=5))
```

### Generate exercise URL
```python
# By order (new nested URL)
url = url_for('python_practice.course_subtopics',
              course_id=course.id,
              lesson_id=lesson.id,
              exercise_order=0)  # First exercise

# By ID (legacy)
url = url_for('python_practice.view_exercise', exercise_id=24)
```

## Key Points

1. **Course ID is now required** - The nested structure always starts with the course ID
2. **Exercise order vs ID** - The nested URL uses `order_index` (0, 1, 2...), not the database ID
3. **Backward compatible** - Old URLs automatically redirect to the new structure
4. **Cleaner URLs** - Users see `/course/3/subtopics/5/exercise/2` instead of separate endpoints

## Migration Checklist

- [x] Routes updated in `app/python_practice/routes.py`
- [x] Templates updated:
  - [x] `course_subtopics.html`
  - [x] `lesson_exercises.html`
  - [x] `exercise.html`
- [ ] Other templates (optional updates):
  - [ ] `learning/lesson.html`
  - [ ] `catalog/course_detail.html`
  - [ ] `account/dashboard.html`
  - [ ] Admin templates

## Testing

Run the test script to verify routes:
```bash
python test_route_registration.py
```

Start the server and test URLs manually:
```bash
python run_server.py

# Then visit:
# http://127.0.0.1:5000/python-practice/course/3/subtopics
# http://127.0.0.1:5000/python-practice/course/3/subtopics/5
# http://127.0.0.1:5000/python-practice/course/3/subtopics/5/exercise/0
```
