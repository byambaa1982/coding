# seed_mock_course_data.py
"""
Create mock course data for testing the Continue Learning feature.

Structure:
- 1 Course: Python Programming Fundamentals
- 3 Topics (Sections)
- 9 Subtopics (Lessons) - 3 per topic
- 27+ Exercises - At least 3 per subtopic
"""

from app import create_app
from app.models import NewTutorial, Lesson, Exercise, TutorialUser
from app.extensions import db
from datetime import datetime

app = create_app()

def create_mock_course_data():
    """Create comprehensive mock data for testing."""
    
    with app.app_context():
        print("🚀 Starting mock data creation...")
        
        # Get or create instructor (use first admin user)
        instructor = TutorialUser.query.filter_by(is_admin=True).first()
        if not instructor:
            instructor = TutorialUser.query.first()
        
        if not instructor:
            print("❌ No users found. Please create a user first.")
            return
        
        print(f"👤 Using instructor: {instructor.email} (ID: {instructor.id})")
        
        # Create Course
        print("\n📚 Creating Course...")
        course = NewTutorial(
            instructor_id=instructor.id,
            title="Python Programming Fundamentals",
            slug="python-fundamentals-complete",
            description="Complete Python programming course from basics to advanced concepts with hands-on exercises.",
            short_description="Master Python programming with structured lessons and exercises",
            difficulty_level="beginner",
            course_type="python",
            category="Programming",
            price=49.99,
            status="published",
            is_free=False,
            total_lessons=9,
            published_at=datetime.utcnow()
        )
        db.session.add(course)
        db.session.commit()
        print(f"✅ Course created: {course.title} (ID: {course.id})")
        
        # Topic 1: Python Basics
        print("\n📖 Topic 1: Python Basics")
        topic1_lessons = [
            {
                'title': 'Introduction to Python',
                'description': 'Learn what Python is, why it\'s popular, and set up your environment.',
                'section': 'Topic 1: Python Basics'
            },
            {
                'title': 'Variables and Data Types',
                'description': 'Understand variables, numbers, strings, and basic data types.',
                'section': 'Topic 1: Python Basics'
            },
            {
                'title': 'Basic Operations and Expressions',
                'description': 'Learn arithmetic, comparison, and logical operations.',
                'section': 'Topic 1: Python Basics'
            }
        ]
        
        topic1_order = 0
        for lesson_data in topic1_lessons:
            lesson = Lesson(
                tutorial_id=course.id,
                title=lesson_data['title'],
                slug=lesson_data['title'].lower().replace(' ', '-'),
                description=lesson_data['description'],
                content_type='text',
                section_name=lesson_data['section'],
                order_index=topic1_order,
                is_free_preview=(topic1_order == 0)
            )
            db.session.add(lesson)
            db.session.commit()
            print(f"  ✅ Subtopic {topic1_order + 1}: {lesson.title} (ID: {lesson.id})")
            
            # Create 3 exercises per lesson
            create_exercises_for_lesson(lesson, topic1_order)
            topic1_order += 1
        
        # Topic 2: Control Flow
        print("\n📖 Topic 2: Control Flow")
        topic2_lessons = [
            {
                'title': 'Conditional Statements (if/else)',
                'description': 'Learn to make decisions in your code with if, elif, and else.',
                'section': 'Topic 2: Control Flow'
            },
            {
                'title': 'Loops - While Loop',
                'description': 'Understand how to repeat code execution with while loops.',
                'section': 'Topic 2: Control Flow'
            },
            {
                'title': 'Loops - For Loop',
                'description': 'Master iteration with for loops and range function.',
                'section': 'Topic 2: Control Flow'
            }
        ]
        
        topic2_order = topic1_order
        for lesson_data in topic2_lessons:
            lesson = Lesson(
                tutorial_id=course.id,
                title=lesson_data['title'],
                slug=lesson_data['title'].lower().replace(' ', '-').replace('/', '-'),
                description=lesson_data['description'],
                content_type='text',
                section_name=lesson_data['section'],
                order_index=topic2_order,
                is_free_preview=False
            )
            db.session.add(lesson)
            db.session.commit()
            print(f"  ✅ Subtopic {topic2_order + 1}: {lesson.title} (ID: {lesson.id})")
            
            # Create 3 exercises per lesson
            create_exercises_for_lesson(lesson, topic2_order)
            topic2_order += 1
        
        # Topic 3: Functions and Data Structures
        print("\n📖 Topic 3: Functions and Data Structures")
        topic3_lessons = [
            {
                'title': 'Functions Basics',
                'description': 'Learn to define and call functions, pass arguments, and return values.',
                'section': 'Topic 3: Functions and Data Structures'
            },
            {
                'title': 'Lists and Tuples',
                'description': 'Work with ordered collections of data.',
                'section': 'Topic 3: Functions and Data Structures'
            },
            {
                'title': 'Dictionaries and Sets',
                'description': 'Master key-value pairs and unique collections.',
                'section': 'Topic 3: Functions and Data Structures'
            }
        ]
        
        topic3_order = topic2_order
        for lesson_data in topic3_lessons:
            lesson = Lesson(
                tutorial_id=course.id,
                title=lesson_data['title'],
                slug=lesson_data['title'].lower().replace(' ', '-'),
                description=lesson_data['description'],
                content_type='text',
                section_name=lesson_data['section'],
                order_index=topic3_order,
                is_free_preview=False
            )
            db.session.add(lesson)
            db.session.commit()
            print(f"  ✅ Subtopic {topic3_order + 1}: {lesson.title} (ID: {lesson.id})")
            
            # Create 3 exercises per lesson
            create_exercises_for_lesson(lesson, topic3_order)
            topic3_order += 1
        
        print(f"\n✨ Mock data creation complete!")
        print(f"📊 Summary:")
        print(f"   - Course: {course.title}")
        print(f"   - Topics: 3")
        print(f"   - Subtopics (Lessons): 9")
        print(f"   - Exercises: {topic3_order * 3} (3 per subtopic)")


