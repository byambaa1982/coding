"""
Database Migration for Phase 6 - SQL Practice Environment
Adds expected_output column to exercises table
"""

from app import create_app
from app.extensions import db
from sqlalchemy import text

def run_migration():
    """Run Phase 6 database migration"""
    
    app = create_app()
    
    with app.app_context():
        print("Starting Phase 6 migration...")
        
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'exercises' 
                AND COLUMN_NAME = 'expected_output'
            """))
            
            if result.fetchone():
                print("✓ expected_output column already exists")
            else:
                # Add expected_output column
                db.session.execute(text("""
                    ALTER TABLE exercises 
                    ADD COLUMN expected_output TEXT NULL
                    COMMENT 'JSON for expected results (SQL exercises)'
                """))
                print("✓ Added expected_output column to exercises table")
            
            db.session.commit()
            print("\n✅ Phase 6 migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            raise


if __name__ == '__main__':
    run_migration()
