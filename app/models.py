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
    test_cases = db.Column(db.Text, nullable=True)  # JSON string for Python test cases
    hints = db.Column(db.Text, nullable=True)  # JSON array
    expected_output = db.Column(db.Text, nullable=True)  # JSON for expected results (SQL exercises)
    
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


class ExerciseSubmission(db.Model):
    """Exercise submission model for tracking code execution results."""
    
    __tablename__ = 'exercise_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tutorial_users.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('tutorial_enrollments.id'), nullable=True)
    
    # Submission info
    submitted_code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20), default='python')  # 'python' or 'sql'
    
    # Execution results
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)  # 'pending', 'passed', 'failed', 'error', 'timeout'
    output = db.Column(db.Text, nullable=True)  # stdout
    error_message = db.Column(db.Text, nullable=True)  # stderr or exception
    test_results = db.Column(db.Text, nullable=True)  # JSON: test case results
    
    # Scoring
    tests_passed = db.Column(db.Integer, default=0)
    tests_failed = db.Column(db.Integer, default=0)
    score = db.Column(db.Numeric(5, 2), default=0.00)
    
    # Performance metrics
    execution_time_ms = db.Column(db.Integer, nullable=True)
    memory_used_mb = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Security & validation
    is_flagged = db.Column(db.Boolean, default=False)  # Flagged for suspicious code
    flagged_reason = db.Column(db.String(500), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    
    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    executed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('TutorialUser', backref=db.backref('exercise_submissions', lazy='dynamic'))
    exercise = db.relationship('Exercise', backref=db.backref('submissions', lazy='dynamic'))
    enrollment = db.relationship('TutorialEnrollment', backref=db.backref('exercise_submissions', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ExerciseSubmission User:{self.user_id} Exercise:{self.exercise_id} Status:{self.status}>'
    
    def mark_as_passed(self):
        """Mark submission as passed and update enrollment progress."""
        if self.status == 'passed' and self.enrollment:
            # Check if this is the first successful submission for this exercise
            previous_success = ExerciseSubmission.query.filter(
                ExerciseSubmission.user_id == self.user_id,
                ExerciseSubmission.exercise_id == self.exercise_id,
                ExerciseSubmission.status == 'passed',
                ExerciseSubmission.id < self.id
            ).first()
            
            if not previous_success:
                # First time passing this exercise, increment count
                self.enrollment.exercises_completed += 1
                db.session.commit()


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


class Certificate(db.Model):
    """Certificate model for course completion certificates."""
    
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False,
                     default=lambda: str(uuid.uuid4()), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tutorial_users.id'), nullable=False)
    tutorial_id = db.Column(db.Integer, db.ForeignKey('new_tutorials.id'), nullable=False)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('tutorial_enrollments.id'), nullable=False)
    
    # Certificate details
    certificate_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    issued_to_name = db.Column(db.String(200), nullable=False)
    tutorial_title = db.Column(db.String(300), nullable=False)
    instructor_name = db.Column(db.String(200), nullable=True)
    
    # File storage
    pdf_url = db.Column(db.String(500), nullable=True)
    pdf_path = db.Column(db.String(500), nullable=True)
    
    # Verification
    verification_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    is_revoked = db.Column(db.Boolean, default=False)
    revoked_reason = db.Column(db.String(500), nullable=True)
    
    # Metadata
    completion_date = db.Column(db.Date, nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('TutorialUser', backref=db.backref('certificates', lazy='dynamic'))
    tutorial = db.relationship('NewTutorial', backref=db.backref('certificates', lazy='dynamic'))
    enrollment = db.relationship('TutorialEnrollment', backref='certificate', uselist=False)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'tutorial_id', name='unique_user_tutorial_certificate'),
    )
    
    def __repr__(self):
        return f'<Certificate {self.certificate_number}>'
    
    @staticmethod
    def generate_certificate_number():
        """Generate unique certificate number."""
        import random
        timestamp = datetime.utcnow().strftime('%Y%m')
        random_part = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return f'CERT-{timestamp}-{random_part}'
    
    @staticmethod
    def generate_verification_code():
        """Generate unique verification code."""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class Review(db.Model):
    """Review/Rating model for tutorials."""
    
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tutorial_users.id'), nullable=False)
    tutorial_id = db.Column(db.Integer, db.ForeignKey('new_tutorials.id'), nullable=False)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('tutorial_enrollments.id'), nullable=True)
    
    # Review details
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    title = db.Column(db.String(200), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    
    # Additional ratings
    content_quality = db.Column(db.Integer, nullable=True)  # 1-5
    instructor_quality = db.Column(db.Integer, nullable=True)  # 1-5
    value_for_money = db.Column(db.Integer, nullable=True)  # 1-5
    
    # Moderation
    is_verified_purchase = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Helpfulness
    helpful_count = db.Column(db.Integer, default=0)
    not_helpful_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('TutorialUser', backref=db.backref('reviews', lazy='dynamic'))
    tutorial = db.relationship('NewTutorial', backref=db.backref('reviews', lazy='dynamic'))
    enrollment = db.relationship('TutorialEnrollment', backref=db.backref('reviews', lazy='dynamic'))
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'tutorial_id', name='unique_user_tutorial_review'),
    )
    
    def __repr__(self):
        return f'<Review User:{self.user_id} Tutorial:{self.tutorial_id} Rating:{self.rating}>'


