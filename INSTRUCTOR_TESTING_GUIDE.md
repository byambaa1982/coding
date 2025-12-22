# Instructor Testing Guide

## Overview

This guide shows instructors how to test Python exercises **without running the web application**. The new testing tools provide:

✅ **Standalone testing** - Test code from command line  
✅ **Detailed logging** - See exactly what's happening  
✅ **Execution replay** - Re-run past executions  
✅ **Debug mode** - Verbose output for troubleshooting  
✅ **File preservation** - Keep temp files for inspection  

---

## Quick Start

### 1. Simple Test (Command Line)

```bash
# Test a solution with test cases
python instructor_test_tool.py my_solution.py test_cases.json
```

### 2. Interactive Mode

```bash
# Launch interactive testing interface
python instructor_test_tool.py --interactive
```

### 3. Create Example Files

```bash
# Generate example code and test files
python instructor_test_tool.py --example
```

---

## Tools Available

### 1. `instructor_test_tool.py` (Recommended for Instructors)

**Simple CLI for testing exercises**

```bash
# Basic usage
python instructor_test_tool.py solution.py tests.json

# Interactive mode (guided)
python instructor_test_tool.py --interactive

# Create example
python instructor_test_tool.py --example

# Quiet mode (less output)
python instructor_test_tool.py solution.py tests.json --quiet
```

**Features:**
- ✅ Easy to use, no coding required
- ✅ Color-coded output (✅ pass, ❌ fail)
- ✅ Saves full execution logs
- ✅ Interactive mode with menu

---

### 2. `debug_executor.py` (For Advanced Users)

**Programmatic testing with detailed logging**

```python
from app.python_practice.debug_executor import DebugExecutor

# Create executor
executor = DebugExecutor(
    debug_mode=True,
    preserve_temp_files=True,  # Keep temp files
    verbose=True               # Print to console
)

# Execute code
result = executor.execute(code, test_cases, timeout=30)

# Check results
print(f"Status: {result['status']}")
print(f"Passed: {result['tests_passed']}/{len(test_cases)}")

# Replay an execution
result = executor.replay_execution('exec_1_1234567890')
```

**Features:**
- ✅ Full logging to file
- ✅ Saves code, tests, and results
- ✅ Replay functionality
- ✅ Programmatic control

---

## Test Case Format

Test cases are JSON files with this structure:

```json
[
  {
    "type": "assert_function",
    "description": "Test greeting with name",
    "function_name": "greet",
    "input": ["Alice"],
    "expected": "Hello, Alice!"
  },
  {
    "type": "assert_output",
    "description": "Test print output",
    "expected_output": "Welcome!\n"
  }
]
```

### Supported Test Types

| Type | Purpose | Example |
|------|---------|---------|
| `assert_function` | Test function return value | Check `add(2,3)` returns `5` |
| `assert_output` | Test printed output | Check program prints "Hello" |
| `assert_output_contains` | Check output contains text | Check output has "Success" |
| `assert_variable_exists` | Check variable is defined | Check `result` exists |
| `assert_variable_value` | Test variable value | Check `x == 10` |
| `assert_custom` | Custom Python assertion | Custom validation |

---

## Common Workflows

### Testing Student Submission

```bash
# 1. Save student code to file
echo 'def solution(): return 42' > student_code.py

# 2. Create test cases file
cat > tests.json << EOF
[
  {
    "type": "assert_function",
    "description": "Test solution",
    "function_name": "solution",
    "input": [],
    "expected": 42
  }
]
EOF

# 3. Run test
python instructor_test_tool.py student_code.py tests.json
```

### Debugging Failed Submission

```bash
# 1. Test with verbose output
python instructor_test_tool.py code.py tests.json

# 2. Check saved execution
cd debug_logs/exec_*_*/
cat summary.txt
cat code.py
cat result.json

# 3. Re-run if needed
python instructor_test_tool.py --interactive
# Choose option 5 (replay execution)
```

### Creating New Exercise

