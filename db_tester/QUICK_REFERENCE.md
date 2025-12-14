# Quick Reference Guide

## Common Commands

### Test Single Course/Lesson
```bash
python db_tester/test_python_exercises.py
```

### Test Specific Exercise
```bash
python db_tester/test_validator.py <exercise_id>
```

### List Available Courses
```bash
python db_tester/batch_tester.py list
```

### Batch Test Specific Courses
```bash
python db_tester/batch_tester.py specific
```

### Batch Test All Courses
```bash
python db_tester/batch_tester.py all
```

### Interactive Menu (Windows)
```bash
db_tester\run_tests.bat
```

### Interactive Menu (Linux/Mac)
```bash
bash db_tester/run_tests.sh
```

### Run Examples
```bash
python db_tester/examples.py
```

---

## Configuration

Edit test targets in `test_python_exercises.py`:
```python
COURSE_ID = 5
LESSON_ID = 6
```

Edit batch test targets in `batch_tester.py`:
```python
course_lesson_pairs = [
    (5, 6),  # Course 5, Lesson 6
    (5, 7),  # Course 5, Lesson 7
]
```

---

## Programmatic Usage

### Test Single Course
```python
from db_tester import ExerciseTester

tester = ExerciseTester(course_id=5, lesson_id=6)
results, summary = tester.run_tests()
tester.print_summary(summary)
```

### Validate Code
```python
from db_tester import ExerciseValidator

validator = ExerciseValidator()
is_valid, errors = validator.validate_code_syntax(code)
```

### Generate HTML Report
```python
from db_tester import generate_html_report

generate_html_report(results, summary, 'report.html')
```

---

## Exit Codes

- `0`: All tests passed ✅
- `1`: Some tests failed or error occurred ❌

---

## File Locations

- **Test Scripts**: `db_tester/*.py`
- **Reports**: `db_tester/reports/`
- **Config**: `db_tester/test_config.py`
- **Examples**: `db_tester/examples.py`

---

## URL Format

Test exercises via web browser:
```
http://127.0.0.1:5000/python-practice/exercise/<exercise_id>?course_id=<course_id>&lesson_id=<lesson_id>
```

Example:
```
http://127.0.0.1:5000/python-practice/exercise/27?course_id=5&lesson_id=6
```

---

## Troubleshooting

### Module Not Found
Make sure you're in the project root:
```bash
cd c:\Users\byamb\projects\project_plan\code_tutorial
```

### Database Connection Error
Check if the Flask app can connect to the database:
```bash
python run_server.py
```

### Exercise Not Found
Verify exercise exists in database:
```sql
SELECT id, title FROM exercises WHERE id = <exercise_id>;
```

### Timeout Errors
Increase timeout in `test_config.py`:
```python
TEST_CONFIG = {
    'TIMEOUT_SECONDS': 60  # Increase from 30
}
```

---

## Best Practices

1. ✅ Run tests before deploying new exercises
2. ✅ Review all failed tests - they indicate content issues
3. ✅ Monitor execution times for performance regressions
4. ✅ Keep solution code updated when exercises change
5. ✅ Use descriptive test case descriptions

---

## Support

For issues, check:
1. README.md for detailed documentation
2. examples.py for usage examples
3. Test output and error messages
4. JSON reports for detailed error information
