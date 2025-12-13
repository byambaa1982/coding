# test_continue_learning.py
"""Test the Continue Learning feature."""

from app import create_app
from app.models import TutorialEnrollment, Lesson, Exercise, LessonProgress, ExerciseSubmission
from app.account.utils import get_continue_learning_destination
from app.extensions import db

app = create_app()

with app.app_context():
    with app.test_request_context():
        # Test with a real enrollment
        enrollment = TutorialEnrollment.query.first()
    
    if enrollment:
        print(f"\n🔍 Testing Continue Learning Feature")
        print(f"=" * 60)
        print(f"Enrollment ID: {enrollment.id}")
        print(f"User ID: {enrollment.user_id}")
        print(f"Course: {enrollment.tutorial.title}")
        print(f"Progress: {enrollment.progress_percentage}%")
        print(f"Lessons Completed: {enrollment.lessons_completed}")
        print(f"Exercises Completed: {enrollment.exercises_completed}")
        print(f"Last Accessed Lesson: {enrollment.last_accessed_lesson_id}")
        
        # Get destination
        destination = get_continue_learning_destination(
            enrollment.user_id,
            enrollment.id
        )
        
        print(f"\n📍 Destination:")
        print(f"Type: {destination['type']}")
        print(f"URL: {destination['url']}")
        if 'id' in destination:
            print(f"ID: {destination['id']}")
        
        # Check lesson details if applicable
        if enrollment.last_accessed_lesson_id:
            lesson = Lesson.query.get(enrollment.last_accessed_lesson_id)
            if lesson:
                print(f"\n📚 Last Accessed Lesson:")
                print(f"Title: {lesson.title}")
                print(f"Order: {lesson.order_index}")
                
                # Check lesson progress
                progress = LessonProgress.query.filter_by(
                    user_id=enrollment.user_id,
                    lesson_id=lesson.id
                ).first()
                
                if progress:
                    print(f"Completed: {progress.is_completed}")
                    print(f"Progress: {progress.completion_percentage}%")
                
                # Check exercises
                exercises = Exercise.query.filter_by(
                    lesson_id=lesson.id
                ).order_by(Exercise.order_index).all()
                
                print(f"Exercises in lesson: {len(exercises)}")
                
                if exercises:
                    for ex in exercises:
                        submission = ExerciseSubmission.query.filter_by(
                            user_id=enrollment.user_id,
                            exercise_id=ex.id,
                            status='passed'
                        ).first()
                        status = "✓ Passed" if submission else "○ Not completed"
                        print(f"  - {ex.title}: {status}")
        
        print(f"\n" + "=" * 60)
        print(f"✅ Test completed successfully!")
        
    else:
        print("❌ No enrollments found. Please enroll in a course first.")
