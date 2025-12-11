# app/python_practice/validators.py
"""Code validation and security checks for Python submissions."""

import re
from datetime import datetime, timedelta
from typing import Tuple
from app.extensions import db


# Banned imports and keywords for security
BANNED_IMPORTS = [
    'os', 'sys', 'subprocess', 'eval', 'exec', 'compile',
    '__import__', 'importlib', 'open', 'file',
    'input', 'raw_input', 'execfile',
    'socket', 'urllib', 'requests', 'http',
    'pickle', 'shelve', 'marshal',
    'ctypes', 'multiprocessing', 'threading'
]

BANNED_KEYWORDS = [
    '__builtins__', '__globals__', '__locals__',
    '__code__', '__dict__', '__class__',
    'globals()', 'locals()', 'vars()',
    'dir()', 'help()'
]

# Allowed imports (whitelist)
ALLOWED_IMPORTS = [
    'math', 'random', 'datetime', 'collections',
    'itertools', 'functools', 're', 'json',
    'statistics', 'decimal', 'fractions'
]


def validate_python_code(code: str) -> Tuple[bool, str]:
    """
    Validate Python code for security issues.
    
    Args:
        code: Python code to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not code or not code.strip():
        return False, 'Code cannot be empty'
    
    # Check code length
    if len(code) > 10000:
        return False, 'Code is too long (max 10,000 characters)'
    
    # Check for banned imports
    for banned in BANNED_IMPORTS:
        patterns = [
            rf'\bimport\s+{banned}\b',
            rf'\bfrom\s+{banned}\b',
            rf'__import__\s*\(\s*["\'{banned}]'
        ]
        for pattern in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f'Banned import detected: {banned}'
    
    # Check for banned keywords
    for keyword in BANNED_KEYWORDS:
        if keyword in code:
            return False, f'Banned keyword detected: {keyword}'
    
    # Check for suspicious patterns
    suspicious_patterns = [
        (r'while\s+True\s*:', 'Infinite loops are not allowed'),
        (r'for\s+\w+\s+in\s+range\s*\(\s*\d{6,}', 'Loop range too large'),
        (r'\*\*\s*\d{4,}', 'Exponentiation too large'),
        (r'[\[\{].*[\]\}]\s*\*\s*\d{6,}', 'Data structure too large'),
    ]
    
    for pattern, message in suspicious_patterns:
        if re.search(pattern, code):
            return False, message
    
    # Basic syntax check
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        return False, f'Syntax error: {str(e)}'
    except Exception as e:
        return False, f'Code validation error: {str(e)}'
    
    return True, 'Code is valid'


def check_rate_limit(user_id: int, max_submissions: int = 10, time_window_minutes: int = 1) -> Tuple[bool, str]:
    """
    Check if user has exceeded rate limit for code submissions.
    
    Args:
        user_id: User ID
        max_submissions: Maximum submissions allowed in time window
        time_window_minutes: Time window in minutes
        
    Returns:
        Tuple of (is_allowed, message)
    """
    from app.models import ExerciseSubmission
    
    time_threshold = datetime.utcnow() - timedelta(minutes=time_window_minutes)
    
    recent_submissions = ExerciseSubmission.query.filter(
        ExerciseSubmission.user_id == user_id,
        ExerciseSubmission.submitted_at >= time_threshold
    ).count()
    
    if recent_submissions >= max_submissions:
        return False, f'Rate limit exceeded. Please wait before submitting again. ({max_submissions} submissions per {time_window_minutes} minute(s))'
    
    return True, 'OK'


def sanitize_output(output: str, max_length: int = 5000) -> str:
    """
    Sanitize output from code execution.
    
    Args:
        output: Output string
        max_length: Maximum output length
        
    Returns:
        Sanitized output string
    """
    if not output:
        return ''
    
    # Truncate if too long
    if len(output) > max_length:
        output = output[:max_length] + '\n\n... (output truncated)'
    
    # Remove any potential harmful characters
    output = output.replace('\x00', '')
    
    return output


def check_for_plagiarism(code: str, user_id: int, exercise_id: int) -> Tuple[bool, float]:
    """
    Basic plagiarism check against other submissions.
    TODO: Implement more sophisticated plagiarism detection.
    
    Args:
        code: Code to check
        user_id: User ID
        exercise_id: Exercise ID
        
    Returns:
        Tuple of (is_plagiarized, similarity_score)
    """
    # This is a placeholder for future implementation
    return False, 0.0
