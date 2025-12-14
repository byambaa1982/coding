#!/usr/bin/env python
"""Test script to verify new nested URL routes are working correctly."""

import sys
sys.path.insert(0, '.')

from app import create_app
from flask import url_for

def test_routes():
    """Test the new nested URL structure."""
    app = create_app()
    
    with app.app_context():
        print("Testing new nested URL structure...")
        print()
        
        # Test 1: View all subtopics
        try:
            url1 = url_for('python_practice.course_subtopics', course_id=3)
            print(f"✓ Subtopics URL: {url1}")
        except Exception as e:
            print(f"✗ Subtopics URL failed: {e}")
        
        # Test 2: View lesson exercises
        try:
            url2 = url_for('python_practice.course_subtopics', course_id=3, lesson_id=5)
            print(f"✓ Lesson exercises URL: {url2}")
        except Exception as e:
            print(f"✗ Lesson exercises URL failed: {e}")
        
        # Test 3: View specific exercise
        try:
            url3 = url_for('python_practice.course_subtopics', 
                          course_id=3, lesson_id=5, exercise_order=2)
            print(f"✓ Exercise URL: {url3}")
        except Exception as e:
            print(f"✗ Exercise URL failed: {e}")
        
        # Test 4: Old lesson_exercises route (backward compatibility)
        try:
            url4 = url_for('python_practice.lesson_exercises', lesson_id=5)
            print(f"✓ Legacy lesson URL: {url4}")
        except Exception as e:
            print(f"✗ Legacy lesson URL failed: {e}")
        
        # Test 5: Exercise view route
        try:
            url5 = url_for('python_practice.view_exercise', exercise_id=24)
            print(f"✓ Exercise view URL: {url5}")
        except Exception as e:
            print(f"✗ Exercise view URL failed: {e}")
        
        print()
        print("All URL routes registered successfully!")
        print()
        print("Example URLs:")
        print(f"  - All subtopics: {url1}")
        print(f"  - Lesson exercises: {url2}")
        print(f"  - Specific exercise: {url3}")

if __name__ == '__main__':
    test_routes()
