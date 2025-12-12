"""Add lesson_id column to quizzes table."""

from app import create_app
from app.extensions import db
from sqlalchemy import text

def add_quiz_lesson_column():
    """Add lesson_id column to quizzes table."""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Adding lesson_id column to quizzes table")
        print("=" * 60)
        
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'quizzes' 
                AND COLUMN_NAME = 'lesson_id'
            """))
            
            if result.fetchone():
                print("\n✓ lesson_id column already exists")
                return
            
            # Add lesson_id column
            print("\nAdding lesson_id column...")
            db.session.execute(text("""
                ALTER TABLE quizzes 
                ADD COLUMN lesson_id INT NULL 
                AFTER id
            """))
            
            # Add foreign key constraint
            print("Adding foreign key constraint...")
            db.session.execute(text("""
                ALTER TABLE quizzes 
                ADD CONSTRAINT fk_quizzes_lesson 
                FOREIGN KEY (lesson_id) REFERENCES lessons(id) 
                ON DELETE CASCADE
            """))
            
            db.session.commit()
            print("✓ lesson_id column added successfully")
            
            print("\n" + "=" * 60)
            print("Migration completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error: {str(e)}")
            raise

if __name__ == '__main__':
    add_quiz_lesson_column()
