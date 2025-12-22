#!/usr/bin/env python
"""
Instructor Testing Tool
=======================
Standalone tool for instructors to test Python exercises without running the web app.

Usage:
    python instructor_test_tool.py <code_file> <test_cases_file>
    python instructor_test_tool.py --interactive
    python instructor_test_tool.py --example
"""

import sys
import os
import json
from pathlib import Path

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.python_practice.debug_executor import DebugExecutor


def run_test(code_file: str, test_file: str, verbose: bool = True):
    """Run a test from files."""
    
    # Load code
    code_path = Path(code_file)
    if not code_path.exists():
        print(f"❌ Code file not found: {code_file}")
        return False
    
    code = code_path.read_text(encoding='utf-8')
    
    # Load test cases
    test_path = Path(test_file)
    if not test_path.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    test_cases = json.loads(test_path.read_text(encoding='utf-8'))
    
    # Execute
    print(f"\n{'='*70}")
    print(f"Testing: {code_path.name}")
    print(f"Test cases: {len(test_cases)}")
    print(f"{'='*70}\n")
    
    executor = DebugExecutor(debug_mode=True, verbose=verbose)
    result = executor.execute(code, test_cases, timeout=30)
    
    # Print results
    print(f"\n{'='*70}")
    print(f"📊 RESULTS")
    print(f"{'='*70}")
    print(f"Status: {result['status'].upper()}")
    print(f"Tests Passed: {result['tests_passed']}/{len(test_cases)}")
    print(f"Execution Time: {result.get('execution_time_ms', 0)}ms")
    
    if result.get('output'):
        print(f"\n📝 Output:")
        print(result['output'])
    
    if result.get('error'):
        print(f"\n❌ Error:")
        print(result['error'])
    
    print(f"\n📋 Test Details:")
    for tr in result.get('test_results', []):
        status_icon = "✅" if tr.get('passed') else "❌"
        print(f"\n  {status_icon} Test {tr.get('test_number')}: {tr.get('description')}")
        
        if not tr.get('passed'):
            print(f"     Expected: {tr.get('expected')}")
            print(f"     Actual:   {tr.get('actual')}")
            if tr.get('error'):
                print(f"     Error:    {tr.get('error')}")
    
    print(f"\n💾 Full details saved to: debug_logs/{result['debug_info']['execution_id']}")
    print(f"{'='*70}\n")
    
    return result['status'] == 'passed'


def interactive_mode():
    """Interactive testing mode."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║        Interactive Python Exercise Testing Tool              ║
╚══════════════════════════════════════════════════════════════╝

This tool helps you test Python exercises without running the web app.
""")
    
    while True:
        print("\nOptions:")
        print("  1. Test code from file")
        print("  2. Test code inline")
        print("  3. Create example test")
        print("  4. List saved executions")
        print("  5. Replay execution")
        print("  6. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            code_file = input("Code file path: ").strip()
            test_file = input("Test cases file path: ").strip()
            run_test(code_file, test_file)
        
        elif choice == '2':
            print("\nEnter code (end with Ctrl+D on Unix or Ctrl+Z on Windows):")
            code_lines = []
            try:
                while True:
                    code_lines.append(input())
            except EOFError:
                pass
            
            code = '\n'.join(code_lines)
            
            test_file = input("Test cases file path: ").strip()
            test_cases = json.loads(Path(test_file).read_text(encoding='utf-8'))
            
            executor = DebugExecutor(debug_mode=True, verbose=True)
            result = executor.execute(code, test_cases, timeout=30)
            print(f"\nStatus: {result['status']}")
            print(f"Tests Passed: {result['tests_passed']}")
        
        elif choice == '3':
            create_example()
        
        elif choice == '4':
            executor = DebugExecutor()
            executions = executor.list_executions()
            print(f"\n📁 Found {len(executions)} saved executions:")
            for i, exec_id in enumerate(executions[:10], 1):
                print(f"  {i}. {exec_id}")
            if len(executions) > 10:
                print(f"  ... and {len(executions) - 10} more")
        
        elif choice == '5':
            exec_id = input("Execution ID to replay: ").strip()
            executor = DebugExecutor(debug_mode=True, verbose=True)
            try:
                result = executor.replay_execution(exec_id)
                print(f"\nReplay Status: {result['status']}")
                print(f"Tests Passed: {result['tests_passed']}")
            except FileNotFoundError:
                print(f"❌ Execution not found: {exec_id}")
        
        elif choice == '6':
            print("\nGoodbye! 👋")
            break
        
        else:
            print("Invalid choice. Please try again.")


def create_example():
    """Create example files for testing."""
    
    print("\n📝 Creating example files...")
    
    # Example code
    code = '''def greet(name):
    """Return a greeting message."""
    return f"Hello, {name}!"

def add(a, b):
    """Add two numbers."""
    return a + b
'''
    
    # Example test cases
    test_cases = [
        {
            "type": "assert_function",
            "description": "Test greet function",
            "function_name": "greet",
            "input": ["Alice"],
            "expected": "Hello, Alice!"
        },
        {
            "type": "assert_function",
            "description": "Test add function",
            "function_name": "add",
            "input": [2, 3],
            "expected": 5
        }
    ]
    
    # Save files
    code_path = Path('example_code.py')
    test_path = Path('example_tests.json')
    
    code_path.write_text(code, encoding='utf-8')
    test_path.write_text(json.dumps(test_cases, indent=2), encoding='utf-8')
    
    print(f"✅ Created: {code_path}")
    print(f"✅ Created: {test_path}")
    print(f"\nRun with: python instructor_test_tool.py {code_path} {test_path}")
    
    # Ask if they want to run it now
    run_now = input("\nRun example now? (y/n): ").strip().lower()
    if run_now == 'y':
        run_test(str(code_path), str(test_path))


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test Python exercises for instructors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python instructor_test_tool.py code.py tests.json
  python instructor_test_tool.py --interactive
  python instructor_test_tool.py --example
        """
    )
    
    parser.add_argument('code_file', nargs='?', help='Python code file to test')
    parser.add_argument('test_file', nargs='?', help='JSON file with test cases')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('-e', '--example', action='store_true', help='Create example files')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.example:
        create_example()
    elif args.code_file and args.test_file:
        success = run_test(args.code_file, args.test_file, verbose=not args.quiet)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        print("\n💡 Tip: Use --interactive for a guided experience")


if __name__ == '__main__':
    main()
