"""
Test script for Step 2 UI implementation
Verifies the enhanced exercise page with progression indicators
"""
from app import create_app, db
from app.models import Exercise, Lesson, TutorialEnrollment, ExerciseSubmission, TutorialUser
from sqlalchemy import and_

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("STEP 2 UI TESTING - Exercise Progression")
    print("="*60)
    
    # Get the test user
    user = TutorialUser.query.filter_by(email='byambaa1982@gmail.com').first()
    if not user:
        print("❌ User not found. Please create test user first.")
        exit(1)
    
    print(f"\n✅ Test User: {user.email} (ID: {user.id})")
    
    # Get enrollment for mock course (Tutorial ID 5)
    enrollment = TutorialEnrollment.query.filter_by(
        user_id=user.id,
        tutorial_id=5  # Mock course
    ).first()
    
    if not enrollment:
        print("❌ No enrollment found for mock course. Run enroll_in_mock_course.py first.")
        exit(1)
    
    print(f"✅ Active Enrollment ID: {enrollment.id}")
    
    # Get first lesson (subtopic) in the course
    first_lesson = Lesson.query.filter_by(
        tutorial_id=enrollment.tutorial_id
    ).order_by(Lesson.order_index).first()
    
    if not first_lesson:
        print("❌ No lessons found in enrolled course.")
        exit(1)
    
    print(f"\n📚 First Subtopic: {first_lesson.title}")
    print(f"   Topic: {first_lesson.section_name}")
    
    # Get exercises in first lesson
    exercises = Exercise.query.filter_by(
        lesson_id=first_lesson.id
    ).order_by(Exercise.order_index).all()
    
    print(f"\n📝 Exercises in Subtopic ({len(exercises)} total):")
    print("-" * 60)
    
    for idx, ex in enumerate(exercises, 1):
        # Check if completed
        submission = ExerciseSubmission.query.filter_by(
            user_id=user.id,
            exercise_id=ex.id,
            status='passed'
        ).first()
        
        status = "✅ Completed" if submission else "⭕ Not Started"
        
        print(f"{idx}. Part {idx}: {ex.title}")
        print(f"   Exercise ID: {ex.id}")
        print(f"   Difficulty: {ex.difficulty}")
        print(f"   Points: {ex.points}")
        print(f"   Status: {status}")
        print(f"   URL: http://127.0.0.1:5000/python-practice/exercise/{ex.id}")
        print()
    
    # Test the new route context
    print("\n" + "="*60)
    print("TESTING UI ELEMENTS")
    print("="*60)
    
    first_exercise = exercises[0]
    print(f"\n📍 Testing with: Exercise {first_exercise.id}")
    
    # Simulate route logic
    lesson_exercises = exercises
    current_exercise_index = 0
    
    # Check completed count
    completed_count = ExerciseSubmission.query.filter(
        and_(
            ExerciseSubmission.user_id == user.id,
            ExerciseSubmission.exercise_id.in_([ex.id for ex in exercises]),
            ExerciseSubmission.status == 'passed'
        )
    ).distinct(ExerciseSubmission.exercise_id).count()
    
    total = len(exercises)
    progress_pct = (completed_count / total * 100) if total > 0 else 0
    
    print(f"\n✅ Progress Tracking:")
    print(f"   Completed: {completed_count}/{total}")
    print(f"   Percentage: {progress_pct:.1f}%")
    
    # Navigation
    print(f"\n✅ Navigation:")
    print(f"   Previous Exercise: {'None (First exercise)' if current_exercise_index == 0 else f'Exercise {exercises[current_exercise_index-1].id}'}")
    print(f"   Current Exercise: Exercise {first_exercise.id}")
    print(f"   Next Exercise: {'Exercise ' + str(exercises[1].id) if len(exercises) > 1 else 'None'}")
    
    # Completion check
    if completed_count == total:
        print(f"\n🎉 SUBTOPIC COMPLETE!")
        print(f"   'Next Subtopic' button should appear")
        print(f"   URL: /account/continue-learning/{enrollment.id}")
    else:
        print(f"\n⏳ In Progress ({total - completed_count} exercises remaining)")
    
    print("\n" + "="*60)
    print("MANUAL TESTING STEPS")
    print("="*60)
    print("""
1. Start Flask app: flask run
2. Login as byambaa1982@gmail.com
3. Go to My Courses: http://127.0.0.1:5000/account/my-courses
4. Click 'Continue Learning' button
5. Verify UI elements:
   ✓ Breadcrumb navigation (Course > Topic > Subtopic > Exercise)
   ✓ Hierarchy card showing all levels
   ✓ Progress card showing "X/3 Completed" with progress bar
   ✓ Exercise navigation sidebar showing Part 1, 2, 3
   ✓ Status icons: ▶️ (current), ✅ (completed), ⭕ (incomplete)
   ✓ Previous/Next navigation buttons
   
6. Complete first exercise:
   - Write code that passes tests
   - Submit
   - Verify ✅ appears in sidebar
   - Click 'Next →' button
   
7. Complete second exercise:
   - Verify progress shows "2/3 Completed"
   - Progress bar should be ~66%
   - Click 'Next →' button
   
8. Complete third exercise:
   - Verify progress shows "3/3 Completed"
   - Progress bar should be 100%
   - Should see '🎉 Next Subtopic →' button instead of 'Next'
   
9. Click 'Next Subtopic' button:
   - Should redirect to first exercise of next subtopic
   - Verify breadcrumb updates to new subtopic
   - Verify progress resets to "0/3 Completed"
    """)
    
    print("\n" + "="*60)
    print("Ready to test! Start your Flask app and follow the steps above.")
    print("="*60 + "\n")