class Achievement(db.Model):
    """Achievement/Badge definition model."""
    
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Achievement details
    name = db.Column(db.String(200), unique=True, nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    icon_url = db.Column(db.String(500), nullable=True)
    icon_class = db.Column(db.String(100), nullable=True)  # CSS class for icon
    
    # Achievement criteria
    achievement_type = db.Column(db.String(50), nullable=False, index=True)  # 'first_lesson', 'complete_course', 'streak', 'exercise_master', etc.
    criteria = db.Column(db.Text, nullable=True)  # JSON: {"lessons_completed": 10, "course_type": "python"}
    points = db.Column(db.Integer, default=10)
    
    # Categorization
    category = db.Column(db.String(50), nullable=True)  # 'learning', 'social', 'mastery'
    difficulty = db.Column(db.String(20), default='bronze')  # 'bronze', 'silver', 'gold', 'platinum'
    
    # Visibility
    is_hidden = db.Column(db.Boolean, default=False)  # Secret achievements
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Achievement {self.name}>'


class UserAchievement(db.Model):
    """User achievement tracking model."""
    
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tutorial_users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    
    # Progress tracking
    progress_current = db.Column(db.Integer, default=0)
    progress_target = db.Column(db.Integer, default=1)
    is_unlocked = db.Column(db.Boolean, default=False)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    unlocked_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('TutorialUser', backref=db.backref('achievements', lazy='dynamic'))
    achievement = db.relationship('Achievement', backref=db.backref('user_achievements', lazy='dynamic'))
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),
    )
    
    def __repr__(self):
        return f'<UserAchievement User:{self.user_id} Achievement:{self.achievement_id}>'
    
    def check_and_unlock(self):
        """Check if achievement criteria is met and unlock if needed."""
        if not self.is_unlocked and self.progress_current >= self.progress_target:
            self.is_unlocked = True
            self.unlocked_at = datetime.utcnow()
            db.session.commit()
            return True
        return False


class Notification(db.Model):
    """Notification model for user alerts."""
    
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tutorial_users.id'), nullable=False)
    
    # Notification details
    notification_type = db.Column(db.String(50), nullable=False, index=True)  # 'achievement', 'certificate', 'course_update', 'reminder', etc.
    title = db.Column(db.String(300), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Action/Link
    action_url = db.Column(db.String(500), nullable=True)
    action_text = db.Column(db.String(100), nullable=True)
    
    # Status
    is_read = db.Column(db.Boolean, default=False, index=True)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Related objects (optional)
    related_type = db.Column(db.String(50), nullable=True)  # 'tutorial', 'achievement', 'certificate'
    related_id = db.Column(db.Integer, nullable=True)
    
    # Metadata
    icon_class = db.Column(db.String(100), nullable=True)
    priority = db.Column(db.String(20), default='normal')  # 'low', 'normal', 'high'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('TutorialUser', backref=db.backref('notifications', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Notification User:{self.user_id} Type:{self.notification_type}>'
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
            db.session.commit()


class LearningStreak(db.Model):
    """Learning streak tracking model."""
    
    __tablename__ = 'learning_streaks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tutorial_users.id'), nullable=False, unique=True)
    
    # Streak data
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    total_learning_days = db.Column(db.Integer, default=0)
    
    # Dates
    last_activity_date = db.Column(db.Date, nullable=True)
    streak_start_date = db.Column(db.Date, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('TutorialUser', backref='learning_streak', uselist=False)
    
    def __repr__(self):
        return f'<LearningStreak User:{self.user_id} Current:{self.current_streak}>'
    
    def update_streak(self):
        """Update streak based on current date."""
        from datetime import date
        today = date.today()
        
        if not self.last_activity_date:
            # First activity
            self.current_streak = 1
            self.longest_streak = 1
            self.total_learning_days = 1
            self.last_activity_date = today
            self.streak_start_date = today
        elif self.last_activity_date == today:
            # Already logged activity today
            return
        elif self.last_activity_date == today - timedelta(days=1):
            # Consecutive day
            self.current_streak += 1
            self.last_activity_date = today
            self.total_learning_days += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            # Streak broken
            self.current_streak = 1
            self.last_activity_date = today
            self.streak_start_date = today
            self.total_learning_days += 1
        
        db.session.commit()


class UserAnalytics(db.Model):
    """User analytics and statistics model."""
    
    __tablename__ = 'user_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tutorial_users.id'), nullable=False, unique=True)
    
    # Learning statistics
    total_learning_time_minutes = db.Column(db.Integer, default=0)
    total_courses_enrolled = db.Column(db.Integer, default=0)
    total_courses_completed = db.Column(db.Integer, default=0)
    total_lessons_completed = db.Column(db.Integer, default=0)
    total_exercises_completed = db.Column(db.Integer, default=0)
    total_quizzes_completed = db.Column(db.Integer, default=0)
    
    # Performance statistics
    average_quiz_score = db.Column(db.Numeric(5, 2), default=0.00)
    average_exercise_success_rate = db.Column(db.Numeric(5, 2), default=0.00)
    total_points_earned = db.Column(db.Integer, default=0)
    
    # Course type breakdown
    python_courses_completed = db.Column(db.Integer, default=0)
    sql_courses_completed = db.Column(db.Integer, default=0)
    python_exercises_completed = db.Column(db.Integer, default=0)
    sql_exercises_completed = db.Column(db.Integer, default=0)
    
    # Engagement metrics
    days_active = db.Column(db.Integer, default=0)
    avg_daily_time_minutes = db.Column(db.Integer, default=0)
    last_7_days_time_minutes = db.Column(db.Integer, default=0)
    last_30_days_time_minutes = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('TutorialUser', backref='analytics', uselist=False)
    
    def __repr__(self):
        return f'<UserAnalytics User:{self.user_id}>'
