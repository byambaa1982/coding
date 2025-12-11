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


class TutorialEnrollment(db.Model):
    """Enrollment model for user course access."""
    
    __tablename__ = 'tutorial_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False,
                     default=lambda: str(uuid.uuid4()), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tutorial_users.id'), nullable=False)
    tutorial_id = db.Column(db.Integer, db.ForeignKey('new_tutorials.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('tutorial_orders.id'), nullable=True)
    
    # Enrollment status
    status = db.Column(db.String(20), nullable=False, default='active', index=True)
    enrollment_type = db.Column(db.String(20), nullable=False, default='paid')  # 'paid', 'free', 'gifted'
    
    # Progress tracking
    progress_percentage = db.Column(db.Numeric(5, 2), default=0.00)
    lessons_completed = db.Column(db.Integer, default=0)
    exercises_completed = db.Column(db.Integer, default=0)
    last_accessed_lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=True)
    
    # Completion
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    certificate_issued = db.Column(db.Boolean, default=False)
    
    # Timestamps
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime, nullable=True)  # For time-limited access
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('TutorialUser', backref=db.backref('enrollments', lazy='dynamic'))
    tutorial = db.relationship('NewTutorial', backref=db.backref('enrollments', lazy='dynamic'))
    last_accessed_lesson = db.relationship('Lesson', foreign_keys=[last_accessed_lesson_id])
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'tutorial_id', name='unique_user_tutorial_enrollment'),
    )
    
    def __repr__(self):
        return f'<TutorialEnrollment User:{self.user_id} Tutorial:{self.tutorial_id}>'


