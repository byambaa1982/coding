# Phase 7 Quick Start Guide

## 🚀 Getting Started with User Dashboard & Analytics

This guide will help you set up and test Phase 7 features quickly.

## Prerequisites

✅ Phase 1-6 completed (User auth, courses, enrollment, learning interface)
✅ MySQL database running
✅ Python virtual environment activated

## Step 1: Install Dependencies

```bash
pip install weasyprint==59.0
```

**Note**: WeasyPrint requires system dependencies. Install them first:

### Windows
Download and install GTK3 runtime from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

### macOS
```bash
brew install cairo pango gdk-pixbuf libffi
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

## Step 2: Create Database Tables

```bash
python create_phase7_tables.py
```

Expected output:
```
Creating Phase 7 tables...
✓ Created certificates table
✓ Created reviews table
✓ Created achievements table
✓ Created user_achievements table
✓ Created notifications table
✓ Created learning_streaks table
✓ Created user_analytics table

✅ Phase 7 tables created successfully!
```

## Step 3: Seed Default Achievements

```bash
python seed_achievements.py
```

This creates 20 default achievements:
- First Step, Python Novice, SQL Explorer
- Course Graduate, Python Master, SQL Guru
- Problem Solver, Code Warrior, Exercise Master
- Learning streaks (7, 30, 100 days)
- Quiz Master, Perfect Score
- And more!

## Step 4: Test the Features

### 1. Enhanced Dashboard
```
http://localhost:5000/account/dashboard
```

**What to see:**
- Learning statistics cards
- Recent activity
- Learning streak
- Achievement stats
- Weekly progress chart
- Personalized insights

### 2. Analytics Page
```
http://localhost:5000/account/analytics
```

**What to see:**
- Total learning time
- Courses completed
- Exercises solved
- Weekly activity chart
- Python vs SQL breakdown
- Performance metrics
- Recent completions

### 3. Achievements
```
http://localhost:5000/account/achievements
```

**What to see:**
- Unlocked and locked achievements
- Progress toward locked achievements
- Points earned
- Achievement categories (Learning, Mastery, Social)

### 4. Certificates
```
http://localhost:5000/account/certificates
```

**Note**: Certificates are automatically generated when you complete a course.

To test manually:
```python
# In Flask shell
from app import create_app, db
from app.models import TutorialUser, NewTutorial, TutorialEnrollment
from app.account.certificate_utils import generate_certificate_pdf

app = create_app()
with app.app_context():
    user = TutorialUser.query.first()
    enrollment = TutorialEnrollment.query.filter_by(
        user_id=user.id,
        is_completed=True
    ).first()
    
    if enrollment:
        cert = generate_certificate_pdf(user, enrollment.tutorial, enrollment)
        print(f"Certificate created: {cert.certificate_number}")
```

### 5. Notifications
```
http://localhost:5000/account/notifications
```

**What to see:**
- Achievement unlock notifications
- Certificate notifications
- Course update notifications

## Step 5: Test Achievement Unlocking

### Option 1: Complete a Lesson
1. Go to any enrolled course
2. Complete a lesson
3. Achievement "First Step" should unlock
4. Check `/account/achievements`

### Option 2: Manually Trigger
```python
# In Flask shell
from app import create_app
from app.account.achievement_utils import check_and_unlock_achievements

app = create_app()
with app.app_context():
    user_id = 1  # Your user ID
    newly_unlocked = check_and_unlock_achievements(user_id)
    print(f"Unlocked {len(newly_unlocked)} achievements!")
    for achievement in newly_unlocked:
        print(f"- {achievement.name}")
```

### Option 3: Use Refresh Button
1. Go to `/account/achievements`
2. Click "Check for New Achievements"
3. System will check all criteria and unlock any eligible achievements

## Step 6: Test Certificate Generation

### Complete a Course
1. Enroll in a course
2. Complete all lessons (mark as complete)
3. Complete all exercises
4. Certificate should auto-generate
5. Check `/account/certificates`
6. View and download PDF

### Verify Certificate
1. Go to `/account/certificate/verify`
2. Enter certificate number or verification code
3. See validation result

## Step 7: Test Analytics Updates

### Track Learning Time
```python
from app.account.analytics_utils import track_lesson_time

