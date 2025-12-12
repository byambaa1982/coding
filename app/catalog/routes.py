# app/catalog/routes.py
"""Catalog routes for course browsing."""

from flask import render_template, request, abort, redirect, url_for
from app.catalog import catalog_bp
from app.models import NewTutorial, Lesson
from app.extensions import db
from sqlalchemy import or_, func
from app.cache import cached, get_cached_course_catalog, cache_course_catalog, invalidate_cache


@catalog_bp.route('/')
def index():
    """Course catalog index with filtering."""
    page = request.args.get('page', 1, type=int)
    course_type = request.args.get('type', None)
    difficulty = request.args.get('difficulty', None)
    category = request.args.get('category', None)
    search = request.args.get('search', None)
    sort = request.args.get('sort', 'newest')
    
    # Try to use cached data for common queries (no search/filters on page 1)
    cache_key = f"catalog:page{page}:{course_type}:{difficulty}:{category}:{search}:{sort}"
    
    # Base query - only published courses
    query = NewTutorial.query.filter_by(status='published')
    
    # Apply filters
    if course_type:
        query = query.filter_by(course_type=course_type)
    
    if difficulty:
        query = query.filter_by(difficulty_level=difficulty)
    
    if category:
        query = query.filter_by(category=category)
    
    # Search
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            or_(
                NewTutorial.title.ilike(search_term),
                NewTutorial.description.ilike(search_term),
                NewTutorial.tags.ilike(search_term)
            )
        )
    
    # Sorting
    if sort == 'newest':
        query = query.order_by(NewTutorial.published_at.desc())
    elif sort == 'oldest':
        query = query.order_by(NewTutorial.published_at.asc())
    elif sort == 'price_low':
        query = query.order_by(NewTutorial.price.asc())
    elif sort == 'price_high':
        query = query.order_by(NewTutorial.price.desc())
    elif sort == 'popular':
        query = query.order_by(NewTutorial.enrollment_count.desc())
    else:
        query = query.order_by(NewTutorial.created_at.desc())
    
    tutorials = query.paginate(page=page, per_page=12, error_out=False)
    
    # Get counts for filtering UI (cached for 10 minutes)
    python_count = get_cached_catalog_count('python') or cache_catalog_count('python')
    sql_count = get_cached_catalog_count('sql') or cache_catalog_count('sql')
    
    # Get unique categories (cached)
    categories = get_cached_categories() or cache_categories()
    
    return render_template('catalog/index.html',
                         tutorials=tutorials,
                         python_count=python_count,
                         sql_count=sql_count,
                         categories=categories,
                         current_type=course_type,
                         current_difficulty=difficulty,
                         current_category=category,
                         search_term=search,
                         current_sort=sort)


def get_cached_catalog_count(course_type):
    """Get cached course count."""
    from app.cache import cache_manager
    return cache_manager.get(f'catalog:count:{course_type}')


def cache_catalog_count(course_type):
    """Cache course count for 10 minutes."""
    from app.cache import cache_manager
    count = NewTutorial.query.filter_by(status='published', course_type=course_type).count()
    cache_manager.set(f'catalog:count:{course_type}', count, timeout=600)
    return count


def get_cached_categories():
    """Get cached categories list."""
    from app.cache import cache_manager
    return cache_manager.get('catalog:categories')


def cache_categories():
    """Cache categories list for 10 minutes."""
    from app.cache import cache_manager
    categories = db.session.query(NewTutorial.category).filter_by(status='published').distinct().all()
    categories = [cat[0] for cat in categories]
    cache_manager.set('catalog:categories', categories, timeout=600)
    return categories


