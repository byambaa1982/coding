#!/usr/bin/env python
"""Test script to verify new nested URL routes are registered."""

import sys
sys.path.insert(0, '.')

from app import create_app

def test_routes():
    """Test the new nested URL structure."""
    app = create_app()
    
    print("Checking registered routes for python_practice blueprint...")
    print()
    
    python_routes = []
    for rule in app.url_map.iter_rules():
        if 'python_practice' in rule.endpoint:
            python_routes.append({
                'endpoint': rule.endpoint,
                'rule': str(rule),
                'methods': ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
            })
    
    # Sort by endpoint
    python_routes.sort(key=lambda x: x['endpoint'])
    
    print(f"Found {len(python_routes)} python_practice routes:")
    print()
    
    for route in python_routes:
        print(f"Endpoint: {route['endpoint']}")
        print(f"  URL: {route['rule']}")
        print(f"  Methods: {route['methods']}")
        print()
    
    # Check for the new nested routes
    print("Checking for new nested routes...")
    nested_routes = [r for r in python_routes if 'course_subtopics' in r['endpoint']]
    
    if nested_routes:
        print(f"✓ Found {len(nested_routes)} course_subtopics route(s)")
        for route in nested_routes:
            print(f"  - {route['rule']}")
    else:
        print("✗ No course_subtopics routes found!")
    
    print()
    print("Expected URLs:")
    print("  1. /python-practice/course/<int:course_id>/subtopics")
    print("  2. /python-practice/course/<int:course_id>/subtopics/<int:lesson_id>")
    print("  3. /python-practice/course/<int:course_id>/subtopics/<int:lesson_id>/exercise/<int:exercise_order>")

if __name__ == '__main__':
    test_routes()