class TutorialOrder(db.Model):
    """Order model for course purchases."""
    
    __tablename__ = 'tutorial_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False,
                     default=lambda: str(uuid.uuid4()), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tutorial_users.id'), nullable=False)
    
    # Order details
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    
    # Pricing
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), default=0.00)
    tax_amount = db.Column(db.Numeric(10, 2), default=0.00)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # Discount/Coupon
    coupon_code = db.Column(db.String(50), nullable=True)
    coupon_discount_percentage = db.Column(db.Numeric(5, 2), nullable=True)
    
    # Stripe payment details
    stripe_payment_intent_id = db.Column(db.String(255), unique=True, nullable=True, index=True)
    stripe_checkout_session_id = db.Column(db.String(255), unique=True, nullable=True, index=True)
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    payment_method = db.Column(db.String(50), default='stripe')
    
    # Billing information
    billing_name = db.Column(db.String(200), nullable=True)
    billing_email = db.Column(db.String(255), nullable=True)
    billing_address = db.Column(db.Text, nullable=True)  # JSON string
    
    # Invoice
    invoice_url = db.Column(db.String(500), nullable=True)
    receipt_url = db.Column(db.String(500), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    refunded_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('TutorialUser', backref=db.backref('orders', lazy='dynamic'))
    items = db.relationship('TutorialOrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    enrollments = db.relationship('TutorialEnrollment', backref='order', lazy='dynamic')
    
    def __repr__(self):
        return f'<TutorialOrder {self.order_number}>'
    
    @staticmethod
    def generate_order_number():
        """Generate unique order number."""
        import random
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        random_part = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return f'ORD-{timestamp}-{random_part}'


class TutorialOrderItem(db.Model):
    """Order item model for individual course purchases."""
    
    __tablename__ = 'tutorial_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('tutorial_orders.id'), nullable=False)
    tutorial_id = db.Column(db.Integer, db.ForeignKey('new_tutorials.id'), nullable=False)
    
    # Item details
    tutorial_title = db.Column(db.String(300), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tutorial = db.relationship('NewTutorial', backref='order_items')
    
    def __repr__(self):
        return f'<TutorialOrderItem {self.tutorial_title}>'


class Coupon(db.Model):
    """Coupon/Discount code model."""
    
    __tablename__ = 'tutorial_coupons'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Discount details
    discount_type = db.Column(db.String(20), nullable=False, default='percentage')  # 'percentage', 'fixed'
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    max_discount_amount = db.Column(db.Numeric(10, 2), nullable=True)  # For percentage discounts
    
    # Usage limits
    max_uses = db.Column(db.Integer, nullable=True)  # Null = unlimited
    times_used = db.Column(db.Integer, default=0)
    max_uses_per_user = db.Column(db.Integer, default=1)
    
    # Validity
    valid_from = db.Column(db.DateTime, nullable=True)
    valid_until = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Restrictions
    min_purchase_amount = db.Column(db.Numeric(10, 2), nullable=True)
    applicable_course_types = db.Column(db.String(100), nullable=True)  # 'python', 'sql', 'all'
    specific_tutorial_ids = db.Column(db.Text, nullable=True)  # JSON array
    
    # Metadata
    description = db.Column(db.String(500), nullable=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('tutorial_users.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Coupon {self.code}>'
    
    def is_valid(self, user_id=None, cart_total=0, tutorial_ids=None):
        """Check if coupon is valid for use."""
        now = datetime.utcnow()
        
        # Check if active
        if not self.is_active:
            return False, "Coupon is not active"
        
        # Check date validity
        if self.valid_from and now < self.valid_from:
            return False, "Coupon is not yet valid"
        if self.valid_until and now > self.valid_until:
            return False, "Coupon has expired"
        
        # Check usage limits
        if self.max_uses and self.times_used >= self.max_uses:
            return False, "Coupon has reached maximum uses"
        
        # Check minimum purchase
        if self.min_purchase_amount and cart_total < float(self.min_purchase_amount):
            return False, f"Minimum purchase of ${self.min_purchase_amount} required"
        
        # Check per-user usage (would need additional query)
        if user_id and self.max_uses_per_user:
            uses_by_user = TutorialOrder.query.filter_by(
                user_id=user_id,
                coupon_code=self.code,
                status='completed'
            ).count()
            if uses_by_user >= self.max_uses_per_user:
                return False, "You have already used this coupon"
        
        return True, "Coupon is valid"
    
    def calculate_discount(self, amount):
        """Calculate discount amount."""
        if self.discount_type == 'percentage':
            discount = amount * (float(self.discount_value) / 100)
            if self.max_discount_amount:
                discount = min(discount, float(self.max_discount_amount))
            return round(discount, 2)
        else:  # fixed
            return min(float(self.discount_value), amount)


class Wishlist(db.Model):
    """Wishlist model for saved courses."""
    
    __tablename__ = 'tutorial_wishlists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tutorial_users.id'), nullable=False)
    tutorial_id = db.Column(db.Integer, db.ForeignKey('new_tutorials.id'), nullable=False)
    
    # Timestamps
    added_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = db.relationship('TutorialUser', backref=db.backref('wishlist_items', lazy='dynamic'))
    tutorial = db.relationship('NewTutorial', backref=db.backref('wishlisted_by', lazy='dynamic'))
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'tutorial_id', name='unique_user_tutorial_wishlist'),
    )
    
    def __repr__(self):
        return f'<Wishlist User:{self.user_id} Tutorial:{self.tutorial_id}>'


class LessonProgress(db.Model):
    """Lesson progress tracking model."""
    
    __tablename__ = 'lesson_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tutorial_users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('tutorial_enrollments.id'), nullable=False)
    
    # Progress tracking
    is_completed = db.Column(db.Boolean, default=False)
    completion_percentage = db.Column(db.Numeric(5, 2), default=0.00)
    time_spent_seconds = db.Column(db.Integer, default=0)
    
    # Video progress (for video lessons)
    video_position_seconds = db.Column(db.Integer, default=0)
    video_watched_percentage = db.Column(db.Numeric(5, 2), default=0.00)
    
    # Bookmarks
    is_bookmarked = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    first_accessed_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('TutorialUser', backref=db.backref('lesson_progress', lazy='dynamic'))
    lesson = db.relationship('Lesson', backref=db.backref('progress_records', lazy='dynamic'))
    enrollment = db.relationship('TutorialEnrollment', backref=db.backref('lesson_progress', lazy='dynamic'))
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'lesson_id', name='unique_user_lesson_progress'),
    )
    
    def __repr__(self):
        return f'<LessonProgress User:{self.user_id} Lesson:{self.lesson_id}>'
    
    def mark_complete(self):
        """Mark lesson as complete and update enrollment progress."""
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = datetime.utcnow()
            self.completion_percentage = 100.00
            
            # Update enrollment progress
            enrollment = self.enrollment
            if enrollment:
                total_lessons = enrollment.tutorial.total_lessons
                if total_lessons > 0:
                    enrollment.lessons_completed += 1
                    enrollment.progress_percentage = (enrollment.lessons_completed / total_lessons) * 100
                    enrollment.last_accessed_lesson_id = self.lesson_id
                    
                    # Check if tutorial is completed
                    if enrollment.lessons_completed >= total_lessons:
                        enrollment.is_completed = True
                        enrollment.completed_at = datetime.utcnow()
            
            db.session.commit()


