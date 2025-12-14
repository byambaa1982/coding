"""Script to toggle instructor status for a user."""
import sys
from app import create_app
from app.models import TutorialUser, db


def make_instructor(email):
    """Grant instructor privileges to a user by email."""
    app = create_app()
    
    with app.app_context():
        user = TutorialUser.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ Error: User with email '{email}' not found.")
            return False
        
        if user.is_instructor:
            print(f"✓ User '{user.email}' is already an instructor.")
            return True
        
        user.is_instructor = True
        db.session.commit()
        
        print(f"✅ Success! User '{user.email}' is now an instructor.")
        print(f"   - Username: {user.username}")
        print(f"   - Full Name: {user.full_name or 'Not set'}")
        print(f"   - Instructor: Yes")
        print(f"   - Admin: {'Yes' if user.is_admin else 'No'}")
        
        return True


def remove_instructor(email):
    """Remove instructor privileges from a user by email."""
    app = create_app()
    
    with app.app_context():
        user = TutorialUser.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ Error: User with email '{email}' not found.")
            return False
        
        if not user.is_instructor:
            print(f"✓ User '{user.email}' is not an instructor.")
            return True
        
        user.is_instructor = False
        db.session.commit()
        
        print(f"✅ Success! Instructor privileges removed from '{user.email}'.")
        
        return True


def list_instructors():
    """List all instructors."""
    app = create_app()
    
    with app.app_context():
        instructors = TutorialUser.query.filter_by(is_instructor=True).all()
        
        if not instructors:
            print("No instructors found.")
            return
        
        print(f"\n📚 Instructors ({len(instructors)}):")
        print("-" * 80)
        
        for instructor in instructors:
            courses_count = len(instructor.tutorials_created)
            print(f"  • {instructor.email}")
            print(f"    Name: {instructor.full_name or 'Not set'}")
            print(f"    Username: {instructor.username}")
            print(f"    Courses: {courses_count}")
            print(f"    Admin: {'Yes' if instructor.is_admin else 'No'}")
            print()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python make_instructor.py add <email>       - Make user an instructor")
        print("  python make_instructor.py remove <email>    - Remove instructor status")
        print("  python make_instructor.py list              - List all instructors")
        print("\nExample:")
        print("  python make_instructor.py add instructor@example.com")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'add':
        if len(sys.argv) < 3:
            print("❌ Error: Email address required.")
            print("Usage: python make_instructor.py add <email>")
            sys.exit(1)
        
        email = sys.argv[2]
        make_instructor(email)
    
    elif command == 'remove':
        if len(sys.argv) < 3:
            print("❌ Error: Email address required.")
            print("Usage: python make_instructor.py remove <email>")
            sys.exit(1)
        
        email = sys.argv[2]
        remove_instructor(email)
    
    elif command == 'list':
        list_instructors()
    
    else:
        print(f"❌ Error: Unknown command '{command}'")
        print("Available commands: add, remove, list")
        sys.exit(1)
