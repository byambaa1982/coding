"""Quick test script for instructor panel functionality."""
from app import create_app
from app.models import TutorialUser, NewTutorial, Lesson, Exercise, db


def test_instructor_panel():
    """Test instructor panel setup."""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("INSTRUCTOR PANEL - QUICK TEST")
        print("=" * 80)
        
        # Check if we have any instructors
        instructors = TutorialUser.query.filter_by(is_instructor=True).all()
        print(f"\n📊 Instructors: {len(instructors)}")
        
        if instructors:
            for instructor in instructors:
                courses = NewTutorial.query.filter_by(instructor_id=instructor.id).all()
                print(f"\n👤 {instructor.email}")
                print(f"   - Username: {instructor.username}")
                print(f"   - Courses: {len(courses)}")
                
                for course in courses:
                    lessons = Lesson.query.filter_by(tutorial_id=course.id).count()
                    exercises = Exercise.query.filter_by(tutorial_id=course.id).count()
                    print(f"      • {course.title}")
                    print(f"        Status: {course.status}")
                    print(f"        Lessons: {lessons}, Exercises: {exercises}")
        else:
            print("\n⚠️  No instructors found!")
            print("\n💡 To create an instructor, run:")
            print("   python manage_instructors.py add <email>")
        
        # Check routes
        print("\n" + "=" * 80)
        print("AVAILABLE ROUTES")
        print("=" * 80)
        
        instructor_routes = [
            rule for rule in app.url_map.iter_rules() 
            if 'instructor' in rule.endpoint
        ]
        
        print(f"\n✅ {len(instructor_routes)} instructor routes registered:\n")
        for route in sorted(instructor_routes, key=lambda r: r.rule):
            methods = ', '.join([m for m in route.methods if m not in ['HEAD', 'OPTIONS']])
            print(f"   {route.rule:50s} [{methods}]")
        
        # Blueprint check
        print("\n" + "=" * 80)
        print("BLUEPRINT STATUS")
        print("=" * 80)
        
        blueprints = list(app.blueprints.keys())
        print(f"\n✅ Registered Blueprints: {', '.join(blueprints)}")
        
        if 'instructor' in blueprints:
            print("\n✅ Instructor blueprint is registered!")
        else:
            print("\n❌ Instructor blueprint NOT registered!")
        
        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("""
1. Make a user an instructor:
   python manage_instructors.py add <email>

2. Start the server:
   python run_server.py

3. Navigate to:
   http://localhost:5000/instructor

4. Login and start creating courses!
        """)
        
        print("=" * 80)


if __name__ == '__main__':
    test_instructor_panel()
