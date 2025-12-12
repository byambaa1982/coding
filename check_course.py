from app import create_app
from app.models import NewTutorial, Lesson

app = create_app()

with app.app_context():
    # Check if course exists
    tutorial = NewTutorial.query.filter_by(slug='python-beginner-fundamentals').first()
    
    if tutorial:
        print(f"✓ Tutorial found: {tutorial.title}")
        print(f"  ID: {tutorial.id}")
        print(f"  Status: {tutorial.status}")
        print(f"  Course Type: {tutorial.course_type}")
        print(f"  Slug: {tutorial.slug}")
        
        # Check lessons
        lessons = Lesson.query.filter_by(tutorial_id=tutorial.id).all()
        print(f"\n  Lessons: {len(lessons)}")
        for lesson in lessons[:5]:
            print(f"    - {lesson.title} (order: {lesson.order_index})")
    else:
        print("✗ Tutorial NOT FOUND")
        print("\nAvailable tutorials:")
        tutorials = NewTutorial.query.all()
        for t in tutorials[:5]:
            print(f"  - {t.slug} ({t.status})")
