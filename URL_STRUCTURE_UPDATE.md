# URL Structure Update - Nested Routes

## Overview
The Python practice module now uses a cleaner, nested URL structure for better navigation and SEO.

## New URL Structure

### Before (Old URLs)
```
/python-practice/course/3/subtopics          → View all lessons in a course
/python-practice/lesson/5/exercises          → View all exercises in a lesson  
/python-practice/exercise/24                 → View a specific exercise
```

### After (New URLs)
```
/python-practice/course/3/subtopics                      → View all lessons (subtopics)
/python-practice/course/3/subtopics/5                   → View exercises for lesson 5
/python-practice/course/3/subtopics/5/exercise/2        → View exercise at order index 2
```

## Key Changes

### 1. Unified Route Handler
All course navigation now goes through a single route handler `course_subtopics()` with optional parameters:
- `course_id` - Required, identifies the course
- `lesson_id` - Optional, shows exercises for a specific lesson
- `exercise_order` - Optional, shows a specific exercise by its order_index

### 2. Backward Compatibility
Old URLs still work via redirect:
- `/python-practice/lesson/5/exercises` automatically redirects to `/python-practice/course/3/subtopics/5`
- `/python-practice/exercise/24` continues to work as before

### 3. Exercise Order vs Exercise ID
The new nested URL uses `exercise_order` (the order_index field) instead of `exercise_id`:
- More user-friendly (exercise 1, 2, 3 instead of random IDs)
- Easier to predict and share URLs
- When clicked, redirects to the actual exercise view with the exercise_id

## Benefits

1. **Cleaner URLs**: More intuitive hierarchy showing course → lesson → exercise
2. **Better SEO**: Search engines prefer hierarchical URL structures
3. **User-Friendly**: URLs are predictable and easier to share
4. **Maintainability**: Single route handler reduces code duplication

## Implementation Details

### Route Definition
```python
@python_practice_bp.route('/course/<int:course_id>/subtopics')
@python_practice_bp.route('/course/<int:course_id>/subtopics/<int:lesson_id>')
@python_practice_bp.route('/course/<int:course_id>/subtopics/<int:lesson_id>/exercise/<int:exercise_order>')
@login_required
def course_subtopics(course_id, lesson_id=None, exercise_order=None):
    # Handles all three URL patterns with a single function
    ...
```

### Template Usage
```jinja2
{# Link to all subtopics #}
<a href="{{ url_for('python_practice.course_subtopics', course_id=course_id) }}">

{# Link to lesson exercises #}
<a href="{{ url_for('python_practice.course_subtopics', course_id=course_id, lesson_id=lesson.id) }}">

{# Link to specific exercise #}
<a href="{{ url_for('python_practice.course_subtopics', course_id=course_id, lesson_id=lesson.id, exercise_order=exercise.order_index) }}">
```

## Files Modified

1. **app/python_practice/routes.py**
   - Updated `course_subtopics()` to handle nested routing
   - Modified `view_exercise()` to accept course_id and lesson_id parameters
   - Updated `lesson_exercises()` to redirect to new URL structure

2. **app/templates/python_practice/course_subtopics.html**
   - Updated lesson links to use new nested URLs

3. **app/templates/python_practice/lesson_exercises.html**
   - Updated breadcrumbs and navigation to use course_id
   - Updated exercise links to use nested URL structure

4. **app/templates/python_practice/exercise.html**
   - Updated breadcrumb navigation
   - Updated prev/next exercise navigation buttons

## Testing

To test the new URL structure:

1. **View subtopics**: Navigate to `/python-practice/course/3/subtopics`
2. **View lesson exercises**: Click on a lesson or go to `/python-practice/course/3/subtopics/5`
3. **View exercise**: Click on an exercise or go to `/python-practice/course/3/subtopics/5/exercise/0`
4. **Test backward compatibility**: Try old URLs like `/python-practice/lesson/5/exercises`

## Migration Notes

- No database changes required
- All existing URLs continue to work via redirects
- Templates updated to generate new URL format
- Can gradually update other templates that still use old URLs

## Future Enhancements

Consider adding similar nested routing for:
- SQL practice module
- Quiz navigation
- Other content types
