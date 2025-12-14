# Exercise QA Testing Suite

Professional testing framework for validating Python exercises in the Flask application.

## Overview

This testing suite validates that all Python exercises have correct solution code that passes all defined test cases. It's designed for QA testing to ensure content quality before deployment.

## Features

- ✅ **Automated Validation**: Tests all exercises in a course/lesson automatically
- 📊 **Detailed Reporting**: Generates JSON and HTML reports
- 🔒 **Security Checks**: Validates code for security issues
- ⚡ **Performance Metrics**: Tracks execution time for each test
- 🎯 **Test Case Analysis**: Detailed breakdown of each test case result
- 📈 **Summary Statistics**: Overall pass/fail rates and metrics

## Directory Structure

```
db_tester/
├── test_python_exercises.py   # Main test runner
├── test_validator.py           # Enhanced validation logic
├── test_config.py              # Configuration and utilities
├── html_report.py              # HTML report generator
├── README.md                   # This file
└── reports/                    # Generated test reports
```

## Installation

No additional dependencies required beyond the main Flask application.

## Usage

### Test All Exercises in a Course/Lesson

```bash
python db_tester/test_python_exercises.py
```

This will test all Python exercises for **course_id=5, lesson_id=6** by default.

### Test a Single Exercise

```bash
python db_tester/test_validator.py <exercise_id>
```

Example:
```bash
python db_tester/test_validator.py 27
```

### Customize Test Configuration

Edit `test_python_exercises.py` and modify:

```python
# Configuration
COURSE_ID = 5
LESSON_ID = 6
```

## What Gets Tested

For each exercise, the test suite validates:

1. **Solution Code Exists**: Checks if exercise has solution_code
2. **Test Cases Exist**: Verifies test_cases are defined
3. **Code Syntax**: Validates Python syntax is correct
4. **Security**: Checks for banned imports and dangerous patterns
5. **Test Execution**: Runs solution against all test cases
6. **Expected Output**: Verifies actual output matches expected results
7. **Performance**: Tracks execution time

## Test Output

### Console Output

```
================================================================================
QA Testing Python Exercises
================================================================================
Course: Python Programming Basics (ID: 5)
Lesson: Variables and Data Types (ID: 6)
================================================================================

Found 10 Python exercise(s) to test

[1/10] Testing: Hello World Exercise
    Exercise ID: 27
    Difficulty: easy
    ✅ PASSED - 3/3 tests passed
    Execution time: 125ms

[2/10] Testing: Variable Assignment
    Exercise ID: 28
    Difficulty: easy
    ❌ FAILED - 2/3 tests passed
       Error: Test case 3 failed - expected 'Hello' but got 'hello'
    Execution time: 98ms

...

================================================================================
TEST SUMMARY
================================================================================
Course: Python Programming Basics (ID: 5)
Lesson: Variables and Data Types (ID: 6)
Test Date: 2025-12-14T10:30:00.000000
--------------------------------------------------------------------------------
Total Exercises: 10
✅ Passed: 8
❌ Failed: 2
Success Rate: 80.0%
--------------------------------------------------------------------------------
Total Test Cases: 35
Tests Passed: 32
Tests Failed: 3
--------------------------------------------------------------------------------
Total Execution Time: 1250ms
Avg Execution Time: 125.0ms per exercise
================================================================================

📄 Detailed report saved to: db_tester/test_report_course5_lesson6_20251214_103000.json
```

### JSON Report

Saved to `db_tester/test_report_course<id>_lesson<id>_<timestamp>.json`

```json
{
  "summary": {
    "course_id": 5,
    "course_title": "Python Programming Basics",
    "lesson_id": 6,
    "lesson_title": "Variables and Data Types",
    "test_date": "2025-12-14T10:30:00.000000",
    "total_exercises": 10,
    "passed_exercises": 8,
    "failed_exercises": 2,
    "success_rate": 80.0,
    "total_test_cases": 35,
    "total_tests_passed": 32,
    "total_tests_failed": 3
  },
  "detailed_results": [
    {
      "exercise_id": 27,
      "exercise_title": "Hello World Exercise",
      "validation_passed": true,
      "tests_passed": 3,
      "tests_failed": 0,
      "total_tests": 3,
      "execution_time_ms": 125,
      "test_details": [...]
    }
  ]
}
```

