# app/python_practice/executor_enhanced.py
"""Enhanced Python code execution engine with flexible test validation."""

import json
import time
import subprocess
import tempfile
import os
import re
from typing import Dict, List, Any


def execute_python_code_enhanced(code: str, test_cases: List[Dict], timeout: int = 30) -> Dict[str, Any]:
    """
    Execute Python code with enhanced flexible test validation.
    
    Supported test types:
    - assert_function: Test function return values
    - assert_output: Test exact output (with options for case_sensitive, strip_whitespace)
    - assert_output_contains: Check if output contains text
    - assert_output_regex: Match output against regex
    - assert_variable_exists: Check if variable is defined
    - assert_variable_type: Check variable type
    - assert_variable_length: Check collection length
    - assert_variable_value: Check variable value
    - assert_custom: Custom Python expression validation
    """
    result = {
        'status': 'error',
        'output': '',
        'error': '',
        'test_results': [],
        'tests_passed': 0,
        'tests_failed': 0,
        'execution_time_ms': 0,
        'is_flagged': False,
        'flagged_reason': None
    }
    
    start_time = time.time()
    
    try:
        result = execute_enhanced_local(code, test_cases, timeout)
    except Exception as e:
        result['status'] = 'error'
        result['error'] = f'Execution error: {str(e)}'
    finally:
        execution_time = (time.time() - start_time) * 1000
        result['execution_time_ms'] = int(execution_time)
    
    return result


