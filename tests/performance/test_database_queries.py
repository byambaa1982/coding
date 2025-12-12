# tests/performance/test_database_queries.py
"""
Performance testing for database queries.
Phase 9.1 - Day 1: Database Analysis & Optimization
"""

import time
import statistics
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask import Flask
from app import create_app
from app.models import (
    TutorialUser, NewTutorial, Lesson, Exercise, 
    TutorialEnrollment, TutorialOrder, LessonProgress, Review
)
from app.extensions import db


class QueryProfiler:
    """Profile database queries for performance analysis."""
    
    def __init__(self):
        self.queries = []
        self.query_times = {}
        
    def start_profiling(self):
        """Start profiling database queries."""
        self.queries = []
        
        @event.listens_for(Engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())
            
        @event.listens_for(Engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, params, context, executemany):
            total_time = time.time() - conn.info['query_start_time'].pop()
            self.queries.append({
                'statement': statement,
                'params': params,
                'execution_time': total_time * 1000  # Convert to milliseconds
            })
    
    def get_slow_queries(self, threshold_ms=100):
        """Get queries that exceed the threshold."""
        return [q for q in self.queries if q['execution_time'] > threshold_ms]
    
    def get_query_stats(self):
        """Get query statistics."""
        if not self.queries:
            return None
            
        times = [q['execution_time'] for q in self.queries]
        return {
            'total_queries': len(self.queries),
            'total_time_ms': sum(times),
            'avg_time_ms': statistics.mean(times),
            'median_time_ms': statistics.median(times),
            'max_time_ms': max(times),
            'min_time_ms': min(times)
        }
    
    def print_report(self):
        """Print profiling report."""
        stats = self.get_query_stats()
        if not stats:
            print("No queries captured.")
            return
            
        print("\n" + "="*80)
        print("DATABASE QUERY PERFORMANCE REPORT")
        print("="*80)
        print(f"\nTotal Queries: {stats['total_queries']}")
        print(f"Total Time: {stats['total_time_ms']:.2f}ms")
        print(f"Average Time: {stats['avg_time_ms']:.2f}ms")
        print(f"Median Time: {stats['median_time_ms']:.2f}ms")
        print(f"Max Time: {stats['max_time_ms']:.2f}ms")
        print(f"Min Time: {stats['min_time_ms']:.2f}ms")
        
        slow_queries = self.get_slow_queries(threshold_ms=100)
        if slow_queries:
            print(f"\n⚠️  SLOW QUERIES (>100ms): {len(slow_queries)}")
            print("-"*80)
            for i, query in enumerate(slow_queries, 1):
                print(f"\n{i}. Execution Time: {query['execution_time']:.2f}ms")
                print(f"   SQL: {query['statement'][:200]}...")
        
        print("\n" + "="*80 + "\n")


def test_user_query_performance():
    """Test user-related query performance."""
    app = create_app()
    profiler = QueryProfiler()
    
    with app.app_context():
        profiler.start_profiling()
        
        print("\n📊 Testing User Query Performance...")
        
        # Test 1: Get all active users
        start = time.time()
        users = TutorialUser.query.filter_by(is_active=True).all()
        elapsed = (time.time() - start) * 1000
        print(f"✓ Query active users: {len(users)} users in {elapsed:.2f}ms")
        
        # Test 2: Get user by email (should use index)
        if users:
            start = time.time()
            user = TutorialUser.query.filter_by(email=users[0].email).first()
            elapsed = (time.time() - start) * 1000
            print(f"✓ Query user by email: {elapsed:.2f}ms")
        
        # Test 3: Get user enrollments
        start = time.time()
        enrollments = TutorialEnrollment.query.filter_by(user_id=users[0].id if users else 1).all()
        elapsed = (time.time() - start) * 1000
        print(f"✓ Query user enrollments: {len(enrollments)} enrollments in {elapsed:.2f}ms")
        
        profiler.print_report()


