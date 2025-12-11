# Phase 1: Foundation & Setup - Detailed Implementation Guide

## 📋 Overview

This guide provides step-by-step instructions for implementing Phase 1 of the E-Commerce Tutorial Platform. By the end of this phase, you will have a working Flask application with MySQL database connection, user authentication, and basic frontend templates.

**Duration:** Week 1 (5-7 days)

**Prerequisites:**
- Python 3.8+ installed
- MySQL database access (using existing PythonAnywhere database)
- Basic knowledge of Flask and MySQL

---

## 🎯 Phase 1 Goals

✅ Development environment fully configured  
✅ Flask application structure created  
✅ MySQL database connected using SSH tunnel  
✅ Database models defined with **unique table names**  
✅ Basic authentication system working  
✅ Project documentation started  

---

## 📁 Project Structure

Create the following directory structure:

```
code_tutorial/
├── app.py                          # Application entry point
├── config.py                       # Configuration settings (SSH tunnel)
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables
├── .gitignore                     # Git ignore rules
│
├── app/
│   ├── __init__.py                # App factory
│   ├── models.py                  # Database models (NEW TABLES)
│   ├── extensions.py              # Flask extensions
│   │
│   ├── auth/                      # Authentication blueprint
│   │   ├── __init__.py
│   │   ├── routes.py              # Login, register, logout
│   │   ├── forms.py               # WTForms
│   │   └── utils.py               # Auth utilities
│   │
│   ├── main/                      # Main pages blueprint
│   │   ├── __init__.py
│   │   └── routes.py              # Home, about pages
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── main.css
│   │   └── js/
│   │       └── main.js
│   │
│   └── templates/
│       ├── base.html              # Base template
│       ├── index.html             # Homepage
│       │
│       └── auth/
│           ├── login.html
│           ├── register.html
│           └── reset_password.html
│
├── migrations/                     # Database migrations
│
└── markdown/                       # Documentation
    └── setup.md
```

---

## 📝 Step-by-Step Implementation

### **Step 1: Create requirements.txt**

Create `requirements.txt` with the following dependencies:

```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
Flask-Migrate==4.0.5
Flask-Mail==0.9.1
Flask-Bcrypt==1.0.1
python-dotenv==1.0.0
sshtunnel==0.4.0
PyMySQL==1.1.0
cryptography==41.0.7
email-validator==2.1.0
WTForms==3.1.1
```

**Install dependencies:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### **Step 2: Create .env File**

Create `.env` file for environment variables (NEVER commit this file):

```env
# Flask
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_APP=app.py
FLASK_ENV=development

# MySQL/PythonAnywhere Database
SSH_HOST=ssh.pythonanywhere.com
SSH_USERNAME=byambaa1982
SSH_PASSWORD=your-ssh-password
DB_HOST=byambaa1982.mysql.pythonanywhere-services.com
DB_USER=byambaa1982
DB_PASSWORD=your-mysql-password
DB_NAME=byambaa1982$codemirror

# Mail (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@tutorial-ecommerce.com
```

**Important:** The database is shared with the existing `imageToCode` project. We will use **different table names** to avoid conflicts.

---

### **Step 3: Create config.py**

Create `config.py` to handle SSH tunnel connection (same method as imageToCode project):

