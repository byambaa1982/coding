# app/python_practice/debug_executor.py
"""
Debug-friendly Python code executor for instructors and testing.

This module provides enhanced debugging capabilities:
- Verbose logging of execution steps
- Optional preservation of temp files
- Standalone CLI for testing
- Detailed error reporting
- Test case replay functionality
"""

import json
import time
import subprocess
import tempfile
import os
import sys
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Import the base executor
from app.python_practice.executor_enhanced import execute_python_code_enhanced


class DebugExecutor:
    """Debug-friendly executor with enhanced logging and inspection."""
    
    def __init__(
        self,
        debug_mode: bool = True,
        preserve_temp_files: bool = False,
        log_dir: Optional[str] = None,
        verbose: bool = True
    ):
        """
        Initialize debug executor.
        
        Args:
            debug_mode: Enable detailed logging
            preserve_temp_files: Keep temp files after execution
            log_dir: Directory to save execution logs (default: ./debug_logs)
            verbose: Print execution details to console
        """
        self.debug_mode = debug_mode
        self.preserve_temp_files = preserve_temp_files
        self.verbose = verbose
        
        # Set up logging
        self.log_dir = Path(log_dir or './debug_logs')
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = self._setup_logger()
        self.execution_count = 0
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logger for debug output."""
        logger = logging.getLogger('debug_executor')
        logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        
        # File handler
        log_file = self.log_dir / f'executor_{datetime.now():%Y%m%d_%H%M%S}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        if self.verbose:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            logger.addHandler(console_handler)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        return logger
    
    def execute(
        self,
        code: str,
        test_cases: List[Dict],
        timeout: int = 30,
        save_execution: bool = True
    ) -> Dict[str, Any]:
        """
        Execute code with debug logging.
        
        Args:
            code: Python code to execute
            test_cases: List of test case dictionaries
            timeout: Maximum execution time in seconds
            save_execution: Save execution details to file
            
        Returns:
            Execution result with additional debug info
        """
        self.execution_count += 1
        exec_id = f"exec_{self.execution_count}_{int(time.time())}"
        
        self.logger.info(f"="*60)
        self.logger.info(f"Starting execution {exec_id}")
        self.logger.info(f"Code length: {len(code)} characters")
        self.logger.info(f"Test cases: {len(test_cases)}")
        self.logger.info(f"Timeout: {timeout}s")
        
        # Log code (first 500 chars)
        code_preview = code[:500] + "..." if len(code) > 500 else code
        self.logger.debug(f"Code preview:\n{code_preview}")
        
        # Log test cases
        for i, tc in enumerate(test_cases):
            self.logger.debug(f"Test {i+1}: {tc.get('description', 'No description')}")
            self.logger.debug(f"  Type: {tc.get('type', 'assert_function')}")
        
        # Execute
        start_time = time.time()
        try:
            result = execute_python_code_enhanced(code, test_cases, timeout)
            execution_time = time.time() - start_time
            
            self.logger.info(f"Execution completed in {execution_time:.2f}s")
            self.logger.info(f"Status: {result.get('status')}")
            self.logger.info(f"Tests passed: {result.get('tests_passed', 0)}/{len(test_cases)}")
            
            if result.get('error'):
                self.logger.error(f"Error: {result.get('error')}")
            
            # Log test results
            for tr in result.get('test_results', []):
                status = "✓ PASS" if tr.get('passed') else "✗ FAIL"
                self.logger.info(f"  {status}: Test {tr.get('test_number')} - {tr.get('description')}")
                if not tr.get('passed'):
                    self.logger.debug(f"    Expected: {tr.get('expected')}")
                    self.logger.debug(f"    Actual: {tr.get('actual')}")
                    if tr.get('error'):
                        self.logger.debug(f"    Error: {tr.get('error')}")
            
            # Save execution details
            if save_execution:
                self._save_execution(exec_id, code, test_cases, result)
            
            # Add debug info to result
            result['debug_info'] = {
                'execution_id': exec_id,
                'log_file': str(self.logger.handlers[0].baseFilename),
                'execution_time': execution_time
            }
            
            return result
            
        except Exception as e:
            self.logger.exception(f"Execution failed with exception: {str(e)}")
            raise
    
    def _save_execution(self, exec_id: str, code: str, test_cases: List[Dict], result: Dict):
        """Save execution details to file."""
        exec_dir = self.log_dir / exec_id
        exec_dir.mkdir(exist_ok=True)
        
        # Save code
        code_file = exec_dir / 'code.py'
        code_file.write_text(code, encoding='utf-8')
        self.logger.debug(f"Saved code to {code_file}")
        
        # Save test cases
        test_file = exec_dir / 'test_cases.json'
        test_file.write_text(json.dumps(test_cases, indent=2), encoding='utf-8')
        self.logger.debug(f"Saved test cases to {test_file}")
        
        # Save results
        result_file = exec_dir / 'result.json'
        result_file.write_text(json.dumps(result, indent=2, default=str), encoding='utf-8')
        self.logger.debug(f"Saved results to {result_file}")
        
        # Create summary report
        summary_file = exec_dir / 'summary.txt'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Execution Summary - {exec_id}\n")
            f.write("="*60 + "\n\n")
            f.write(f"Status: {result.get('status')}\n")
            f.write(f"Tests Passed: {result.get('tests_passed', 0)}/{len(test_cases)}\n")
            f.write(f"Execution Time: {result.get('execution_time_ms', 0)}ms\n\n")
            
            if result.get('output'):
                f.write(f"Output:\n{result['output']}\n\n")
            
            if result.get('error'):
                f.write(f"Error:\n{result['error']}\n\n")
            
            f.write("Test Results:\n")
            for tr in result.get('test_results', []):
                status = "PASS" if tr.get('passed') else "FAIL"
                f.write(f"  [{status}] Test {tr.get('test_number')}: {tr.get('description')}\n")
                if not tr.get('passed'):
                    f.write(f"       Expected: {tr.get('expected')}\n")
                    f.write(f"       Actual: {tr.get('actual')}\n")
                    if tr.get('error'):
                        f.write(f"       Error: {tr.get('error')}\n")
        
        self.logger.info(f"Execution saved to {exec_dir}")
    
    def replay_execution(self, exec_id: str) -> Dict[str, Any]:
        """
        Replay a saved execution.
        
        Args:
            exec_id: Execution ID to replay
            
        Returns:
            New execution result
        """
        exec_dir = self.log_dir / exec_id
        
        if not exec_dir.exists():
            raise FileNotFoundError(f"Execution {exec_id} not found")
        
        # Load code and test cases
        code = (exec_dir / 'code.py').read_text(encoding='utf-8')
        test_cases = json.loads((exec_dir / 'test_cases.json').read_text(encoding='utf-8'))
        
        self.logger.info(f"Replaying execution {exec_id}")
        return self.execute(code, test_cases)
    
    def list_executions(self) -> List[str]:
        """List all saved executions."""
        executions = [d.name for d in self.log_dir.iterdir() if d.is_dir() and d.name.startswith('exec_')]
        return sorted(executions, reverse=True)


def execute_with_debug(
    code: str,
    test_cases: List[Dict],
    timeout: int = 30,
    preserve_files: bool = False,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Convenience function for debug execution.
    
    Args:
        code: Python code to execute
        test_cases: List of test cases
        timeout: Timeout in seconds
        preserve_files: Keep temp files after execution
        verbose: Print to console
        
    Returns:
        Execution result with debug info
    """
    executor = DebugExecutor(
        debug_mode=True,
        preserve_temp_files=preserve_files,
        verbose=verbose
    )
    return executor.execute(code, test_cases, timeout)


