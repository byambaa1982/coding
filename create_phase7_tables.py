#!/usr/bin/env python3
"""
Phase 7: User Dashboard & Analytics - Database Table Creation

This script creates the tables for:
- Certificates
- Reviews
- Achievements
- User Achievements
- Notifications
- Learning Streaks
- User Analytics
"""

from app import create_app
from app.extensions import db
from app.models import (
    Certificate, Review, Achievement, UserAchievement,
    Notification, LearningStreak, UserAnalytics
)

def create_phase7_tables():
    """Create Phase 7 tables."""
    app = create_app()
    
    with app.app_context():
        print("Creating Phase 7 tables...")
        
        # Create tables
        Certificate.__table__.create(db.engine, checkfirst=True)
        print("✓ Created certificates table")
        
        Review.__table__.create(db.engine, checkfirst=True)
        print("✓ Created reviews table")
        
        Achievement.__table__.create(db.engine, checkfirst=True)
        print("✓ Created achievements table")
        
        UserAchievement.__table__.create(db.engine, checkfirst=True)
        print("✓ Created user_achievements table")
        
        Notification.__table__.create(db.engine, checkfirst=True)
        print("✓ Created notifications table")
        
        LearningStreak.__table__.create(db.engine, checkfirst=True)
        print("✓ Created learning_streaks table")
        
        UserAnalytics.__table__.create(db.engine, checkfirst=True)
        print("✓ Created user_analytics table")
        
        print("\n✅ Phase 7 tables created successfully!")
        print("\nNext steps:")
        print("1. Run: python seed_achievements.py")
        print("2. Test dashboard: http://localhost:5000/account/dashboard")
        print("3. Test analytics: http://localhost:5000/account/analytics")

if __name__ == '__main__':
    create_phase7_tables()