```python
# config.py
"""Application configuration with SSH tunnel support."""

import os
import socket
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from sshtunnel import SSHTunnelForwarder
    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MySQL/PythonAnywhere configuration
    SSH_HOST = os.environ.get('SSH_HOST') or 'ssh.pythonanywhere.com'
    SSH_USERNAME = os.environ.get('SSH_USERNAME') or 'byambaa1982'
    SSH_PASSWORD = os.environ.get('SSH_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST') or 'byambaa1982.mysql.pythonanywhere-services.com'
    DB_USER = os.environ.get('DB_USER') or 'byambaa1982'
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME') or 'byambaa1982$codemirror'
    
    # SSH tunnel (for local development)
    _ssh_tunnel = None
    _is_on_pythonanywhere = None
    
    # Database
    SQLALCHEMY_DATABASE_URI = None  # Will be set dynamically
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_POOL_RECYCLE = 280
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@tutorial-ecommerce.com'
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Application
    APP_NAME = 'Tutorial E-Commerce Platform'
    APP_URL = os.environ.get('APP_URL') or 'http://localhost:5000'
    
    @classmethod
    def is_on_pythonanywhere(cls):
        """Check if we're running on PythonAnywhere."""
        if cls._is_on_pythonanywhere is None:
            hostname = socket.gethostname()
            cls._is_on_pythonanywhere = (
                'pythonanywhere' in hostname.lower() or
                os.getenv('PYTHONANYWHERE_SITE') is not None or
                os.path.exists('/home/byambaa1982')
            )
        return cls._is_on_pythonanywhere
    
    @classmethod
    def start_ssh_tunnel(cls):
        """Start SSH tunnel (only for local development)."""
        if not SSH_AVAILABLE:
            print("Warning: sshtunnel package not available. Install with: pip install sshtunnel")
            return None
        
        if cls._ssh_tunnel is None or not cls._ssh_tunnel.is_active:
            try:
                # Find available local port
                sock = socket.socket()
                sock.bind(('', 0))
                available_port = sock.getsockname()[1]
                sock.close()
                
                cls._ssh_tunnel = SSHTunnelForwarder(
                    (cls.SSH_HOST, 22),
                    ssh_username=cls.SSH_USERNAME,
                    ssh_password=cls.SSH_PASSWORD,
                    remote_bind_address=(cls.DB_HOST, 3306),
                    local_bind_address=('127.0.0.1', available_port),
                    allow_agent=False,
                    host_pkey_directories=[],
                    set_keepalive=30.0
                )
                
                print(f"🔄 Starting SSH tunnel on port {available_port}...")
                cls._ssh_tunnel.start()
                print(f"✅ SSH tunnel started successfully on port {available_port}")
                
                return cls._ssh_tunnel
            except Exception as e:
                print(f"❌ Failed to start SSH tunnel: {str(e)}")
                raise
        
        return cls._ssh_tunnel
    
    @classmethod
    def get_database_uri(cls):
        """Get database URI based on environment."""
        if cls.is_on_pythonanywhere():
            # Direct connection on PythonAnywhere
            uri = f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}/{cls.DB_NAME}"
            print("📡 Using direct database connection (PythonAnywhere)")
        else:
            # Use SSH tunnel for local development
            tunnel = cls.start_ssh_tunnel()
            if tunnel:
                local_bind_port = tunnel.local_bind_port
                uri = f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@127.0.0.1:{local_bind_port}/{cls.DB_NAME}"
                print(f"🔒 Using SSH tunnel connection (localhost:{local_bind_port})")
            else:
                raise Exception("Could not establish database connection")
        
        return uri
    
    @classmethod
    def init_app(cls, app):
        """Initialize app configuration."""
        # Set database URI
        app.config['SQLALCHEMY_DATABASE_URI'] = cls.get_database_uri()


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

---

### **Step 4: Create app/extensions.py**

Create `app/extensions.py` to initialize Flask extensions:

```python
# app/extensions.py
"""Flask extensions initialization."""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()

# Configure login manager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
```

---

### **Step 5: Create app/models.py**

Create `app/models.py` with **UNIQUE table names** to avoid conflicts with existing tables:

```python
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


class Tutorial(db.Model):
    """Tutorial/Course model."""
    
    __tablename__ = 'tutorials'
    
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
        return f'<Tutorial {self.title}>'


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
```

**Key Points:**
- Table names: `tutorial_users`, `tutorials`, `tutorial_password_resets`
- These names are DIFFERENT from existing `accounts` and `user` tables
- Using same database connection as imageToCode project
- Models follow same pattern as the project plan

---

### **Step 6: Create app/__init__.py (App Factory)**

Create `app/__init__.py` with the Flask app factory pattern:

```python
# app/__init__.py
"""Flask application factory."""

from flask import Flask
from config import config
from app.extensions import db, login_manager, bcrypt, migrate, mail, csrf


