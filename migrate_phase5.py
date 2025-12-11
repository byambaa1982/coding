# migrate_phase5.py
"""Database migration for Phase 5: Python Code Editor."""

from app import create_app
from app.extensions import db
from sqlalchemy import text

def run_migration():
    """Run Phase 5 database migration."""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("PHASE 5 DATABASE MIGRATION")
        print("=" * 60)
        
        try:
            # Check if exercise_submissions table exists
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'exercise_submissions' in existing_tables:
                print("\n⚠️  exercise_submissions table already exists")
                response = input("Do you want to recreate it? This will DELETE all data! (yes/no): ")
                
                if response.lower() == 'yes':
                    print("\nDropping existing table...")
                    db.session.execute(text('DROP TABLE IF EXISTS exercise_submissions'))
                    db.session.commit()
                    print("✓ Table dropped")
                else:
                    print("Migration cancelled")
                    return
            
            # Create exercise_submissions table
            print("\nCreating exercise_submissions table...")
            
            create_table_sql = """
            CREATE TABLE exercise_submissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                exercise_id INT NOT NULL,
                enrollment_id INT NULL,
                
                submitted_code TEXT NOT NULL,
                language VARCHAR(20) DEFAULT 'python',
                
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                output TEXT NULL,
                error_message TEXT NULL,
                test_results TEXT NULL,
                
                tests_passed INT DEFAULT 0,
                tests_failed INT DEFAULT 0,
                score DECIMAL(5, 2) DEFAULT 0.00,
                
                execution_time_ms INT NULL,
                memory_used_mb DECIMAL(10, 2) NULL,
                
                is_flagged BOOLEAN DEFAULT FALSE,
                flagged_reason VARCHAR(500) NULL,
                ip_address VARCHAR(50) NULL,
                
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                executed_at DATETIME NULL,
                
                INDEX idx_user_id (user_id),
                INDEX idx_exercise_id (exercise_id),
                INDEX idx_status (status),
                INDEX idx_submitted_at (submitted_at),
                
                FOREIGN KEY (user_id) REFERENCES tutorial_users(id) ON DELETE CASCADE,
                FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE,
                FOREIGN KEY (enrollment_id) REFERENCES tutorial_enrollments(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            db.session.execute(text(create_table_sql))
            db.session.commit()
            print("✓ exercise_submissions table created")
            
            # Verify table creation
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'exercise_submissions' in tables:
                print("\n✓ Migration successful!")
                
                # Display table info
                columns = inspector.get_columns('exercise_submissions')
                print(f"\nTable structure:")
                print(f"  Columns: {len(columns)}")
                for col in columns:
                    print(f"    - {col['name']}: {col['type']}")
                
                indexes = inspector.get_indexes('exercise_submissions')
                print(f"\n  Indexes: {len(indexes)}")
                for idx in indexes:
                    print(f"    - {idx['name']}: {', '.join(idx['column_names'])}")
            else:
                print("\n✗ Migration failed - table not found")
            
            print("\n" + "=" * 60)
            print("MIGRATION COMPLETE")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    run_migration()
