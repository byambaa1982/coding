# app/catalog/routes.py
"""Catalog routes for course browsing."""

from flask import render_template, request, abort, redirect, url_for
from app.catalog import catalog_bp
from app.models import NewTutorial, Lesson
from app.extensions import db
from sqlalchemy import or_, func


@catalog_bp.route('/')
def index():
    """Course catalog index with filtering."""
    page = request.args.get('page', 1, type=int)
    course_type = request.args.get('type', None)
    difficulty = request.args.get('difficulty', None)
    category = request.args.get('category', None)
    search = request.args.get('search', None)
    sort = request.args.get('sort', 'newest')
    
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
    
    # Get counts for filtering UI
    python_count = NewTutorial.query.filter_by(status='published', course_type='python').count()
    sql_count = NewTutorial.query.filter_by(status='published', course_type='sql').count()
    
    # Get unique categories
    categories = db.session.query(NewTutorial.category).filter_by(status='published').distinct().all()
    categories = [cat[0] for cat in categories]
    
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
    
    # Get featured Python courses
    featured = NewTutorial.query.filter_by(
        status='published', 
        course_type='python', 
        is_featured=True
    ).limit(3).all()
    
    return render_template('catalog/python.html',
                         tutorials=tutorials,
                         featured=featured,
                         current_difficulty=difficulty)


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