def execute_enhanced_local(code: str, test_cases: List[Dict], timeout: int) -> Dict[str, Any]:
    """Execute with enhanced test validation."""
    
    result = {
        'status': 'passed',
        'output': '',
        'error': '',
        'test_results': [],
        'tests_passed': 0,
        'tests_failed': 0,
        'is_flagged': False
    }
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        temp_file = f.name
        
        # Add test framework FIRST to capture all output
        f.write('''
# Test execution framework
import json
import sys
import re
from io import StringIO

# Capture stdout for output tests
original_stdout = sys.stdout
captured_output = StringIO()
sys.stdout = captured_output

test_results = []
''')
        
        # Write user code AFTER setting up stdout capture
        f.write('\n# User code\n')
        f.write(code)
        f.write('\n\n')
        
        # Generate test code for each test case
        for i, test in enumerate(test_cases):
            test_type = test.get('type', 'assert_function')
            description = test.get('description', f'Test {i+1}')
            
            f.write(f'\n# Test {i+1}: {description}\n')
            f.write('try:\n')
            
            if test_type == 'assert_function':
                # Test function return value
                function_name = test.get('function_name', 'solution')
                test_input = test.get('input', [])
                expected = test.get('expected')
                expected_any_of = test.get('expected_any_of', [])
                
                if isinstance(test_input, list):
                    args = ', '.join([repr(arg) for arg in test_input])
                else:
                    args = repr(test_input)
                
                f.write(f'    actual = {function_name}({args})\n')
                
                if expected_any_of:
                    f.write(f'    expected_any = {repr(expected_any_of)}\n')
                    f.write('    passed = actual in expected_any\n')
                    f.write(f'    expected = expected_any\n')
                else:
                    f.write(f'    expected = {repr(expected)}\n')
                    f.write('    passed = actual == expected\n')
                
            elif test_type == 'assert_output':
                # Test exact output
                expected = test.get('expected', '')
                case_sensitive = test.get('case_sensitive', True)
                strip_whitespace = test.get('strip_whitespace', True)
                
                f.write('    output = captured_output.getvalue()\n')
                if strip_whitespace:
                    f.write('    output = output.strip()\n')
                    f.write(f'    expected = {repr(expected)}.strip()\n')
                else:
                    f.write(f'    expected = {repr(expected)}\n')
                
                if not case_sensitive:
                    f.write('    passed = output.lower() == expected.lower()\n')
                else:
                    f.write('    passed = output == expected\n')
                
                f.write('    actual = output\n')
                
            elif test_type == 'assert_output_contains':
                # Check if output contains text
                expected = test.get('expected', '')
                case_sensitive = test.get('case_sensitive', True)
                
                f.write('    output = captured_output.getvalue()\n')
                f.write(f'    expected = {repr(expected)}\n')
                
                if not case_sensitive:
                    f.write('    passed = expected.lower() in output.lower()\n')
                else:
                    f.write('    passed = expected in output\n')
                
                f.write('    actual = output\n')
                
            elif test_type == 'assert_output_regex':
                # Match output with regex
                pattern = test.get('pattern', '')
                flags_str = test.get('flags', '')
                
                f.write('    output = captured_output.getvalue().strip()\n')
                f.write(f'    pattern = {repr(pattern)}\n')
                
                flags_code = '0'
                if 'IGNORECASE' in flags_str or 'I' in flags_str:
                    flags_code = 're.IGNORECASE'
                
                f.write(f'    passed = bool(re.match(pattern, output, {flags_code}))\n')
                f.write('    actual = output\n')
                f.write(f'    expected = "matches pattern: {pattern}"\n')
                
            elif test_type == 'assert_variable_exists':
                # Check if variable exists
                var_name = test.get('variable_name', '')
                f.write(f'    passed = {repr(var_name)} in dir()\n')
                f.write(f'    expected = "Variable {var_name} exists"\n')
                f.write(f'    actual = "Variable {var_name} " + ("exists" if passed else "not found")\n')
                
            elif test_type == 'assert_variable_type':
                # Check variable type
                var_name = test.get('variable_name', '')
                expected_type = test.get('expected_type', 'str')
                
                f.write(f'    if {repr(var_name)} in dir():\n')
                f.write(f'        actual_type = type({var_name}).__name__\n')
                f.write(f'        passed = actual_type == {repr(expected_type)}\n')
                f.write(f'        expected = {repr(expected_type)}\n')
                f.write('        actual = actual_type\n')
                f.write('    else:\n')
                f.write('        passed = False\n')
                f.write(f'        expected = {repr(expected_type)}\n')
                f.write(f'        actual = "Variable {var_name} not found"\n')
                
            elif test_type == 'assert_variable_length':
                # Check collection length
                var_name = test.get('variable_name', '')
                expected_length = test.get('expected_length', 0)
                
                f.write(f'    if {repr(var_name)} in dir():\n')
                f.write(f'        actual_length = len({var_name})\n')
                f.write(f'        passed = actual_length == {expected_length}\n')
                f.write(f'        expected = {expected_length}\n')
                f.write('        actual = actual_length\n')
                f.write('    else:\n')
                f.write('        passed = False\n')
                f.write(f'        expected = {expected_length}\n')
                f.write(f'        actual = "Variable {var_name} not found"\n')
                
            elif test_type == 'assert_variable_value':
                # Check variable value
                var_name = test.get('variable_name', '')
                expected_value = test.get('expected_value')
                
                f.write(f'    if {repr(var_name)} in dir():\n')
                f.write(f'        actual = {var_name}\n')
                f.write(f'        expected = {repr(expected_value)}\n')
                f.write('        passed = actual == expected\n')
                f.write('    else:\n')
                f.write('        passed = False\n')
                f.write(f'        expected = {repr(expected_value)}\n')
                f.write(f'        actual = "Variable {var_name} not found"\n')
                
            elif test_type == 'assert_custom':
                # Custom validation code
                validation_code = test.get('code', 'True')
                f.write(f'    passed = bool({validation_code})\n')
                f.write('    expected = "Custom validation passed"\n')
                f.write('    actual = "Custom validation " + ("passed" if passed else "failed")\n')
            
            else:
                # Unknown test type
                f.write('    passed = False\n')
                f.write(f'    expected = "Unknown test type: {test_type}"\n')
                f.write('    actual = "Error"\n')
            
            # Append result
            f.write('    test_results.append({\n')
            f.write(f'        "test_number": {i+1},\n')
            f.write(f'        "description": {repr(description)},\n')
            f.write('        "passed": passed,\n')
            f.write('        "expected": expected,\n')
            f.write('        "actual": actual,\n')
            f.write('        "error": None\n')
            f.write('    })\n')
            
            f.write('except Exception as e:\n')
            f.write('    test_results.append({\n')
            f.write(f'        "test_number": {i+1},\n')
            f.write(f'        "description": {repr(description)},\n')
            f.write('        "passed": False,\n')
            f.write('        "expected": "Test should not raise exception",\n')
            f.write('        "actual": None,\n')
            f.write('        "error": str(e)\n')
            f.write('    })\n')
        
        # Output results
        f.write('''
# Restore stdout and print results
sys.stdout = original_stdout
print("__USER_OUTPUT__")
print(captured_output.getvalue())
print("__TEST_RESULTS__")
print(json.dumps(test_results))
''')
    
    try:
        # Execute
        process = subprocess.Popen(
            ['python', temp_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        stdout, stderr = process.communicate(timeout=timeout)
        
        # Parse results
        if '__TEST_RESULTS__' in stdout:
            parts = stdout.split('__USER_OUTPUT__')
            if len(parts) > 1:
                output_and_results = parts[1]
                result_parts = output_and_results.split('__TEST_RESULTS__')
                
                if len(result_parts) > 1:
                    result['output'] = result_parts[0].strip()
                    test_results_json = result_parts[1].strip()
                    
                    try:
                        test_results = json.loads(test_results_json)
                        result['test_results'] = test_results
                        
                        for test in test_results:
                            if test.get('passed', False):
                                result['tests_passed'] += 1
                            else:
                                result['tests_failed'] += 1
                        
                        if result['tests_failed'] == 0 and result['tests_passed'] > 0:
                            result['status'] = 'passed'
                        else:
                            result['status'] = 'failed'
                    except json.JSONDecodeError as e:
                        result['status'] = 'error'
                        result['error'] = f'Failed to parse test results: {e}'
        else:
            result['output'] = stdout
            result['status'] = 'error'
            result['error'] = 'No test results found'
        
        if stderr:
            result['error'] = stderr
            if result['status'] == 'passed':
                result['status'] = 'error'
    
    except subprocess.TimeoutExpired:
        result['status'] = 'timeout'
        result['error'] = f'Code execution exceeded {timeout} second time limit'
        try:
            process.kill()
        except:
            pass
    
    except Exception as e:
        result['status'] = 'error'
        result['error'] = f'Execution error: {str(e)}'
    
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass
    
    return result
