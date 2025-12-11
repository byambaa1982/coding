# app/models.py
"""Database models for Tutorial E-Commerce Platform.

IMPORTANT: Using different table names to avoid conflicts with existing database:
- 'tutorial_users' instead of 'users' or 'accounts'
- 'tutorials' instead of 'courses'
- All tables prefixed with 'tutorial_' or 'tut_'
"""

import uuid
from datetime import datetime, timedelta
from flask_login import UserMixin
from app.extensions import db, bcrypt


class TutorialUser(UserMixin, db.Model):
    """User model for tutorial platform (different from existing 'accounts' table)."""
    
    __tablename__ = 'tutorial_users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, 
                     default=lambda: str(uuid.uuid4()), index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=True)
    full_name = db.Column(db.String(200), nullable=True)
    
    # Status flags
    email_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_instructor = db.Column(db.Boolean, default=False)
    
    # Profile
    bio = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Security
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships (will be added in later phases)
    # enrollments = db.relationship('TutorialEnrollment', backref='user', lazy='dynamic')
    # orders = db.relationship('TutorialOrder', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<TutorialUser {self.email}>'
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches hash."""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_locked(self):
        """Check if account is locked."""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def increment_failed_login(self):
        """Increment failed login attempts and lock if needed."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
    
    def reset_failed_login(self):
        """Reset failed login attempts."""
        self.failed_login_attempts = 0
        self.locked_until = None
        db.session.commit()
    
    def get_id(self):
        """Return user ID for Flask-Login."""
        return str(self.id)


class NewTutorial(db.Model):
    """Tutorial/Course model - New table for Phase 2."""
    
    __tablename__ = 'new_tutorials'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, 
                     default=lambda: str(uuid.uuid4()), index=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('tutorial_users.id'), nullable=False)
    
    # Tutorial info
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(350), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(500), nullable=True)
    
    # Content
    thumbnail_url = db.Column(db.String(500), nullable=True)
    preview_video_url = db.Column(db.String(500), nullable=True)
    difficulty_level = db.Column(db.String(20), nullable=False, default='beginner')
    language = db.Column(db.String(50), default='en')
    
    # Categorization
    course_type = db.Column(db.String(50), nullable=False, default='python', index=True)  # 'python' or 'sql'
    category = db.Column(db.String(100), nullable=False, index=True)
    tags = db.Column(db.Text, nullable=True)  # JSON string
    
    # Pricing
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    currency = db.Column(db.String(3), default='USD')
    is_free = db.Column(db.Boolean, default=False)
    
    # Status
    status = db.Column(db.String(20), nullable=False, default='draft', index=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Metadata
    estimated_duration_hours = db.Column(db.Numeric(5, 2), nullable=True)
    total_lessons = db.Column(db.Integer, default=0)
    enrollment_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    instructor = db.relationship('TutorialUser', backref='tutorials_created')
    
    def __repr__(self):
        return f'<NewTutorial {self.title}>'


class PasswordReset(db.Model):
    """Password reset token model."""
    
    __tablename__ = 'tutorial_password_resets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tutorial_users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('TutorialUser', backref='password_resets')
    
    def is_valid(self):
        """Check if token is still valid."""
        return not self.used and self.expires_at > datetime.utcnow()
    
    def __repr__(self):
        return f'<PasswordReset {self.token}>'


class Lesson(db.Model):
    """Lesson model for tutorials."""
    
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    tutorial_id = db.Column(db.Integer, db.ForeignKey('new_tutorials.id'), nullable=False)
    
    # Lesson info
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(350), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Content
    content_type = db.Column(db.String(20), nullable=False, default='text')  # 'text', 'video', 'quiz'
    content = db.Column(db.Text, nullable=True)  # Text content or video URL
    video_url = db.Column(db.String(500), nullable=True)
    video_duration_seconds = db.Column(db.Integer, nullable=True)
    
    # Organization
    section_name = db.Column(db.String(200), nullable=True)  # For grouping lessons
    order_index = db.Column(db.Integer, nullable=False, default=0)
    
    # Metadata
    is_free_preview = db.Column(db.Boolean, default=False)
    estimated_duration_minutes = db.Column(db.Integer, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tutorial = db.relationship('NewTutorial', backref=db.backref('lessons', lazy='dynamic', order_by='Lesson.order_index'))
    
    def __repr__(self):
        return f'<Lesson {self.title}>'


class Exercise(db.Model):
    """Exercise model for practice problems."""
    
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    tutorial_id = db.Column(db.Integer, db.ForeignKey('new_tutorials.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=True)
    
    # Exercise info
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(350), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Exercise type and content
    exercise_type = db.Column(db.String(20), nullable=False, index=True)  # 'python', 'sql'
    difficulty = db.Column(db.String(20), nullable=False, default='easy')  # 'easy', 'medium', 'hard'
    
    # Code/Query setup
    starter_code = db.Column(db.Text, nullable=True)
    solution_code = db.Column(db.Text, nullable=True)
    test_cases = db.Column(db.Text, nullable=True)  # JSON string
    hints = db.Column(db.Text, nullable=True)  # JSON array
    
    # SQL-specific
    database_schema = db.Column(db.Text, nullable=True)  # DDL for SQL exercises
    sample_data = db.Column(db.Text, nullable=True)  # INSERT statements
    
    # Organization
    order_index = db.Column(db.Integer, nullable=False, default=0)
    points = db.Column(db.Integer, default=10)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tutorial = db.relationship('NewTutorial', backref=db.backref('exercises', lazy='dynamic'))
    lesson = db.relationship('Lesson', backref=db.backref('exercises', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Exercise {self.title}>'