# Track 30 minutes on a lesson
track_lesson_time(user_id, lesson_id, enrollment_id, seconds_spent=1800)
```

### Update All Analytics
```python
from app.account.analytics_utils import update_user_analytics

update_user_analytics(user_id)
```

### View Analytics
1. Complete some lessons
2. Visit `/account/analytics`
3. See updated statistics
4. Check weekly chart

## Step 8: Test Review System

1. Go to any enrolled course detail page
2. Click "Write a Review" (if available)
3. Or go directly: `/account/tutorial/<tutorial_id>/review`
4. Submit rating (1-5 stars) and comment
5. Achievement "Reviewer" should unlock!

## 🎯 Quick Feature Test Checklist

- [ ] Dashboard loads with stats
- [ ] Analytics page displays charts
- [ ] Achievements show locked/unlocked
- [ ] "First Step" achievement unlocks after first lesson
- [ ] Learning streak updates daily
- [ ] Certificate generates after course completion
- [ ] Certificate PDF downloads successfully
- [ ] Certificate verification works
- [ ] Notifications appear after achievement unlock
- [ ] Mark notification as read works
- [ ] Review submission works
- [ ] Weekly progress chart displays correctly

## 🔧 Troubleshooting

### WeasyPrint Import Error
```
Error: ImportError: weasyprint could not be found
```
**Solution**: Install system dependencies first, then `pip install weasyprint`

### Certificate PDF Not Generating
```
Error: Failed to generate certificate PDF
```
**Solutions**:
- Check WeasyPrint installation
- Ensure `app/static/certificates/` directory exists
- Check file permissions

### Achievement Not Unlocking
**Solutions**:
- Check achievement criteria in `seed_achievements.py`
- Verify criteria logic in `achievement_utils.py`
- Check `UserAchievement` table for progress
- Use refresh button on achievements page

### Analytics Not Updating
**Solutions**:
- Call `update_user_analytics(user_id)` manually
- Check `LessonProgress` and `ExerciseSubmission` tables have data
- Verify foreign key relationships

### Streak Not Updating
**Solutions**:
- Ensure you complete a lesson (mark as complete)
- Check `LearningStreak.update_streak()` is called
- Verify timezone settings (all dates in UTC)

## 📊 Sample Data Commands

### Create Sample Activity
```python
from app import create_app, db
from app.models import LessonProgress, LearningStreak
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    user_id = 1  # Your user ID
    
    # Create 7 days of activity
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        # Add lesson progress for this day
        # ... (use track_lesson_time)
    
    # Update streak
    streak = LearningStreak.query.filter_by(user_id=user_id).first()
    if streak:
        streak.update_streak()
```

## 🎨 Customization Tips

### Change Certificate Design
Edit: `app/templates/account/certificate_template.html`
- Modify colors, fonts, layout
- Add company logo
- Change border style

### Add Custom Achievements
Edit: `seed_achievements.py`
```python
{
    'name': 'Speed Demon',
    'slug': 'speed-demon',
    'description': 'Complete 5 exercises in 10 minutes',
    'achievement_type': 'speed_completion',
    'criteria': json.dumps({'exercises': 5, 'time_minutes': 10}),
    'points': 100,
    'category': 'mastery',
    'difficulty': 'platinum',
    'icon_class': 'fas fa-bolt'
}
```

### Custom Insights
Edit: `app/account/analytics_utils.py` function `get_learning_insights()`
Add your own insight logic.

## 🚀 Next Steps

1. **Test thoroughly** - Complete the checklist above
2. **Customize** - Adjust achievements, certificate design
3. **Deploy** - Push to production
4. **Monitor** - Track user engagement with analytics
5. **Iterate** - Add more achievements based on user behavior

## 📚 Additional Resources

- [Full Implementation Guide](PHASE7_IMPLEMENTATION_COMPLETE.md)
- [Project Plan](TUTORIAL_ECOMMERCE_PROJECT_PLAN.md)
- [WeasyPrint Documentation](https://doc.courtbouillon.org/weasyprint/)

## ✅ Success!

If all tests pass, Phase 7 is complete and ready for use! 🎉

**Questions or issues?** Check the troubleshooting section or review the implementation guide.