# CLI for standalone testing
def main():
    """Command-line interface for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Debug Python code execution')
    parser.add_argument('code_file', help='Python file to execute')
    parser.add_argument('test_file', help='JSON file with test cases')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout in seconds')
    parser.add_argument('--preserve', action='store_true', help='Preserve temp files')
    parser.add_argument('--quiet', action='store_true', help='Quiet mode (no console output)')
    parser.add_argument('--replay', help='Replay execution by ID')
    parser.add_argument('--list', action='store_true', help='List saved executions')
    
    args = parser.parse_args()
    
    executor = DebugExecutor(
        debug_mode=True,
        preserve_temp_files=args.preserve,
        verbose=not args.quiet
    )
    
    if args.list:
        executions = executor.list_executions()
        print(f"\nFound {len(executions)} saved executions:")
        for exec_id in executions:
            print(f"  - {exec_id}")
        return
    
    if args.replay:
        result = executor.replay_execution(args.replay)
        print(f"\n{'='*60}")
        print(f"Replay Status: {result['status']}")
        print(f"Tests Passed: {result['tests_passed']}")
        return
    
    # Load code and test cases
    with open(args.code_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    with open(args.test_file, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    
    # Execute
    result = executor.execute(code, test_cases, args.timeout)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Execution Status: {result['status']}")
    print(f"Tests Passed: {result['tests_passed']}/{len(test_cases)}")
    print(f"Execution Time: {result.get('execution_time_ms', 0)}ms")
    
    if result.get('error'):
        print(f"\nError:\n{result['error']}")
    
    print(f"\nDebug info saved to: {result['debug_info']['execution_id']}")


if __name__ == '__main__':
    main()
