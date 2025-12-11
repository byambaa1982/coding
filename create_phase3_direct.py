"""
Direct database table creation for Phase 3
Run this with: python create_phase3_direct.py
"""

from app import create_app
from app.extensions import db
from app.models import (
    TutorialUser, NewTutorial, Lesson, Exercise, PasswordReset,
    TutorialEnrollment, TutorialOrder, TutorialOrderItem, Coupon, Wishlist
)

def create_tables():
    """Create all Phase 3 tables directly."""
    app = create_app('development')
    
    with app.app_context():
        print("Creating database tables...")
        
        # Create all tables defined in models
        db.create_all()
        
        print("✅ All tables created successfully!")
        print("\nNew Phase 3 tables:")
        print("  - tutorial_enrollments")
        print("  - tutorial_orders")
        print("  - tutorial_order_items")
        print("  - tutorial_coupons")
        print("  - tutorial_wishlists")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"\nTotal tables in database: {len(tables)}")
        print("\nPhase 3 tables verification:")
        phase3_tables = [
            'tutorial_enrollments',
            'tutorial_orders', 
            'tutorial_order_items',
            'tutorial_coupons',
            'tutorial_wishlists'
        ]
        
        for table in phase3_tables:
            if table in tables:
                print(f"  ✓ {table}")
            else:
                print(f"  ✗ {table} - NOT FOUND")

if __name__ == '__main__':
    create_tables()
