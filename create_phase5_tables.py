# create_phase5_tables.py
"""Create tables for Phase 5: Python Code Editor."""

from app import create_app
from app.extensions import db
from app.models import ExerciseSubmission

def create_phase5_tables():
    """Create Exercise Submission table for Phase 5."""
    app = create_app()
    
    with app.app_context():
        print("Creating Phase 5 tables...")
        
        try:
            # Create ExerciseSubmission table
            db.create_all()
            print("✓ Tables created successfully!")
            
            # Verify table creation
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'exercise_submissions' in tables:
                print("✓ exercise_submissions table created")
            else:
                print("✗ exercise_submissions table not found")
            
            print("\nPhase 5 database setup complete!")
            
        except Exception as e:
            print(f"✗ Error creating tables: {str(e)}")
            raise

if __name__ == '__main__':
    create_phase5_tables()