class Quiz(db.Model):
    """Quiz model for assessments."""
    
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    tutorial_id = db.Column(db.Integer, db.ForeignKey('new_tutorials.id'), nullable=False)
    
    # Quiz info
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Settings
    passing_score = db.Column(db.Numeric(5, 2), default=70.00)
    time_limit_minutes = db.Column(db.Integer, nullable=True)  # Null = no limit
    max_attempts = db.Column(db.Integer, default=3)
    shuffle_questions = db.Column(db.Boolean, default=True)
    shuffle_options = db.Column(db.Boolean, default=True)
    show_correct_answers = db.Column(db.Boolean, default=True)
    
    # Organization
    order_index = db.Column(db.Integer, default=0)
    is_required = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lesson = db.relationship('Lesson', backref=db.backref('quizzes', lazy='dynamic'))
    tutorial = db.relationship('NewTutorial', backref=db.backref('quizzes', lazy='dynamic'))
    questions = db.relationship('QuizQuestion', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Quiz {self.title}>'


class QuizQuestion(db.Model):
    """Quiz question model."""
    
    __tablename__ = 'quiz_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    
    # Question info
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default='multiple_choice')  # 'multiple_choice', 'true_false', 'text'
    
    # Options (JSON array for multiple choice)
    options = db.Column(db.Text, nullable=True)  # JSON: [{"id": "a", "text": "Option A"}, ...]
    correct_answer = db.Column(db.Text, nullable=False)  # "a" for MC, "true"/"false" for T/F, text for text
    
    # Metadata
    explanation = db.Column(db.Text, nullable=True)
    points = db.Column(db.Integer, default=1)
    order_index = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<QuizQuestion {self.id}>'


class QuizAttempt(db.Model):
    """Quiz attempt model for tracking user quiz submissions."""
    
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tutorial_users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('tutorial_enrollments.id'), nullable=False)
    
    # Attempt info
    attempt_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='in_progress')  # 'in_progress', 'completed', 'abandoned'
    
    # Scoring
    score = db.Column(db.Numeric(5, 2), nullable=True)
    max_score = db.Column(db.Integer, nullable=True)
    passed = db.Column(db.Boolean, default=False)
    
    # Timing
    time_taken_seconds = db.Column(db.Integer, nullable=True)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('TutorialUser', backref=db.backref('quiz_attempts', lazy='dynamic'))
    quiz = db.relationship('Quiz', backref=db.backref('attempts', lazy='dynamic'))
    enrollment = db.relationship('TutorialEnrollment', backref=db.backref('quiz_attempts', lazy='dynamic'))
    answers = db.relationship('QuizAnswer', backref='attempt', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<QuizAttempt User:{self.user_id} Quiz:{self.quiz_id} #{self.attempt_number}>'
    
    def calculate_score(self):
        """Calculate and update score based on answers."""
        total_points = 0
        earned_points = 0
        
        for answer in self.answers:
            question = answer.question
            total_points += question.points
            if answer.is_correct:
                earned_points += question.points
        
        self.max_score = total_points
        if total_points > 0:
            self.score = (earned_points / total_points) * 100
            self.passed = self.score >= float(self.quiz.passing_score)
        else:
            self.score = 0
            self.passed = False
        
        db.session.commit()


class QuizAnswer(db.Model):
    """Quiz answer model for tracking user responses."""
    
    __tablename__ = 'quiz_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'), nullable=False)
    
    # Answer info
    user_answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    
    # Timestamps
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    question = db.relationship('QuizQuestion', backref=db.backref('answers', lazy='dynamic'))
    
    def __repr__(self):
        return f'<QuizAnswer Attempt:{self.attempt_id} Question:{self.question_id}>'