def create_app(config_name='development'):
    """Create and configure Flask application.
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)
    
    # User loader for Flask-Login
    from app.models import TutorialUser
    
    @login_manager.user_loader
    def load_user(user_id):
        return TutorialUser.query.get(int(user_id))
    
    # Register blueprints
    from app.auth import auth_bp
    from app.main import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app
```

---

### **Step 7: Create Authentication Blueprint**

#### Create `app/auth/__init__.py`:

```python
# app/auth/__init__.py
"""Authentication blueprint."""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from app.auth import routes
```

#### Create `app/auth/forms.py`:

```python
# app/auth/forms.py
"""Authentication forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import TutorialUser


class RegistrationForm(FlaskForm):
    """User registration form."""
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=255)
    ])
    username = StringField('Username (optional)', validators=[
        Length(max=100)
    ])
    full_name = StringField('Full Name', validators=[
        Length(max=200)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        """Check if email already exists."""
        if TutorialUser.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')
    
    def validate_username(self, field):
        """Check if username already exists."""
        if field.data and TutorialUser.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken.')


class LoginForm(FlaskForm):
    """User login form."""
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RequestPasswordResetForm(FlaskForm):
    """Request password reset form."""
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    """Reset password form."""
    
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8)
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
```

#### Create `app/auth/utils.py`:

```python
# app/auth/utils.py
"""Authentication utilities."""

import secrets
from datetime import datetime, timedelta
from flask import url_for, current_app
from flask_mail import Message
from app.extensions import db, mail
from app.models import PasswordReset


def generate_reset_token():
    """Generate secure password reset token."""
    return secrets.token_urlsafe(32)


def create_password_reset(user):
    """Create password reset token for user.
    
    Args:
        user: TutorialUser instance
    
    Returns:
        PasswordReset instance
    """
    token = generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    reset = PasswordReset(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    
    db.session.add(reset)
    db.session.commit()
    
    return reset


def send_password_reset_email(user, token):
    """Send password reset email.
    
    Args:
        user: TutorialUser instance
        token: Password reset token
    """
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    msg = Message(
        subject='Password Reset Request',
        recipients=[user.email],
        body=f'''Hi {user.full_name or user.email},

You requested a password reset for your Tutorial E-Commerce Platform account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
Tutorial E-Commerce Platform Team
'''
    )
    
    mail.send(msg)


def send_welcome_email(user):
    """Send welcome email to new user.
    
    Args:
        user: TutorialUser instance
    """
    msg = Message(
        subject='Welcome to Tutorial E-Commerce Platform',
        recipients=[user.email],
        body=f'''Hi {user.full_name or user.email},

Welcome to Tutorial E-Commerce Platform!

Your account has been created successfully. You can now browse our courses and start learning.

Login here: {url_for('auth.login', _external=True)}

Best regards,
Tutorial E-Commerce Platform Team
'''
    )
    
    mail.send(msg)
```

#### Create `app/auth/routes.py`:

```python
# app/auth/routes.py
"""Authentication routes."""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import auth_bp
from app.auth.forms import (
    RegistrationForm, LoginForm, 
    RequestPasswordResetForm, ResetPasswordForm
)
from app.auth.utils import create_password_reset, send_password_reset_email, send_welcome_email
from app.models import TutorialUser, PasswordReset
from app.extensions import db
from datetime import datetime


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = TutorialUser(
            email=form.email.data.lower(),
            username=form.username.data or None,
            full_name=form.full_name.data or None,
            email_verified=False
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Send welcome email (in production, use background task)
        try:
            send_welcome_email(user)
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = TutorialUser.query.filter_by(email=form.email.data.lower()).first()
        
        if user is None:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))
        
        if user.is_locked():
            flash('Account is locked due to multiple failed login attempts. Try again later.', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.check_password(form.password.data):
            user.increment_failed_login()
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Your account has been deactivated.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Successful login
        user.reset_failed_login()
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=form.remember_me.data)
        
        # Redirect to next page or home
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        flash('Login successful!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def request_password_reset():
    """Request password reset."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RequestPasswordResetForm()
    
    if form.validate_on_submit():
        user = TutorialUser.query.filter_by(email=form.email.data.lower()).first()
        
        if user:
            reset = create_password_reset(user)
            try:
                send_password_reset_email(user, reset.token)
                flash('Password reset instructions sent to your email.', 'info')
            except Exception as e:
                print(f"Failed to send reset email: {e}")
                flash('Failed to send reset email. Please try again.', 'danger')
        else:
            # Don't reveal if email exists
            flash('If that email exists, password reset instructions have been sent.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/request_reset.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    reset = PasswordReset.query.filter_by(token=token).first()
    
    if not reset or not reset.is_valid():
        flash('Invalid or expired password reset link.', 'danger')
        return redirect(url_for('auth.request_password_reset'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        reset.user.set_password(form.password.data)
        reset.used = True
        db.session.commit()
        
        flash('Your password has been reset. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)
```

---

### **Step 8: Create Main Blueprint**

#### Create `app/main/__init__.py`:

```python
# app/main/__init__.py
"""Main blueprint."""

from flask import Blueprint

main_bp = Blueprint('main', __name__)

from app.main import routes
```

#### Create `app/main/routes.py`:

```python
# app/main/routes.py
"""Main routes."""

from flask import render_template
from flask_login import current_user
from app.main import main_bp


@main_bp.route('/')
def index():
    """Homepage."""
    return render_template('index.html')


@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')
```

---

### **Step 9: Create Templates**

#### Create `app/templates/base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Tutorial E-Commerce Platform{% endblock %}</title>
    
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    
    {% block extra_css %}{% endblock %}
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-lg">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex">
                    <div class="flex-shrink-0 flex items-center">
                        <a href="{{ url_for('main.index') }}" class="text-2xl font-bold text-indigo-600">
                            Tutorial Platform
                        </a>
                    </div>
                    <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
                        <a href="{{ url_for('main.index') }}" 
                           class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                            Home
                        </a>
                        <a href="{{ url_for('main.about') }}" 
                           class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                            About
                        </a>
                    </div>
                </div>
                <div class="hidden sm:ml-6 sm:flex sm:items-center">
                    {% if current_user.is_authenticated %}
                        <span class="text-gray-700 mr-4">Hello, {{ current_user.full_name or current_user.email }}</span>
                        <a href="{{ url_for('auth.logout') }}" 
                           class="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700">
                            Logout
                        </a>
                    {% else %}
                        <a href="{{ url_for('auth.login') }}" 
                           class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                            Login
                        </a>
                        <a href="{{ url_for('auth.register') }}" 
                           class="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 ml-3">
                            Register
                        </a>
                    {% endif %}
                </div>
            </div>
        </div>
    </nav>

    <!-- Flash Messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
                {% for category, message in messages %}
                    <div class="rounded-md p-4 mb-4 {% if category == 'success' %}bg-green-50 text-green-800{% elif category == 'danger' or category == 'error' %}bg-red-50 text-red-800{% elif category == 'warning' %}bg-yellow-50 text-yellow-800{% else %}bg-blue-50 text-blue-800{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="bg-white mt-12">
        <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <p class="text-center text-gray-500 text-sm">
                &copy; 2024 Tutorial E-Commerce Platform. All rights reserved.
            </p>
        </div>
    </footer>

    <!-- Custom JS -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

#### Create `app/templates/index.html`:

```html
{% extends "base.html" %}

{% block title %}Home - Tutorial E-Commerce Platform{% endblock %}

{% block content %}
<div class="text-center">
    <h1 class="text-4xl font-bold text-gray-900 mb-4">
        Welcome to Tutorial E-Commerce Platform
    </h1>
    <p class="text-xl text-gray-600 mb-8">
        Learn programming through interactive courses
    </p>
    
    {% if current_user.is_authenticated %}
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4">Welcome back, {{ current_user.full_name or current_user.email }}!</h2>
            <p class="text-gray-600">You are successfully logged in.</p>
        </div>
    {% else %}
        <div class="space-x-4">
            <a href="{{ url_for('auth.register') }}" 
               class="bg-indigo-600 text-white px-6 py-3 rounded-md text-lg font-medium hover:bg-indigo-700 inline-block">
                Get Started
            </a>
            <a href="{{ url_for('auth.login') }}" 
               class="bg-gray-200 text-gray-800 px-6 py-3 rounded-md text-lg font-medium hover:bg-gray-300 inline-block">
                Login
            </a>
        </div>
    {% endif %}
</div>
{% endblock %}
```

#### Create `app/templates/about.html`:

```html
{% extends "base.html" %}

{% block title %}About - Tutorial E-Commerce Platform{% endblock %}

{% block content %}
<div class="prose max-w-none">
    <h1 class="text-4xl font-bold text-gray-900 mb-6">About Us</h1>
    
    <div class="bg-white rounded-lg shadow-md p-8">
        <p class="text-lg text-gray-700 mb-4">
            Tutorial E-Commerce Platform is an interactive learning platform where you can 
            learn programming through hands-on courses.
        </p>
        
        <h2 class="text-2xl font-bold text-gray-900 mt-6 mb-4">What We Offer</h2>
        <ul class="list-disc list-inside text-gray-700 space-y-2">
            <li>Python programming courses from beginner to advanced</li>
            <li>SQL database courses with interactive exercises</li>
            <li>Interactive code editors for practice</li>
            <li>Real-time code execution and feedback</li>
            <li>Certificates upon course completion</li>
        </ul>
    </div>
</div>
{% endblock %}
```

#### Create `app/templates/auth/register.html`:

```html
{% extends "base.html" %}

{% block title %}Register - Tutorial E-Commerce Platform{% endblock %}

{% block content %}
<div class="max-w-md mx-auto">
    <div class="bg-white rounded-lg shadow-md p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6 text-center">Create Account</h2>
        
        <form method="POST" novalidate>
            {{ form.hidden_tag() }}
            
            <!-- Email -->
            <div class="mb-4">
                {{ form.email.label(class="block text-gray-700 font-medium mb-2") }}
                {{ form.email(class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500") }}
                {% if form.email.errors %}
                    <p class="text-red-500 text-sm mt-1">{{ form.email.errors[0] }}</p>
                {% endif %}
            </div>
            
            <!-- Username -->
            <div class="mb-4">
                {{ form.username.label(class="block text-gray-700 font-medium mb-2") }}
                {{ form.username(class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500") }}
                {% if form.username.errors %}
                    <p class="text-red-500 text-sm mt-1">{{ form.username.errors[0] }}</p>
                {% endif %}
            </div>
            
            <!-- Full Name -->
            <div class="mb-4">
                {{ form.full_name.label(class="block text-gray-700 font-medium mb-2") }}
                {{ form.full_name(class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500") }}
                {% if form.full_name.errors %}
                    <p class="text-red-500 text-sm mt-1">{{ form.full_name.errors[0] }}</p>
                {% endif %}
            </div>
            
            <!-- Password -->
            <div class="mb-4">
                {{ form.password.label(class="block text-gray-700 font-medium mb-2") }}
                {{ form.password(class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500") }}
                {% if form.password.errors %}
                    <p class="text-red-500 text-sm mt-1">{{ form.password.errors[0] }}</p>
                {% endif %}
            </div>
            
            <!-- Confirm Password -->
            <div class="mb-6">
                {{ form.confirm_password.label(class="block text-gray-700 font-medium mb-2") }}
                {{ form.confirm_password(class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500") }}
                {% if form.confirm_password.errors %}
                    <p class="text-red-500 text-sm mt-1">{{ form.confirm_password.errors[0] }}</p>
                {% endif %}
            </div>
            
            <!-- Submit -->
            {{ form.submit(class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium") }}
        </form>
        
        <p class="text-center text-gray-600 mt-4">
            Already have an account? 
            <a href="{{ url_for('auth.login') }}" class="text-indigo-600 hover:text-indigo-800">Login here</a>
        </p>
    </div>
</div>
{% endblock %}
```

#### Create `app/templates/auth/login.html`:

```html
{% extends "base.html" %}

{% block title %}Login - Tutorial E-Commerce Platform{% endblock %}

{% block content %}
<div class="max-w-md mx-auto">
    <div class="bg-white rounded-lg shadow-md p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6 text-center">Login</h2>
        
        <form method="POST" novalidate>
            {{ form.hidden_tag() }}
            
            <!-- Email -->
            <div class="mb-4">
                {{ form.email.label(class="block text-gray-700 font-medium mb-2") }}
                {{ form.email(class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500") }}
                {% if form.email.errors %}
                    <p class="text-red-500 text-sm mt-1">{{ form.email.errors[0] }}</p>
                {% endif %}
            </div>
            
            <!-- Password -->
            <div class="mb-4">
                {{ form.password.label(class="block text-gray-700 font-medium mb-2") }}
                {{ form.password(class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500") }}
                {% if form.password.errors %}
                    <p class="text-red-500 text-sm mt-1">{{ form.password.errors[0] }}</p>
                {% endif %}
            </div>
            
            <!-- Remember Me -->
            <div class="mb-4 flex items-center">
                {{ form.remember_me(class="mr-2") }}
                {{ form.remember_me.label(class="text-gray-700") }}
            </div>
            
            <!-- Submit -->
            {{ form.submit(class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium") }}
        </form>
        
        <div class="text-center mt-4 space-y-2">
            <p class="text-gray-600">
                <a href="{{ url_for('auth.request_password_reset') }}" class="text-indigo-600 hover:text-indigo-800">
                    Forgot password?
                </a>
            </p>
            <p class="text-gray-600">
                Don't have an account? 
                <a href="{{ url_for('auth.register') }}" class="text-indigo-600 hover:text-indigo-800">Register here</a>
            </p>
        </div>
    </div>
</div>
{% endblock %}
```

#### Create `app/templates/auth/request_reset.html`:

```html
{% extends "base.html" %}

{% block title %}Reset Password - Tutorial E-Commerce Platform{% endblock %}

{% block content %}
<div class="max-w-md mx-auto">
    <div class="bg-white rounded-lg shadow-md p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6 text-center">Reset Password</h2>
        
        <p class="text-gray-600 mb-6 text-center">
            Enter your email address and we'll send you instructions to reset your password.
        </p>
        
        <form method="POST" novalidate>
            {{ form.hidden_tag() }}
            
            <!-- Email -->
            <div class="mb-6">
                {{ form.email.label(class="block text-gray-700 font-medium mb-2") }}
                {{ form.email(class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500") }}
                {% if form.email.errors %}
                    <p class="text-red-500 text-sm mt-1">{{ form.email.errors[0] }}</p>
                {% endif %}
            </div>
            
            <!-- Submit -->
            {{ form.submit(class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium") }}
        </form>
        
        <p class="text-center text-gray-600 mt-4">
            <a href="{{ url_for('auth.login') }}" class="text-indigo-600 hover:text-indigo-800">Back to login</a>
        </p>
    </div>
</div>
{% endblock %}
```

#### Create `app/templates/auth/reset_password.html`:

```html
{% extends "base.html" %}

{% block title %}Reset Password - Tutorial E-Commerce Platform{% endblock %}

{% block content %}
<div class="max-w-md mx-auto">
    <div class="bg-white rounded-lg shadow-md p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6 text-center">Set New Password</h2>
        
        <form method="POST" novalidate>
            {{ form.hidden_tag() }}
            
            <!-- Password -->
            <div class="mb-4">
                {{ form.password.label(class="block text-gray-700 font-medium mb-2") }}
                {{ form.password(class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500") }}
                {% if form.password.errors %}
                    <p class="text-red-500 text-sm mt-1">{{ form.password.errors[0] }}</p>
                {% endif %}
            </div>
            
            <!-- Confirm Password -->
            <div class="mb-6">
                {{ form.confirm_password.label(class="block text-gray-700 font-medium mb-2") }}
                {{ form.confirm_password(class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500") }}
                {% if form.confirm_password.errors %}
                    <p class="text-red-500 text-sm mt-1">{{ form.confirm_password.errors[0] }}</p>
                {% endif %}
            </div>
            
            <!-- Submit -->
            {{ form.submit(class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium") }}
        </form>
    </div>
</div>
{% endblock %}
```

---

### **Step 10: Create Static Files**

#### Create `app/static/css/main.css`:

```css
/* Custom styles */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* Flash message animations */
.alert {
    animation: slideIn 0.3s ease-in-out;
}

@keyframes slideIn {
    from {
        transform: translateY(-20px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}
```

#### Create `app/static/js/main.js`:

```javascript
// Main JavaScript file
console.log('Tutorial E-Commerce Platform loaded');

// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert, [class*="bg-green"], [class*="bg-red"], [class*="bg-yellow"], [class*="bg-blue"]');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});
```

---

### **Step 11: Create app.py (Entry Point)**

Create `app.py`:

```python
# app.py
"""Application entry point."""

import os
from app import create_app
from app.extensions import db
from app.models import TutorialUser, Tutorial, PasswordReset

# Create Flask app
app = create_app(os.getenv('FLASK_ENV') or 'development')

# Shell context for Flask CLI
@app.shell_context_processor
def make_shell_context():
    """Add models to shell context."""
    return {
        'db': db,
        'TutorialUser': TutorialUser,
        'Tutorial': Tutorial,
        'PasswordReset': PasswordReset
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

### **Step 12: Create .gitignore**

Create `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Flask
instance/
.webassets-cache

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Database
*.db
*.sqlite

# Logs
*.log

# OS
.DS_Store
Thumbs.db
```

---

### **Step 13: Initialize Database**

Run the following commands:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Initialize Flask-Migrate
flask db init

# Create initial migration
flask db migrate -m "Initial migration: TutorialUser, Tutorial, PasswordReset tables"

# Apply migration to database
flask db upgrade
```

This will create the following tables in your shared MySQL database:
- `tutorial_users`
- `tutorials`
- `tutorial_password_resets`
- `alembic_version` (for migration tracking)

**Important:** These table names DO NOT conflict with existing `accounts` or `user` tables.

---

### **Step 14: Run the Application**

```powershell
# Run Flask development server
flask run

# Or use python directly
python app.py
```

The application should start on `http://localhost:5000`

You should see:
```
🔄 Starting SSH tunnel on port XXXXX...
✅ SSH tunnel started successfully on port XXXXX
🔒 Using SSH tunnel connection (localhost:XXXXX)
 * Running on http://0.0.0.0:5000
```

---

## ✅ Testing Phase 1

### Test Authentication Flow:

1. **Register a new user:**
   - Go to http://localhost:5000/auth/register
   - Fill in the form (email, password, etc.)
   - Click "Register"
   - Should see success message and redirect to login

2. **Login:**
   - Go to http://localhost:5000/auth/login
   - Enter registered email and password
   - Click "Login"
   - Should see "Hello, [name]" in navigation

3. **Test failed login:**
   - Try wrong password 5 times
   - Account should be locked for 30 minutes

4. **Password reset:**
   - Go to http://localhost:5000/auth/reset-password-request
   - Enter email
   - Check console for reset link (email sending)
   - Click reset link and set new password

5. **Logout:**
   - Click "Logout" button
   - Should redirect to homepage

---

## 📊 Database Verification

Check that tables were created:

```sql
-- Connect to database and run:
SHOW TABLES LIKE 'tutorial_%';

-- Should show:
-- tutorial_users
-- tutorial_password_resets
-- tutorials

-- Check table structure:
DESCRIBE tutorial_users;

-- Check data:
SELECT id, email, username, is_active, created_at FROM tutorial_users;
```

---

## 🎯 Success Criteria

✅ SSH tunnel connects successfully to PythonAnywhere MySQL  
✅ Flask application runs without errors  
✅ Database tables created with correct names (no conflicts)  
✅ User registration works  
✅ User login/logout works  
✅ Password reset flow works  
✅ Flash messages display correctly  
✅ Mobile responsive design works  
✅ No security vulnerabilities in authentication  

---

## 📝 Next Steps (Phase 2)

Once Phase 1 is complete and tested, you'll move to Phase 2:
- Admin course management
- Course catalog with filtering
- Search functionality
- Course detail pages

---

## 🐛 Common Issues & Solutions

### Issue 1: SSH Tunnel Connection Failed
**Solution:** Check `.env` file has correct SSH credentials

### Issue 2: Table Already Exists Error
**Solution:** Use different table names (already done with `tutorial_` prefix)

### Issue 3: Email Not Sending
**Solution:** In development, check console output. In production, configure SMTP properly.

### Issue 4: ImportError for sshtunnel
**Solution:** `pip install sshtunnel`

### Issue 5: CSRF Token Missing
**Solution:** Make sure `{{ form.hidden_tag() }}` is in all forms

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [Flask-Login](https://flask-login.readthedocs.io/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [WTForms](https://wtforms.readthedocs.io/)

---

**Congratulations!** You've completed Phase 1 setup. The foundation is ready for building the course management and payment systems in the next phases.
