# app/python_practice/rate_limiter.py
"""Rate limiting for code execution."""

import time
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from flask_login import current_user


# In-memory rate limiting (use Redis in production)
_rate_limit_storage = {}


class RateLimiter:
    """Simple rate limiter for code execution."""
    
    def __init__(self, max_requests=10, time_window=60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
    
    def is_allowed(self, key):
        """
        Check if request is allowed.
        
        Args:
            key: Unique key for rate limiting (e.g., user_id)
            
        Returns:
            Tuple of (is_allowed, remaining_requests, reset_time)
        """
        current_time = time.time()
        
        if key not in _rate_limit_storage:
            _rate_limit_storage[key] = []
        
        # Remove old requests outside time window
        _rate_limit_storage[key] = [
            req_time for req_time in _rate_limit_storage[key]
            if current_time - req_time < self.time_window
        ]
        
        # Check if limit exceeded
        if len(_rate_limit_storage[key]) >= self.max_requests:
            oldest_request = min(_rate_limit_storage[key])
            reset_time = oldest_request + self.time_window
            remaining_requests = 0
            return False, remaining_requests, reset_time
        
        # Add current request
        _rate_limit_storage[key].append(current_time)
        
        remaining_requests = self.max_requests - len(_rate_limit_storage[key])
        reset_time = current_time + self.time_window
        
        return True, remaining_requests, reset_time
    
    def reset(self, key):
        """Reset rate limit for a key."""
        if key in _rate_limit_storage:
            del _rate_limit_storage[key]


# Global rate limiters
code_execution_limiter = RateLimiter(max_requests=10, time_window=60)  # 10 per minute
solution_view_limiter = RateLimiter(max_requests=5, time_window=300)  # 5 per 5 minutes


def rate_limit(limiter, get_key=None):
    """
    Decorator for rate limiting.
    
    Args:
        limiter: RateLimiter instance
        get_key: Function to get rate limit key (default: user_id)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get rate limit key
            if get_key:
                key = get_key()
            elif current_user.is_authenticated:
                key = f'user_{current_user.id}'
            else:
                key = f'ip_{request.remote_addr}'
            
            # Check rate limit
            is_allowed, remaining, reset_time = limiter.is_allowed(key)
            
            if not is_allowed:
                reset_datetime = datetime.fromtimestamp(reset_time)
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Please try again after {reset_datetime.strftime("%H:%M:%S")}',
                    'retry_after': int(reset_time - time.time())
                }), 429
            
            # Add rate limit headers
            response = f(*args, **kwargs)
            
            if isinstance(response, tuple):
                response_obj, status_code = response[0], response[1]
            else:
                response_obj = response
                status_code = 200
            
            # Add headers if response is a Response object
            if hasattr(response_obj, 'headers'):
                response_obj.headers['X-RateLimit-Limit'] = str(limiter.max_requests)
                response_obj.headers['X-RateLimit-Remaining'] = str(remaining)
                response_obj.headers['X-RateLimit-Reset'] = str(int(reset_time))
            
            return response
        
        return decorated_function
    return decorator


# Convenience decorators
def rate_limit_code_execution(f):
    """Rate limit code execution endpoint."""
    return rate_limit(code_execution_limiter)(f)


def rate_limit_solution_view(f):
    """Rate limit solution viewing endpoint."""
    return rate_limit(solution_view_limiter)(f)