def test_catalog_query_performance():
    """Test course catalog query performance."""
    app = create_app()
    profiler = QueryProfiler()
    
    with app.app_context():
        profiler.start_profiling()
        
        print("\n📚 Testing Catalog Query Performance...")
        
        # Test 1: Get all published tutorials
        start = time.time()
        tutorials = NewTutorial.query.filter_by(status='published').all()
        elapsed = (time.time() - start) * 1000
        print(f"✓ Query published tutorials: {len(tutorials)} tutorials in {elapsed:.2f}ms")
        
        # Test 2: Filter by course type (should use index)
        start = time.time()
        python_courses = NewTutorial.query.filter_by(status='published', course_type='python').all()
        elapsed = (time.time() - start) * 1000
        print(f"✓ Query Python courses: {len(python_courses)} courses in {elapsed:.2f}ms")
        
        # Test 3: Filter by category
        start = time.time()
        beginner_courses = NewTutorial.query.filter_by(
            status='published',
            difficulty_level='beginner'
        ).all()
        elapsed = (time.time() - start) * 1000
        print(f"✓ Query beginner courses: {len(beginner_courses)} courses in {elapsed:.2f}ms")
        
        # Test 4: Featured courses
        start = time.time()
        featured = NewTutorial.query.filter_by(status='published', is_featured=True).all()
        elapsed = (time.time() - start) * 1000
        print(f"✓ Query featured courses: {len(featured)} courses in {elapsed:.2f}ms")
        
        profiler.print_report()


def test_enrollment_query_performance():
    """Test enrollment-related query performance."""
    app = create_app()
    profiler = QueryProfiler()
    
    with app.app_context():
        profiler.start_profiling()
        
        print("\n🎓 Testing Enrollment Query Performance...")
        
        # Test 1: Get all active enrollments
        start = time.time()
        enrollments = TutorialEnrollment.query.filter_by(status='active').all()
        elapsed = (time.time() - start) * 1000
        print(f"✓ Query active enrollments: {len(enrollments)} enrollments in {elapsed:.2f}ms")
        
        # Test 2: Get user progress
        if enrollments:
            start = time.time()
            progress = LessonProgress.query.filter_by(
                enrollment_id=enrollments[0].id
            ).all()
            elapsed = (time.time() - start) * 1000
            print(f"✓ Query lesson progress: {len(progress)} records in {elapsed:.2f}ms")
        
        profiler.print_report()


def test_n_plus_one_queries():
    """Detect N+1 query problems."""
    app = create_app()
    profiler = QueryProfiler()
    
    with app.app_context():
        profiler.start_profiling()
        
        print("\n🔍 Testing for N+1 Query Problems...")
        
        # Potential N+1: Getting tutorials with lessons
        start = time.time()
        tutorials = NewTutorial.query.filter_by(status='published').limit(5).all()
        query_count_after_tutorials = len(profiler.queries)
        
        for tutorial in tutorials:
            # This will trigger additional queries if not eager loaded
            _ = tutorial.lessons.all()
        
        elapsed = (time.time() - start) * 1000
        query_count_after_lessons = len(profiler.queries)
        additional_queries = query_count_after_lessons - query_count_after_tutorials
        
        print(f"✓ Loaded {len(tutorials)} tutorials with lessons in {elapsed:.2f}ms")
        print(f"  Initial queries: {query_count_after_tutorials}")
        print(f"  Additional queries for lessons: {additional_queries}")
        
        if additional_queries > 1:
            print(f"⚠️  N+1 PROBLEM DETECTED: {additional_queries} additional queries!")
            print("   Recommendation: Use eager loading with joinedload() or selectinload()")
        
        profiler.print_report()


def run_full_performance_suite():
    """Run complete performance test suite."""
    print("\n" + "="*80)
    print("PHASE 9.1 - DATABASE PERFORMANCE BASELINE")
    print("="*80)
    
    test_user_query_performance()
    test_catalog_query_performance()
    test_enrollment_query_performance()
    test_n_plus_one_queries()
    
    print("\n✅ Performance baseline testing complete!")
    print("\n📋 Next Steps:")
    print("   1. Review slow queries (>100ms)")
    print("   2. Add missing indexes on foreign keys")
    print("   3. Add indexes on frequently filtered columns")
    print("   4. Implement eager loading for N+1 problems")
    print("   5. Re-run tests to measure improvements\n")


if __name__ == '__main__':
    run_full_performance_suite()
