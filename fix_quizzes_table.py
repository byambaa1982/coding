"""Check and fix quizzes table structure."""

from app import create_app
from app.extensions import db
from sqlalchemy import text

def check_and_fix_quizzes_table():
    """Check quizzes table structure and fix if needed."""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Checking quizzes table structure")
        print("=" * 60)
        
        try:
            # Check what columns exist
            result = db.session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'quizzes'
                ORDER BY ORDINAL_POSITION
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            print(f"\nExisting columns in quizzes table:")
            for col in existing_columns:
                print(f"  - {col}")
            
            required_columns = {
                'title': 'VARCHAR(300) NOT NULL',
                'description': 'TEXT NULL',
                'passing_score': 'DECIMAL(5,2) DEFAULT 70.00',
                'time_limit_minutes': 'INT NULL',
                'max_attempts': 'INT DEFAULT 3',
                'shuffle_questions': 'BOOLEAN DEFAULT TRUE',
                'shuffle_options': 'BOOLEAN DEFAULT TRUE',
                'show_correct_answers': 'BOOLEAN DEFAULT TRUE',
                'order_index': 'INT DEFAULT 0',
                'is_required': 'BOOLEAN DEFAULT FALSE',
                'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'
            }
            
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            if missing_columns:
                print(f"\nMissing columns: {', '.join(missing_columns)}")
                print("\nAdding missing columns...")
                
                for col_name, col_def in required_columns.items():
                    if col_name not in existing_columns:
                        print(f"  Adding {col_name}...")
                        db.session.execute(text(f"""
                            ALTER TABLE quizzes 
                            ADD COLUMN {col_name} {col_def}
                        """))
                
                db.session.commit()
                print("\n✓ All missing columns added successfully")
            else:
                print("\n✓ All required columns exist")
            
            print("\n" + "=" * 60)
            print("Table check completed!")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error: {str(e)}")
            raise

if __name__ == '__main__':
    check_and_fix_quizzes_table()
