"""Test the updated parsing logic."""
from app import create_app
from app.models import Exercise
import json

app = create_app()
ctx = app.app_context()
ctx.push()

ex = Exercise.query.get(24)

# Parse test cases using the new logic
test_cases = []
if ex.test_cases:
    try:
        # First try parsing as JSON
        test_cases = json.loads(ex.test_cases)
        print("✓ Parsed as JSON")
    except json.JSONDecodeError:
        # If JSON parsing fails, try Python literal eval
        try:
            import ast
            test_cases = ast.literal_eval(ex.test_cases)
            print("✓ Parsed as Python literal")
        except (ValueError, SyntaxError):
            test_cases = []
            print("✗ Failed to parse")

print(f"\nNumber of test cases: {len(test_cases)}")
print("\nTest cases:")
for i, tc in enumerate(test_cases, 1):
    print(f"\nTest {i}:")
    for key, value in tc.items():
        print(f"  {key}: {value}")
