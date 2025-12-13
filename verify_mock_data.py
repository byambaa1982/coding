# verify_mock_data.py
"""Verify the mock course data structure."""

from app import create_app
from app.models import NewTutorial, Lesson, Exercise
from app.extensions import db

app = create_app()

def verify_mock_data():
    """Verify the structure of mock course data."""
    
    with app.app_context():
        print("=" * 80)
        print("MOCK DATA VERIFICATION")
        print("=" * 80)
        
        # Find the mock course
        course = NewTutorial.query.filter_by(slug='python-fundamentals-complete').first()
        
        if not course:
            print("❌ Mock course not found. Please run seed_mock_course_data.py first.")
            return
        
        print(f"\n📚 Course: {course.title}")
        print(f"   ID: {course.id}")
        print(f"   Type: {course.course_type}")
        print(f"   Difficulty: {course.difficulty_level}")
        print(f"   Status: {course.status}")
        
        # Get all lessons
        lessons = Lesson.query.filter_by(tutorial_id=course.id)\
            .order_by(Lesson.order_index).all()
        
        print(f"\n📖 Total Lessons: {len(lessons)}")
        
        # Group lessons by section (topic)
        topics = {}
        for lesson in lessons:
            section = lesson.section_name or "No Section"
            if section not in topics:
                topics[section] = []
            topics[section].append(lesson)
        
        print(f"📂 Total Topics: {len(topics)}")
        print("\n" + "=" * 80)
        
        total_exercises = 0
        
        for topic_idx, (topic_name, topic_lessons) in enumerate(topics.items(), 1):
            print(f"\n📖 {topic_name}")
            print(f"   Subtopics: {len(topic_lessons)}")
            
            for lesson_idx, lesson in enumerate(topic_lessons, 1):
                exercises = Exercise.query.filter_by(lesson_id=lesson.id)\
                    .order_by(Exercise.order_index).all()
                
                print(f"\n   📝 Subtopic {lesson_idx}: {lesson.title}")
                print(f"      Order Index: {lesson.order_index}")
                print(f"      Lesson ID: {lesson.id}")
                print(f"      Exercises: {len(exercises)}")
                
                for ex_idx, exercise in enumerate(exercises, 1):
                    total_exercises += 1
                    print(f"         {ex_idx}. {exercise.title}")
                    print(f"            - Difficulty: {exercise.difficulty}")
                    print(f"            - Points: {exercise.points}")
                    print(f"            - ID: {exercise.id}")
        
        print("\n" + "=" * 80)
        print(f"📊 SUMMARY")
        print("=" * 80)
        print(f"✅ Course: 1")
        print(f"✅ Topics: {len(topics)}")
        print(f"✅ Subtopics (Lessons): {len(lessons)}")
        print(f"✅ Total Exercises: {total_exercises}")
        print(f"✅ Avg Exercises per Subtopic: {total_exercises / len(lessons):.1f}")
        
        # Verify each subtopic has at least 3 exercises
        print("\n" + "=" * 80)
        print("🔍 VALIDATION: Each subtopic must have at least 3 exercises")
        print("=" * 80)
        
        all_valid = True
        for lesson in lessons:
            exercise_count = Exercise.query.filter_by(lesson_id=lesson.id).count()
            status = "✅" if exercise_count >= 3 else "❌"
            print(f"{status} {lesson.title}: {exercise_count} exercises")
            if exercise_count < 3:
                all_valid = False
        
        print("\n" + "=" * 80)
        if all_valid:
            print("✅ VALIDATION PASSED: All subtopics have at least 3 exercises!")
        else:
            print("❌ VALIDATION FAILED: Some subtopics have fewer than 3 exercises!")
        print("=" * 80)


if __name__ == '__main__':
    verify_mock_data()
