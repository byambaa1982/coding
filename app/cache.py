# app/cache.py
"""
Redis caching utilities for Phase 9.1
Provides caching decorators and utilities for improved performance.
"""

import redis
import json
import functools
from flask import current_app
from datetime import timedelta


class CacheManager:
    """Manage Redis caching operations."""
    
    def __init__(self, app=None):
        self.redis_client = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Redis connection."""
        redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        try:
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            app.logger.info("✅ Redis cache connected successfully")
        except Exception as e:
            app.logger.warning(f"⚠️  Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None
    
    def get(self, key):
        """Get value from cache."""
        if not self.redis_client:
            return None
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            current_app.logger.error(f"Cache get error: {e}")
        return None
    
    def set(self, key, value, timeout=300):
        """Set value in cache with timeout (default 5 minutes)."""
        if not self.redis_client:
            return False
        try:
            serialized = json.dumps(value)
            self.redis_client.setex(key, timeout, serialized)
            return True
        except Exception as e:
            current_app.logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key):
        """Delete key from cache."""
        if not self.redis_client:
            return False
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            current_app.logger.error(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern):
        """Delete all keys matching pattern."""
        if not self.redis_client:
            return False
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            current_app.logger.error(f"Cache delete pattern error: {e}")
            return False
    
    def clear_all(self):
        """Clear entire cache (use with caution)."""
        if not self.redis_client:
            return False
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            current_app.logger.error(f"Cache clear error: {e}")
            return False
    
    def get_stats(self):
        """Get cache statistics."""
        if not self.redis_client:
            return {'enabled': False}
        try:
            info = self.redis_client.info('stats')
            return {
                'enabled': True,
                'total_commands': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(
                    info.get('keyspace_hits', 0),
                    info.get('keyspace_misses', 0)
                )
            }
        except Exception as e:
            current_app.logger.error(f"Cache stats error: {e}")
            return {'enabled': False, 'error': str(e)}
    
    @staticmethod
    def _calculate_hit_rate(hits, misses):
        """Calculate cache hit rate percentage."""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)


# Global cache manager instance
cache_manager = CacheManager()


def cached(timeout=300, key_prefix='view'):
    """
    Decorator to cache function results.
    
    Usage:
        @cached(timeout=600, key_prefix='catalog')
        def get_courses():
            return Course.query.all()
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Build cache key
            cache_key = f"{key_prefix}:{f.__name__}"
            if args:
                cache_key += f":{':'.join(str(arg) for arg in args)}"
            if kwargs:
                cache_key += f":{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                current_app.logger.debug(f"Cache HIT: {cache_key}")
                return cached_value
            
            # Cache miss - execute function
            current_app.logger.debug(f"Cache MISS: {cache_key}")
            result = f(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_key, result, timeout)
            return result
        
        return decorated_function
    return decorator


def invalidate_cache(pattern):
    """
    Invalidate cache entries matching pattern.
    
    Usage:
        invalidate_cache('catalog:*')
    """
    return cache_manager.delete_pattern(pattern)


def cache_course_catalog(courses, timeout=600):
    """Cache course catalog data."""
    cache_manager.set('catalog:all_courses', courses, timeout)


def get_cached_course_catalog():
    """Get cached course catalog."""
    return cache_manager.get('catalog:all_courses')


def cache_user_enrollments(user_id, enrollments, timeout=300):
    """Cache user enrollments."""
    cache_manager.set(f'user:{user_id}:enrollments', enrollments, timeout)


def get_cached_user_enrollments(user_id):
    """Get cached user enrollments."""
    return cache_manager.get(f'user:{user_id}:enrollments')


def cache_tutorial_details(tutorial_id, data, timeout=1800):
    """Cache tutorial details (30 minutes)."""
    cache_manager.set(f'tutorial:{tutorial_id}:details', data, timeout)


def get_cached_tutorial_details(tutorial_id):
    """Get cached tutorial details."""
    return cache_manager.get(f'tutorial:{tutorial_id}:details')


def invalidate_tutorial_cache(tutorial_id):
    """Invalidate all cache entries for a tutorial."""
    invalidate_cache(f'tutorial:{tutorial_id}:*')


def invalidate_user_cache(user_id):
    """Invalidate all cache entries for a user."""
    invalidate_cache(f'user:{user_id}:*')


def cache_statistics(stats, timeout=3600):
    """Cache platform statistics (1 hour)."""
    cache_manager.set('stats:platform', stats, timeout)


def get_cached_statistics():
    """Get cached platform statistics."""
    return cache_manager.get('stats:platform')
