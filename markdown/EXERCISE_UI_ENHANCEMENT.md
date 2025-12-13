# Exercise Page UI Enhancement Design

## Current vs. Enhanced Layout

### Current UI (Shows):
- Exercise title
- Description  
- Points
- Course name
- Code editor

### Enhanced UI (Will Show):
```
┌─────────────────────────────────────────────────────────┐
│ [Breadcrumb Navigation]                                  │
│ Course > Topic > Subtopic > Exercise                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Exercise Title                          [Difficulty]    │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## Database Model Mapping

**All required data is available in the current database model:**

```python
# Already exists in models.py
Exercise:
  - tutorial_id (FK) → Course
  - lesson_id (FK) → Lesson/Subtopic
  - title → Exercise name
  
Lesson:
  - section_name → Topic/Section name
  - title → Subtopic name
  - tutorial_id → Course

NewTutorial:
  - title → Course name
```

### Mapping:
1. **Course**: `exercise.tutorial.title`
2. **Topic**: `exercise.lesson.section_name` (e.g., "Section 1: Python Fundamentals")
3. **Subtopic**: `exercise.lesson.title` (e.g., "Introduction to Python Programming")
4. **Exercise**: `exercise.title` (e.g., "Exercise 1: Variables and Math")

## UI Design

### Breadcrumb Navigation
```html
Course Name > Topic Name > Subtopic Name > Exercise Name
     ↓             ↓              ↓              ↓
  Tutorial    Section Name   Lesson Title   Exercise Title
```

### Visual Layout
```
┌──────────────────────────────────────────────────────────────┐
│  Home > Python Programming > Python Fundamentals >           │
│         Introduction to Python > Exercise 1                  │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  📚 Python Programming for Complete Beginners                │
│  📖 Section 1: Python Fundamentals                           │
│  📝 Introduction to Python Programming                       │
│                                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Exercise 1: Variables and Math          [EASY]    │     │
│  │                                           [✓ Solved]│     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Implementation Changes

### Files to Modify:
1. `app/templates/python_practice/exercise.html` - Add breadcrumb and hierarchy
2. `app/templates/sql_practice/exercise.html` - Same changes for SQL
3. `app/static/css/main.css` (optional) - Styling for breadcrumb

### No Database Changes Required ✅

The current model already has all relationships:
- Exercise → Lesson (via lesson_id)
- Exercise → Tutorial (via tutorial_id)  
- Lesson → Tutorial (via tutorial_id)
- Lesson has section_name field for topic grouping

## Benefits

1. **Better Navigation**: Users know exactly where they are in the course
2. **Context Awareness**: See topic and subtopic while practicing
3. **Easy Navigation**: Click breadcrumb to go back to any level
4. **Professional Look**: Standard UI pattern for hierarchical content
5. **No Breaking Changes**: Only template modification needed
