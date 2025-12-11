"""
Script to verify the ingested Lesson 1 data from the database.
"""

from app import create_app
from app.extensions import db
from app.models import TutorialUser, NewTutorial, Lesson


def verify_data():
    """Verify the ingested data."""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("🔍 Verifying Ingested Data")
        print("="*70 + "\n")
        
        # Check instructor
        instructor = TutorialUser.query.filter_by(email='instructor@test.com').first()
        if instructor:
            print("✅ INSTRUCTOR FOUND:")
            print(f"   ID: {instructor.id}")
            print(f"   Email: {instructor.email}")
            print(f"   Username: {instructor.username}")
            print(f"   Full Name: {instructor.full_name}")
            print(f"   Is Instructor: {instructor.is_instructor}")
            print(f"   Is Admin: {instructor.is_admin}")
        else:
            print("❌ Instructor not found!")
            return
        
        # Check tutorial
        print("\n" + "-"*70)
        tutorial = NewTutorial.query.filter_by(slug='python-programming-fundamentals').first()
        if tutorial:
            print("✅ TUTORIAL FOUND:")
            print(f"   ID: {tutorial.id}")
            print(f"   Title: {tutorial.title}")
            print(f"   Slug: {tutorial.slug}")
            print(f"   Course Type: {tutorial.course_type}")
            print(f"   Category: {tutorial.category}")
            print(f"   Difficulty: {tutorial.difficulty_level}")
            print(f"   Price: ${tutorial.price}")
            print(f"   Status: {tutorial.status}")
            print(f"   Is Featured: {tutorial.is_featured}")
            print(f"   Duration: {tutorial.estimated_duration_hours} hours")
            print(f"   Total Lessons: {tutorial.total_lessons}")
            print(f"   Short Description: {tutorial.short_description[:100]}...")
        else:
            print("❌ Tutorial not found!")
            return
        
        # Check lesson
        print("\n" + "-"*70)
        lesson = Lesson.query.filter_by(
            tutorial_id=tutorial.id,
            slug='welcome-to-python-programming'
        ).first()
        if lesson:
            print("✅ LESSON FOUND:")
            print(f"   ID: {lesson.id}")
            print(f"   Tutorial ID: {lesson.tutorial_id}")
            print(f"   Title: {lesson.title}")
            print(f"   Slug: {lesson.slug}")
            print(f"   Section: {lesson.section_name}")
            print(f"   Order: {lesson.order_index}")
            print(f"   Content Type: {lesson.content_type}")
            print(f"   Duration: {lesson.estimated_duration_minutes} minutes")
            print(f"   Free Preview: {lesson.is_free_preview}")
            print(f"   Description: {lesson.description}")
            print(f"   Content Length: {len(lesson.content)} characters")
            print(f"\n   Content Preview (first 300 chars):")
            print(f"   {lesson.content[:300]}...")
        else:
            print("❌ Lesson not found!")
            return
        
        # Summary
        print("\n" + "="*70)
        print("📊 INGESTION SUMMARY")
        print("="*70)
        print(f"✅ 1 Instructor created")
        print(f"✅ 1 Tutorial created (Python Beginner)")
        print(f"✅ 1 Lesson created (Lesson 1: Welcome to Python Programming)")
        print(f"\n🎯 Next Steps:")
        print(f"   1. Access the lesson in the UI at:")
        print(f"      /catalog/course/{tutorial.slug}")
        print(f"   2. Create routes to display the tutorial and lesson")
        print(f"   3. Ingest remaining lessons (2-10)")
        print(f"   4. Add interactive exercises")
        print("="*70 + "\n")


if __name__ == '__main__':
    verify_data()
