# Phase 4 Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Create Tables
```bash
python create_phase4_tables.py
```

### Step 2: Add Sample Quiz (Optional)
```bash
python add_sample_quiz.py
```

### Step 3: Test the Learning Interface

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Login** to your account

3. **Navigate to your courses**:
   - Go to "My Courses" from the dashboard
   - Click on any enrolled course

4. **View Tutorial Overview**:
   - URL: `/learn/tutorial/<tutorial_id>`
   - See all lessons grouped by sections
   - Check your overall progress

5. **View a Lesson**:
   - Click on any lesson
   - URL: `/learn/lesson/<lesson_id>`
   - Features available:
     - Mark as complete
     - Bookmark lesson
     - Add notes
     - Navigate prev/next

6. **Test Video Player** (if lesson has video):
   - Play/pause with spacebar
   - Skip forward/back with arrow keys
   - Progress auto-saves every 5 seconds
   - Close tab and reopen - should resume

7. **Take a Quiz**:
   - Click "Take Quiz" in lesson page
   - Answer questions
   - Submit quiz
   - View results with explanations

8. **View Progress Dashboard**:
   - Go to `/learn/progress`
   - See statistics, recent activity, bookmarks

---

## 📋 Testing Checklist

### Lesson Viewer
- [ ] Can view lesson content
- [ ] Can mark lesson complete
- [ ] Complete button turns green after marking
- [ ] Progress bar updates
- [ ] Can bookmark lesson (star turns yellow)
- [ ] Can add and save notes
- [ ] Can navigate to prev/next lesson

### Video Player (if video lesson)
- [ ] Video loads and plays
- [ ] Keyboard shortcuts work (space, arrows, f, m)
- [ ] Progress saves automatically
- [ ] Closing and reopening resumes from last position
- [ ] Video at 90%+ auto-completes lesson

### Quiz System
- [ ] Can start quiz
- [ ] Questions display correctly
- [ ] Can select/enter answers
- [ ] Timer counts down (if timed)
- [ ] Can submit quiz
- [ ] Score calculates correctly
- [ ] Can view correct answers and explanations
- [ ] Can retake if attempts remaining
- [ ] Can't retake if max attempts reached

### Progress Dashboard
- [ ] Statistics display correctly
- [ ] Course list shows all enrollments
- [ ] Progress bars reflect actual progress
- [ ] Recent activity shows completed lessons
- [ ] Bookmarked lessons appear in sidebar
- [ ] Learning streak calculates

---

## 🎯 Key URLs

| Feature | URL Pattern | Example |
|---------|-------------|---------|
| Tutorial Overview | `/learn/tutorial/<id>` | `/learn/tutorial/1` |
| View Lesson | `/learn/lesson/<id>` | `/learn/lesson/1` |
| Take Quiz | `/learn/quiz/<id>` | `/learn/quiz/1` |
| Quiz Result | `/learn/quiz/attempt/<id>/result` | `/learn/quiz/attempt/1/result` |
| Progress Dashboard | `/learn/progress` | `/learn/progress` |

---

## 🔧 Troubleshooting

### "You need to enroll in this course first"
- Ensure user is enrolled via payment/manual enrollment
- Check `tutorial_enrollments` table for user_id + tutorial_id

### Video doesn't resume position
- Check browser localStorage
- Verify AJAX request to `/update-video-progress` succeeds
- Check `lesson_progress` table for `video_position_seconds`

### Mark Complete doesn't work
- Check browser console for JavaScript errors
- Verify CSRF token is present
- Check enrollment exists for user

### Quiz doesn't submit
- Ensure all required questions are answered
- Check for JavaScript errors
- Verify form has CSRF token

### Progress bar not updating
- Check `lesson_progress` records exist
- Verify `mark_complete()` method runs successfully
- Check enrollment `progress_percentage` calculation

---

## 📊 Database Queries for Testing

### Check lesson progress
```sql
SELECT * FROM lesson_progress WHERE user_id = 1;
```

### Check quiz attempts
```sql
SELECT * FROM quiz_attempts WHERE user_id = 1;
```

### Check enrollment progress
```sql
SELECT 
    te.progress_percentage,
    te.lessons_completed,
    t.total_lessons,
    t.title
FROM tutorial_enrollments te
JOIN new_tutorials t ON te.tutorial_id = t.id
WHERE te.user_id = 1;
```

### Check quiz scores
```sql
SELECT 
    qa.score,
    qa.passed,
    qa.attempt_number,
    q.title
FROM quiz_attempts qa
JOIN quizzes q ON qa.quiz_id = q.id
WHERE qa.user_id = 1 AND qa.status = 'completed'
ORDER BY qa.completed_at DESC;
```

---

## 🎨 Customization Tips

### Change passing score
Edit `Quiz.passing_score` in database or when creating quiz:
```python
quiz.passing_score = 80.00  # 80% to pass
```

### Disable video auto-complete
In `learning.js`, comment out:
```javascript
// if (progress.video_watched_percentage >= 90 && !progress.is_completed) {
//     progress.mark_complete()
// }
```

### Change video progress save interval
In `learning.js`:
```javascript
// Change from 5000 (5s) to 10000 (10s)
progressInterval = setInterval(() => {
    saveVideoProgress(...);
}, 10000);
```

### Add more quiz question types
Extend `QuizQuestion.question_type` in models.py and add handling in templates.

---

## 💡 Tips for Content Creators

### Creating Effective Quizzes
1. Mix question types (MC, T/F, text)
2. Include explanations for all answers
3. Set reasonable time limits (1-2 min per question)
4. Use 3-5 attempts max
5. Passing score: 70-80% for learning, 90%+ for certification

### Video Best Practices
1. Keep videos under 15 minutes
2. Use clear, high-quality audio
3. Add timestamps in description
4. Provide transcript in lesson notes
5. Host on CDN for best performance

### Lesson Organization
1. Group related lessons in sections
2. Use descriptive titles
3. Add estimated duration
4. Mark preview lessons as free
5. Progress from easy to hard

---

## 🆘 Getting Help

1. Check Phase 4 documentation: `markdown/PHASE4_COMPLETE.md`
2. Review browser console for errors
3. Check Flask logs for backend errors
4. Verify database tables exist
5. Test with simple lesson first

---

## ✅ Success Indicators

You've successfully implemented Phase 4 if:

✅ Can view lessons with proper layout
✅ Progress tracking works (lessons, videos)
✅ Quizzes can be taken and scored
✅ Dashboard shows accurate statistics
✅ Bookmarks and notes save correctly
✅ Video resumes from last position
✅ AJAX updates work without page refresh

---

**Ready for Phase 5?** Next up is the Interactive Python Code Editor with sandboxing! 🐍
