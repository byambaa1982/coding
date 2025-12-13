# Step 2: UI/UX Restructuring Plan

## Overview
Enhance the exercise page UI to show clear progression through subtopics and guide users through the 3-exercise-per-subtopic flow.

## UI Components to Add

### 1. Progress Indicator
- Show "Exercise X of 3" for current subtopic
- Visual progress bar for subtopic completion
- Topic and subtopic context

### 2. Exercise Navigation
- Previous/Next exercise buttons within subtopic
- "Complete & Continue" button that routes to next exercise
- Smart routing after completing all 3 exercises

### 3. Completion Feedback
- Celebration message when subtopic is complete
- Preview of next subtopic
- Auto-redirect option

### 4. Sidebar Enhancement
- List all 3 exercises in current subtopic
- Show completion status (✓ completed, ○ incomplete, → current)
- Show difficulty and points

## Implementation Files
1. `app/templates/python_practice/exercise.html` - Main UI updates
2. `app/python_practice/routes.py` - Add helper data to context
3. `app/account/utils.py` - Already has Continue Learning logic
4. CSS updates for visual polish

## Flow
```
Exercise 1 → Complete → Exercise 2 → Complete → Exercise 3 → Complete → Next Subtopic Exercise 1
```
