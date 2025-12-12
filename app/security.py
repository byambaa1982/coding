# app/security.py
"""
Security utilities for Phase 9.2
Input validation, sanitization, and security helpers.
"""

import re
import html
import bleach
from functools import wraps
from flask import request, abort, current_app, jsonify
from flask_login import current_user
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib


class InputValidator:
    """Validate and sanitize user inputs."""
    
    # Allowed HTML tags for rich text content
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'a', 'code', 'pre', 'blockquote', 'img'
    ]
    
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title'],
        'code': ['class']
    }
    
    @staticmethod
    def sanitize_html(text, allow_tags=True):
        """
        Sanitize HTML input to prevent XSS attacks.
        
        Args:
            text: Input text potentially containing HTML
            allow_tags: Whether to allow safe HTML tags
            
        Returns:
            Sanitized text safe for rendering
        """
        if not text:
            return text
            
        if allow_tags:
            # Use bleach to clean HTML with allowed tags
            return bleach.clean(
                text,
                tags=InputValidator.ALLOWED_TAGS,
                attributes=InputValidator.ALLOWED_ATTRIBUTES,
                strip=True
            )
        else:
            # Strip all HTML
            return html.escape(text)
    
    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitize filename to prevent directory traversal.
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        if not filename:
            return filename
        
        # Remove path separators and dangerous characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        filename = filename.replace('..', '')
        filename = filename.strip('. ')
        
        return filename[:255]  # Limit length
    
    @staticmethod
    def sanitize_email(email):
        """
        Validate and normalize email address.
        
        Args:
            email: Email address to validate
            
        Returns:
            Normalized email or None if invalid
        """
        if not email:
            return None
        
        email = email.strip().lower()
        
        # Basic email regex validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return None
        
        # Check length
        if len(email) > 255:
            return None
        
        return email
    
    @staticmethod
    def validate_url(url):
        """
        Validate URL to prevent SSRF and malicious redirects.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not url:
            return False
        
        # Must start with http:// or https://
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Block localhost and private IPs
        blocked_patterns = [
            r'localhost',
            r'127\.0\.0\.1',
            r'0\.0\.0\.0',
            r'10\.\d+\.\d+\.\d+',
            r'172\.(1[6-9]|2[0-9]|3[0-1])\.\d+\.\d+',
            r'192\.168\.\d+\.\d+'
        ]
        
        for pattern in blocked_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True
    
    @staticmethod
    def validate_slug(slug):
        """
        Validate URL slug format.
        
        Args:
            slug: URL slug to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not slug:
            return False
        
        # Only lowercase letters, numbers, and hyphens
        pattern = r'^[a-z0-9-]+$'
        if not re.match(pattern, slug):
            return False
        
        # Check length
        if len(slug) < 3 or len(slug) > 200:
            return False
        
        # Must not start or end with hyphen
        if slug.startswith('-') or slug.endswith('-'):
            return False
        
        return True
    
    @staticmethod
    def sanitize_search_query(query):
        """
        Sanitize search query to prevent SQL injection.
        
        Args:
            query: Search query string
            
        Returns:
            Sanitized query
        """
        if not query:
            return query
        
        # Remove SQL-like syntax
        query = re.sub(r'[;\'"\\]', '', query)
        
        # Limit length
        query = query[:500]
        
        return query.strip()
    
    @staticmethod
    def validate_integer(value, min_val=None, max_val=None):
        """
        Validate integer input with optional range check.
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Integer value or None if invalid
        """
        try:
            value = int(value)
            
            if min_val is not None and value < min_val:
                return None
            
            if max_val is not None and value > max_val:
                return None
            
            return value
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_price(price):
        """
        Validate price input.
        
        Args:
            price: Price value to validate
            
        Returns:
            Float price or None if invalid
        """
        try:
            price = float(price)
            
            if price < 0 or price > 999999.99:
                return None
            
            # Round to 2 decimal places
            return round(price, 2)
        except (ValueError, TypeError):
            return None


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked_ips = {}
    
    def is_rate_limited(self, identifier, max_requests=60, window_seconds=60):
        """
        Check if identifier is rate limited.
        
        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            
        Returns:
            True if rate limited, False otherwise
        """
        now = datetime.utcnow()
        
        # Check if blocked
        if identifier in self.blocked_ips:
            unblock_time = self.blocked_ips[identifier]
            if now < unblock_time:
                return True
            else:
                del self.blocked_ips[identifier]
        
        # Clean old requests
        cutoff = now - timedelta(seconds=window_seconds)
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff
        ]
        
        # Check rate limit
        if len(self.requests[identifier]) >= max_requests:
            # Block for 5 minutes
            self.blocked_ips[identifier] = now + timedelta(minutes=5)
            return True
        
        # Add current request
        self.requests[identifier].append(now)
        return False
    
    def get_remaining_requests(self, identifier, max_requests=60, window_seconds=60):
        """Get number of remaining requests for identifier."""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)
        
        recent_requests = [
            req_time for req_time in self.requests.get(identifier, [])
            if req_time > cutoff
        ]
        
        return max(0, max_requests - len(recent_requests))


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests=60, window_seconds=60, key_func=None):
    """
    Decorator to rate limit endpoints.
    
    Args:
        max_requests: Maximum requests in window
        window_seconds: Time window in seconds
        key_func: Function to generate identifier (default: IP address)
        
    Usage:
        @rate_limit(max_requests=10, window_seconds=60)
        def login():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get identifier
            if key_func:
                identifier = key_func()
            else:
                identifier = request.remote_addr
            
            # Check rate limit
            if rate_limiter.is_rate_limited(identifier, max_requests, window_seconds):
                remaining = rate_limiter.get_remaining_requests(
                    identifier, max_requests, window_seconds
                )
                
                current_app.logger.warning(
                    f"Rate limit exceeded for {identifier}"
                )
                
                if request.is_json:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'retry_after': 300
                    }), 429
                else:
                    abort(429)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def sanitize_form_data(form_data):
    """
    Sanitize all form data fields.
    
    Args:
        form_data: Dictionary of form data
        
    Returns:
        Sanitized form data dictionary
    """
    sanitized = {}
    
    for key, value in form_data.items():
        if isinstance(value, str):
            # Sanitize string fields
            sanitized[key] = InputValidator.sanitize_html(value, allow_tags=False)
        else:
            sanitized[key] = value
    
    return sanitized


def get_client_ip():
    """Get client IP address, accounting for proxies."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr


def generate_csrf_token():
    """Generate CSRF token for forms."""
    from flask_wtf.csrf import generate_csrf
    return generate_csrf()


def verify_recaptcha(response):
    """
    Verify reCAPTCHA response (placeholder for future implementation).
    
    Args:
        response: reCAPTCHA response token
        
    Returns:
        True if valid, False otherwise
    """
    # TODO: Implement reCAPTCHA verification
    return True


def check_password_strength(password):
    """
    Check password strength.
    
    Args:
        password: Password to check
        
    Returns:
        Tuple of (is_strong: bool, message: str)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Check for common passwords
    common_passwords = [
        'password', '12345678', 'qwerty', 'abc123', 'password123',
        'admin', 'letmein', 'welcome', 'monkey', '1234567890'
    ]
    
    if password.lower() in common_passwords:
        return False, "Password is too common, please choose a stronger one"
    
    return True, "Password is strong"


def hash_sensitive_data(data):
    """Hash sensitive data for logging/tracking without storing actual value."""
    return hashlib.sha256(data.encode()).hexdigest()[:16]
