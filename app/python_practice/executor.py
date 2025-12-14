# app/python_practice/executor.py
"""Python code execution engine with Docker sandbox."""

import json
import time
import subprocess
import tempfile
import os
from typing import Dict, List, Any

# Import enhanced executor
from app.python_practice.executor_enhanced import execute_python_code_enhanced


def execute_python_code(code: str, test_cases: List[Dict], timeout: int = 30) -> Dict[str, Any]:
    """
    Execute Python code with test cases in a secure sandbox.
    
    Args:
        code: Python code to execute
        test_cases: List of test case dictionaries
        timeout: Maximum execution time in seconds
    
    Returns:
        Dictionary with execution results
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
        # Use enhanced executor with flexible test validation
        result = execute_python_code_enhanced(code, test_cases, timeout)
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = f'Execution error: {str(e)}'
    
    finally:
        execution_time = (time.time() - start_time) * 1000
        result['execution_time_ms'] = int(execution_time)
    
    return result


def execute_local_python(code: str, test_cases: List[Dict], timeout: int) -> Dict[str, Any]:
    """
    Execute Python code locally (temporary implementation).
    TODO: Replace with Docker-based execution for security.
    """
    result = {
        'status': 'passed',
        'output': '',
        'error': '',
        'test_results': [],
        'tests_passed': 0,
        'tests_failed': 0,
        'is_flagged': False
    }
    
    # Create a temporary file for the code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        temp_file = f.name
        
        # Write the user code
        f.write(code)
        f.write('\n\n')
        
        # Add test execution code
        f.write('# Test execution code\n')
        f.write('import json\n')
        f.write('import sys\n\n')
        f.write('test_results = []\n\n')
        
        # Generate test execution code
        for i, test_case in enumerate(test_cases):
            test_input = test_case.get('input', {})
            expected_output = test_case.get('expected', None)
            test_description = test_case.get('description', f'Test {i+1}')
            function_name = test_case.get('function_name', 'solution')
            
            f.write(f'# Test case {i+1}: {test_description}\n')
            f.write('try:\n')
            
            # Build function call
            if isinstance(test_input, dict):
                args = ', '.join([f'{k}={repr(v)}' for k, v in test_input.items()])
            elif isinstance(test_input, list):
                args = ', '.join([repr(arg) for arg in test_input])
            else:
                args = repr(test_input)
            
            f.write(f'    actual = {function_name}({args})\n')
            f.write(f'    expected = {repr(expected_output)}\n')
            f.write('    passed = actual == expected\n')
            f.write('    test_results.append({\n')
            f.write(f'        "test_number": {i+1},\n')
            f.write(f'        "description": {repr(test_description)},\n')
            f.write('        "passed": passed,\n')
            f.write('        "expected": expected,\n')
            f.write('        "actual": actual,\n')
            f.write('        "error": None\n')
            f.write('    })\n')
            f.write('except Exception as e:\n')
            f.write('    test_results.append({\n')
            f.write(f'        "test_number": {i+1},\n')
            f.write(f'        "description": {repr(test_description)},\n')
            f.write('        "passed": False,\n')
            f.write(f'        "expected": {repr(expected_output)},\n')
            f.write('        "actual": None,\n')
            f.write('        "error": str(e)\n')
            f.write('    })\n\n')
        
        # Print results as JSON
        f.write('print("__TEST_RESULTS__")\n')
        f.write('print(json.dumps(test_results))\n')
    
    try:
        # Execute the code with timeout
        process = subprocess.Popen(
            ['python', temp_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(timeout=timeout)
        
        # Parse output
        if '__TEST_RESULTS__' in stdout:
            parts = stdout.split('__TEST_RESULTS__')
            result['output'] = parts[0].strip()
            
            try:
                test_results_json = parts[1].strip()
                test_results = json.loads(test_results_json)
                result['test_results'] = test_results
                
                # Count passed/failed
                for test in test_results:
                    if test.get('passed', False):
                        result['tests_passed'] += 1
                    else:
                        result['tests_failed'] += 1
                
                # Determine overall status
                if result['tests_failed'] == 0 and result['tests_passed'] > 0:
                    result['status'] = 'passed'
                else:
                    result['status'] = 'failed'
                    
            except json.JSONDecodeError:
                result['status'] = 'error'
                result['error'] = 'Failed to parse test results'
        else:
            result['output'] = stdout
            result['status'] = 'error'
            result['error'] = 'No test results found'
        
        if stderr:
            result['error'] = stderr
            if result['status'] == 'passed':
                result['status'] = 'error'
        
        if process.returncode != 0 and result['status'] == 'passed':
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
        # Clean up temporary file
        try:
            os.unlink(temp_file)
        except:
            pass
    
    return result


def execute_docker_python(code: str, test_cases: List[Dict], timeout: int) -> Dict[str, Any]:
    """
    Execute Python code in Docker container (secure sandbox).
    TODO: Implement Docker-based execution.
    """
    # This will be implemented when Docker is set up
    raise NotImplementedError('Docker execution not yet implemented')
