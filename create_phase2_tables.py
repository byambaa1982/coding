"""Create Phase 2 database tables."""

from app import create_app
from app.extensions import db
from app.models import NewTutorial, Lesson, Exercise, TutorialUser

# Create app instance
app = create_app()

with app.app_context():
    print("Creating Phase 2 tables...")
    
    # Create all tables
    db.create_all()
    
    print("✅ Tables created successfully!")
    print("\nNew tables:")
    print("  - new_tutorials (for Phase 2 courses)")
    print("  - lessons (for course lessons)")
    print("  - exercises (for practice exercises)")
    
    # Show existing tutorials
    tutorial_count = NewTutorial.query.count()
    print(f"\nCurrent tutorials in database: {tutorial_count}")
    
    if tutorial_count == 0:
        print("\nℹ️  No tutorials yet. Use the admin panel to create courses:")
        print("   http://localhost:5000/admin/dashboard")
    
    print("\n✨ Phase 2 database setup complete!")