```bash
# 1. Create example
python instructor_test_tool.py --example

# 2. Edit example_code.py with your solution

# 3. Edit example_tests.json with test cases

# 4. Test it
python instructor_test_tool.py example_code.py example_tests.json

# 5. If all tests pass, use these in the web app
```

---

## Debug Logs Location

All executions are saved to `debug_logs/`:

```
debug_logs/
├── exec_1_1703280000/
│   ├── code.py          # Executed code
│   ├── test_cases.json  # Test cases
│   ├── result.json      # Full results
│   └── summary.txt      # Human-readable summary
├── exec_2_1703280100/
│   └── ...
└── executor_20231222_150000.log  # Main log file
```

---

## Advanced Features

### 1. Preserve Temp Files

```python
from app.python_practice.debug_executor import execute_with_debug

result = execute_with_debug(
    code=my_code,
    test_cases=my_tests,
    preserve_files=True,  # Keep temp files
    verbose=True
)

# Temp file location is in result['debug_info']
```

### 2. Custom Logging

```python
from app.python_practice.debug_executor import DebugExecutor

executor = DebugExecutor(
    debug_mode=True,
    log_dir='./my_custom_logs',  # Custom log directory
    verbose=False                 # No console output
)

result = executor.execute(code, tests)
```

### 3. List All Saved Executions

```python
executor = DebugExecutor()
executions = executor.list_executions()

for exec_id in executions:
    print(f"Execution: {exec_id}")
```

---

## Integration with Existing System

The new debug tools **do not break** existing code. They work alongside the current executor:

### Current Flow (Unchanged)
```python
# In app/python_practice/routes.py
from app.python_practice.executor import execute_python_code

result = execute_python_code(code, test_cases)  # Still works!
```

### New Debug Flow (Optional)
```python
# For testing/debugging
from app.python_practice.debug_executor import execute_with_debug

result = execute_with_debug(code, test_cases, verbose=True)
```

**No changes required to existing files!**

---

## Troubleshooting

### Issue: Can't find module

```bash
# Make sure you're in the project root
cd /path/to/code_tutorial

# Install dependencies
pip install -r requirements.txt
```

### Issue: Permission denied

```bash
# On Unix/Mac, make tool executable
chmod +x instructor_test_tool.py

# Or run with python explicitly
python instructor_test_tool.py ...
```

### Issue: Test cases not loading

```json
// Make sure JSON is valid
// Use https://jsonlint.com/ to validate

// Common mistake: trailing comma
[
  {"test": 1},
  {"test": 2},  // ← Remove this comma!
]
```

---

## Examples

### Example 1: Test Simple Function

**code.py:**
```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
```

**tests.json:**
```json
[
  {
    "type": "assert_function",
    "description": "Factorial of 0",
    "function_name": "factorial",
    "input": [0],
    "expected": 1
  },
  {
    "type": "assert_function",
    "description": "Factorial of 5",
    "function_name": "factorial",
    "input": [5],
    "expected": 120
  }
]
```

**Run:**
```bash
python instructor_test_tool.py code.py tests.json
```

### Example 2: Test Output

**code.py:**
```python
print("Hello, World!")
print("Python is awesome!")
```

**tests.json:**
```json
[
  {
    "type": "assert_output_contains",
    "description": "Check for greeting",
    "expected_text": "Hello, World!"
  },
  {
    "type": "assert_output_contains",
    "description": "Check for Python",
    "expected_text": "Python"
  }
]
```

---

## Tips for Instructors

1. **Start with --example** - Get familiar with the tool
2. **Use interactive mode** - Easier for beginners
3. **Check debug_logs/** - Full execution details saved
4. **Replay failed executions** - Debug without re-running
5. **Create test template** - Reuse for similar exercises

---

## Next Steps

1. ✅ Try the example: `python instructor_test_tool.py --example`
2. ✅ Test an existing exercise
3. ✅ Create test cases for new exercise
4. ✅ Share with other instructors

---

## Support

For questions or issues:
1. Check debug_logs/ for execution details
2. Use interactive mode for guided testing
3. Review test case format examples above

Happy testing! 🎓