### HTML Report

Visual HTML report with:
- Summary statistics dashboard
- Color-coded pass/fail indicators
- Expandable test case details
- Progress bars
- Error highlighting

## Test Configuration

Edit `test_config.py` to customize:

```python
TEST_CONFIG = {
    'COURSE_ID': 5,
    'LESSON_ID': 6,
    'TIMEOUT_SECONDS': 30,
    'MAX_RETRIES': 3,
    'SAVE_REPORTS': True,
    'REPORT_FORMAT': 'json',  # 'json' or 'html'
    'VERBOSE': True
}
```

## Exit Codes

- `0`: All tests passed ✅
- `1`: Some tests failed or error occurred ❌

Use in CI/CD pipelines:

```bash
python db_tester/test_python_exercises.py
if [ $? -eq 0 ]; then
    echo "All exercises validated successfully"
else
    echo "Exercise validation failed"
    exit 1
fi
```

## API Reference

### ExerciseTester Class

```python
from db_tester.test_python_exercises import ExerciseTester

# Create tester
tester = ExerciseTester(course_id=5, lesson_id=6)

# Run tests
results, summary = tester.run_tests()

# Print summary
tester.print_summary(summary)

# Save report
tester.save_report(results, summary)
```

### ExerciseValidator Class

```python
from db_tester.test_validator import ExerciseValidator

# Create validator
validator = ExerciseValidator(timeout=30)

# Validate single exercise
result = validator.validate_exercise_complete(exercise)

# Validate code syntax
is_valid, errors = validator.validate_code_syntax(code)

# Validate test cases
is_valid, test_cases, errors = validator.validate_test_cases(test_cases_json)
```

## Common Issues

### Issue: "Exercise not found"

**Solution**: Verify the course_id and lesson_id exist in the database.

```sql
SELECT id, title FROM lessons WHERE tutorial_id = 5;
```

### Issue: "Timeout errors"

**Solution**: Increase timeout in test_config.py:

```python
TEST_CONFIG = {
    'TIMEOUT_SECONDS': 60  # Increase from 30
}
```

### Issue: "Module import errors"

**Solution**: Ensure you're running from the project root:

```bash
cd c:\Users\byamb\projects\project_plan\code_tutorial
python db_tester/test_python_exercises.py
```

## Best Practices

1. **Test Before Deployment**: Run tests before deploying new exercises
2. **Review Failed Tests**: Investigate all failures - they indicate content issues
3. **Monitor Performance**: Watch execution times for performance regressions
4. **Keep Solutions Updated**: Ensure solution_code is always correct
5. **Use Descriptive Test Cases**: Add clear descriptions to test cases

## Testing Checklist

Before marking exercises as production-ready:

- [ ] All exercises have solution_code
- [ ] All exercises have test_cases
- [ ] All test cases have descriptions
- [ ] Solution code passes all test cases
- [ ] Execution time is reasonable (<5 seconds)
- [ ] No security violations detected
- [ ] Expected output matches actual output
- [ ] Edge cases are covered in test cases

## Development

### Adding New Test Features

1. Edit `test_validator.py` to add validation logic
2. Update `test_python_exercises.py` to integrate new checks
3. Modify `html_report.py` to display new metrics
4. Update this README with documentation

### Running Tests in Development

```bash
# Test specific exercise
python db_tester/test_validator.py 27

# Test all exercises with verbose output
python db_tester/test_python_exercises.py

# Generate HTML report
# (modify test_python_exercises.py to use html_report.generate_html_report())
```

## Support

For issues or questions:
1. Check the Common Issues section above
2. Review the test output and error messages
3. Inspect the JSON report for detailed error information
4. Check exercise configuration in the database

## License

Internal QA tool - All rights reserved

---

**Version**: 1.0.0  
**Last Updated**: December 14, 2025  
**Author**: QA Testing Team
