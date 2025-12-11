# create_phase4_tables.py
"""Create Phase 4 tables for learning interface - lesson progress and quizzes."""

from app import create_app, db
from app.models import LessonProgress, Quiz, QuizQuestion, QuizAttempt, QuizAnswer

def create_phase4_tables():
    """Create tables for Phase 4 (Learning Interface)."""
    app = create_app()
    
    with app.app_context():
        print("Creating Phase 4 tables...")
        
        # Create tables
        db.create_all()
        
        print("✅ Phase 4 tables created successfully!")
        print("\nNew tables:")
        print("  - lesson_progress (progress tracking)")
        print("  - quizzes (quiz definitions)")
        print("  - quiz_questions (quiz questions)")
        print("  - quiz_attempts (user quiz attempts)")
        print("  - quiz_answers (user answers)")
        
        # Verify tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        phase4_tables = ['lesson_progress', 'quizzes', 'quiz_questions', 'quiz_attempts', 'quiz_answers']
        
        print("\n📊 Table verification:")
        for table in phase4_tables:
            if table in tables:
                print(f"  ✓ {table}")
            else:
                print(f"  ✗ {table} (missing)")

if __name__ == '__main__':
    create_phase4_tables()
