"""Debug script to test the executor with assert_output."""

from app.python_practice.executor_enhanced import execute_python_code_enhanced
import json

# Test code
code = 'print("Hello, World!")'

# Test cases with assert_output
test_cases = [{
    'type': 'assert_output',
    'expected': 'Hello, World!',
    'description': 'Print Hello, World!',
    'case_sensitive': False,
    'strip_whitespace': True
}]

print("Testing code execution...")
print(f"Code: {code}")
print(f"Test cases: {json.dumps(test_cases, indent=2)}")
print("\n" + "="*60 + "\n")

# Execute
result = execute_python_code_enhanced(code, test_cases, timeout=30)

# Display results
print("RESULTS:")
print(json.dumps(result, indent=2))
print("\n" + "="*60 + "\n")

# Check specific fields
print(f"Status: {result['status']}")
print(f"Output: '{result['output']}'")
print(f"Error: '{result['error']}'")
print(f"Tests Passed: {result['tests_passed']}")
print(f"Tests Failed: {result['tests_failed']}")
print(f"\nTest Results:")
for test in result['test_results']:
    print(f"  Test {test['test_number']}: {test['description']}")
    print(f"    Passed: {test['passed']}")
    print(f"    Expected: {test['expected']}")
    print(f"    Actual: {test['actual']}")
    if test['error']:
        print(f"    Error: {test['error']}")
