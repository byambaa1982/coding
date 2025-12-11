#!/usr/bin/env python
"""
Standalone script to make an existing user an admin.

Usage:
    python make_admin.py <email_or_username>

Example:
    python make_admin.py user@example.com
    python make_admin.py johndoe
"""

import sys
import os
from flask import Flask
from app.extensions import db
from app.models import TutorialUser
from config import Config


def create_app():
    """Create minimal Flask app for database operations."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Set up database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_database_uri()
    
    # Initialize extensions
    db.init_app(app)
    
    return app


def make_admin(identifier):
    """
    Make a user an admin by email or username.
    
    Args:
        identifier (str): Email or username of the user
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Try to find user by email first, then by username
    user = TutorialUser.query.filter_by(email=identifier).first()
    if not user:
        user = TutorialUser.query.filter_by(username=identifier).first()
    
    if not user:
        print(f"❌ Error: No user found with email or username '{identifier}'")
        return False
    
    if user.is_admin:
        print(f"ℹ️  User '{user.email}' is already an admin")
        return True
    
    # Make user an admin
    user.is_admin = True
    db.session.commit()
    
    print(f"✅ Success! User '{user.email}' is now an admin")
    print(f"   - ID: {user.id}")
    print(f"   - Username: {user.username or 'N/A'}")
    print(f"   - Email: {user.email}")
    print(f"   - Admin: {user.is_admin}")
    print(f"   - Instructor: {user.is_instructor}")
    
    return True


def list_users():
    """List all users in the system."""
    users = TutorialUser.query.order_by(TutorialUser.created_at.desc()).all()
    
    if not users:
        print("No users found in the database")
        return
    
    print(f"\n{'ID':<6} {'Email':<30} {'Username':<20} {'Admin':<7} {'Active':<7}")
    print("-" * 80)
    
    for user in users:
        print(f"{user.id:<6} {user.email:<30} {(user.username or 'N/A'):<20} "
              f"{'Yes' if user.is_admin else 'No':<7} {'Yes' if user.is_active else 'No':<7}")
    
    print(f"\nTotal users: {len(users)}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <email_or_username>")
        print("       python make_admin.py --list  (to list all users)")
        print("\nExample:")
        print("  python make_admin.py user@example.com")
        print("  python make_admin.py johndoe")
        sys.exit(1)
    
    # Create app and push context
    app = create_app()
    
    with app.app_context():
        if sys.argv[1] == '--list':
            list_users()
        else:
            identifier = sys.argv[1]
            success = make_admin(identifier)
            sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