def create_exercises_for_lesson(lesson, base_order):
    """Create 3 exercises for a given lesson."""
    
    exercises_data = [
        {
            'suffix': 'Part 1',
            'difficulty': 'easy',
            'points': 10,
            'description': 'Basic practice exercise focusing on fundamental concepts.',
            'starter_code': '# Write your solution here\n\ndef solution():\n    # Your code here\n    pass\n'
        },
        {
            'suffix': 'Part 2',
            'difficulty': 'medium',
            'points': 15,
            'description': 'Intermediate exercise that builds on the basics.',
            'starter_code': '# Write your solution here\n\ndef solution():\n    # Your code here\n    pass\n'
        },
        {
            'suffix': 'Part 3',
            'difficulty': 'medium',
            'points': 20,
            'description': 'Challenge exercise combining multiple concepts.',
            'starter_code': '# Write your solution here\n\ndef solution():\n    # Your code here\n    pass\n'
        }
    ]
    
    for idx, ex_data in enumerate(exercises_data):
        exercise = Exercise(
            tutorial_id=lesson.tutorial_id,
            lesson_id=lesson.id,
            title=f"{lesson.title} - {ex_data['suffix']}",
            slug=f"{lesson.slug}-exercise-{idx + 1}",
            description=f"<h4>Exercise: {lesson.title} - {ex_data['suffix']}</h4><p>{ex_data['description']}</p><p>Complete this exercise to practice the concepts from the lesson.</p>",
            exercise_type='python',
            difficulty=ex_data['difficulty'],
            starter_code=ex_data['starter_code'],
            solution_code='# Solution provided after attempts\ndef solution():\n    return "Correct!"\n',
            test_cases='[{"input": "", "expected": "Correct!", "description": "Basic test"}]',
            hints='["Read the lesson material carefully", "Break down the problem into smaller steps", "Test your code with different inputs"]',
            order_index=idx,
            points=ex_data['points']
        )
        db.session.add(exercise)
        db.session.commit()
        print(f"    ✓ Exercise {idx + 1}: {exercise.title} ({exercise.difficulty}, {exercise.points} pts)")


if __name__ == '__main__':
    print("=" * 60)
    print("MOCK COURSE DATA CREATOR")
    print("=" * 60)
    
    response = input("\n⚠️  This will create a new course with lessons and exercises.\nContinue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        create_mock_course_data()
    else:
        print("❌ Operation cancelled.")
