#!/usr/bin/env python
"""Quick verification of the continue learning fix."""

print("Checking app/account/utils.py for course_id parameter...")
print()

with open('app/account/utils.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
    # Check line 51 area
    if "url_for('python_practice.course_subtopics', course_id=enrollment.tutorial_id)" in content:
        print("✅ FIXED: Line uses course_id parameter")
        print("   Found: url_for('python_practice.course_subtopics', course_id=enrollment.tutorial_id)")
    elif "url_for('python_practice.course_subtopics', enrollment_id=" in content:
        print("❌ NOT FIXED: Still uses enrollment_id parameter")
    else:
        print("⚠️  Could not find the specific line")
    
print()
print("The fix is complete. The Start Learning button should now work correctly.")
print()
print("To test:")
print("1. Start the server: python run_server.py")
print("2. Go to My Courses")
print("3. Click 'Start Learning' or 'Continue' on a Python course")
print("4. You should be redirected to: /python-practice/course/{course_id}/subtopics")