@catalog_bp.route('/python')
def python_courses():
    """Python courses landing page."""
    page = request.args.get('page', 1, type=int)
    difficulty = request.args.get('difficulty', None)
    
    query = NewTutorial.query.filter_by(status='published', course_type='python')
    
    if difficulty:
        query = query.filter_by(difficulty_level=difficulty)
    
    tutorials = query.order_by(NewTutorial.published_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Get featured Python courses (cached for 30 minutes)
    featured = get_cached_featured('python') or cache_featured('python')
    
    return render_template('catalog/python.html',
                         tutorials=tutorials,
                         featured=featured,
                         current_difficulty=difficulty)


def get_cached_featured(course_type):
    """Get cached featured courses."""
    from app.cache import cache_manager
    return cache_manager.get(f'catalog:featured:{course_type}')


def cache_featured(course_type):
    """Cache featured courses for 30 minutes."""
    from app.cache import cache_manager
    featured = NewTutorial.query.filter_by(
        status='published',
        course_type=course_type,
        is_featured=True
    ).limit(6).all()
    cache_manager.set(f'catalog:featured:{course_type}', featured, timeout=1800)
    return featured


@catalog_bp.route('/sql')
def sql_courses():
    """SQL courses landing page."""
    page = request.args.get('page', 1, type=int)
    difficulty = request.args.get('difficulty', None)
    
    query = NewTutorial.query.filter_by(status='published', course_type='sql')
    
    if difficulty:
        query = query.filter_by(difficulty_level=difficulty)
    
    tutorials = query.order_by(NewTutorial.published_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Get featured SQL courses
    featured = NewTutorial.query.filter_by(
        status='published', 
        course_type='sql', 
        is_featured=True
    ).limit(3).all()
    
    return render_template('catalog/sql.html',
                         tutorials=tutorials,
                         featured=featured,
                         current_difficulty=difficulty)


@catalog_bp.route('/course/<slug>')
def course_detail(slug):
    """Course detail page with curriculum."""
    from flask_login import current_user
    from app.models import TutorialEnrollment
    
    tutorial = NewTutorial.query.filter_by(slug=slug, status='published').first_or_404()
    
    # Check if user is enrolled
    is_enrolled = False
    if current_user.is_authenticated:
        enrollment = TutorialEnrollment.query.filter_by(
            user_id=current_user.id,
            tutorial_id=tutorial.id,
            status='active'
        ).first()
        is_enrolled = enrollment is not None
    
    # Get lessons organized by section
    lessons = Lesson.query.filter_by(tutorial_id=tutorial.id).order_by(Lesson.order_index).all()
    
    # Organize lessons by section
    sections = {}
    for lesson in lessons:
        section = lesson.section_name or 'Introduction'
        if section not in sections:
            sections[section] = []
        sections[section].append(lesson)
    
    # Get related courses (same type and category)
    related = NewTutorial.query.filter(
        NewTutorial.id != tutorial.id,
        NewTutorial.status == 'published',
        NewTutorial.course_type == tutorial.course_type,
        NewTutorial.category == tutorial.category
    ).limit(3).all()
    
    return render_template('catalog/course_detail.html',
                         tutorial=tutorial,
                         sections=sections,
                         lessons=lessons,
                         related=related,
                         is_enrolled=is_enrolled)


@catalog_bp.route('/search')
def search():
    """Advanced search page."""
    query_text = request.args.get('q', '')
    course_type = request.args.get('type', None)
    difficulty = request.args.get('difficulty', None)
    page = request.args.get('page', 1, type=int)
    
    if not query_text:
        return redirect(url_for('catalog.index'))
    
    # Build search query
    query = NewTutorial.query.filter_by(status='published')
    
    search_term = f'%{query_text}%'
    query = query.filter(
        or_(
            NewTutorial.title.ilike(search_term),
            NewTutorial.description.ilike(search_term),
            NewTutorial.short_description.ilike(search_term),
            NewTutorial.tags.ilike(search_term),
            NewTutorial.category.ilike(search_term)
        )
    )
    
    if course_type:
        query = query.filter_by(course_type=course_type)
    
    if difficulty:
        query = query.filter_by(difficulty_level=difficulty)
    
    tutorials = query.order_by(NewTutorial.published_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('catalog/search.html',
                         tutorials=tutorials,
                         query=query_text,
                         current_type=course_type,
                         current_difficulty=difficulty)
