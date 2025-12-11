# migrate_phase2.py
"""Migration script to create Phase 2 tables from scratch."""

import sys
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app('development')

with app.app_context():
    print("Starting Phase 2 migration...")
    
    try:
        # Drop existing tables if they exist (fresh start)
        print("Dropping old tables if they exist...")
        db.session.execute(text("DROP TABLE IF EXISTS exercises"))
        db.session.execute(text("DROP TABLE IF EXISTS lessons"))
        db.session.commit()
        print("✓ Old tables dropped")
        
        # Create lessons table if it doesn't exist
        print("Creating lessons table...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tutorial_id INT NOT NULL,
                title VARCHAR(300) NOT NULL,
                slug VARCHAR(350) NOT NULL,
                description TEXT,
                content_type VARCHAR(20) NOT NULL DEFAULT 'text',
                content TEXT,
                video_url VARCHAR(500),
                video_duration_seconds INT,
                section_name VARCHAR(200),
                order_index INT NOT NULL DEFAULT 0,
                is_free_preview BOOLEAN DEFAULT FALSE,
                estimated_duration_minutes INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (tutorial_id) REFERENCES tutorials(id) ON DELETE CASCADE,
                INDEX idx_lessons_tutorial_id (tutorial_id),
                INDEX idx_lessons_order (tutorial_id, order_index)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        db.session.commit()
        print("✓ lessons table created/verified")
        
        # Create exercises table if it doesn't exist
        print("Creating exercises table...")
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tutorial_id INT NOT NULL,
                lesson_id INT,
                title VARCHAR(300) NOT NULL,
                slug VARCHAR(350) NOT NULL,
                description TEXT NOT NULL,
                exercise_type VARCHAR(20) NOT NULL,
                difficulty VARCHAR(20) NOT NULL DEFAULT 'easy',
                starter_code TEXT,
                solution_code TEXT,
                test_cases TEXT,
                hints TEXT,
                database_schema TEXT,
                sample_data TEXT,
                order_index INT NOT NULL DEFAULT 0,
                points INT DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (tutorial_id) REFERENCES tutorials(id) ON DELETE CASCADE,
                FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL,
                INDEX idx_exercises_tutorial_id (tutorial_id),
                INDEX idx_exercises_lesson_id (lesson_id),
                INDEX idx_exercises_type (exercise_type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))
        db.session.commit()
        print("✓ exercises table created/verified")
        
        print("\n" + "="*50)
        print("Phase 2 migration completed successfully!")
        print("="*50)
        print("\nNew features available:")
        print("  • course_type field (Python/SQL separation)")
        print("  • lessons table for course content")
        print("  • exercises table for practice problems")
        print("\nYou can now:")
        print("  1. Access admin dashboard: /admin/dashboard")
        print("  2. Create courses: /admin/courses/create")
        print("  3. Browse catalog: /catalog")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        db.session.rollback()
        sys.exit(1)
