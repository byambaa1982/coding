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
        from urllib.parse import quote_plus
        
        # URL encode password to handle special characters
        encoded_password = quote_plus(cls.DB_PASSWORD)
        
        if cls.is_on_pythonanywhere():
            # Direct connection on PythonAnywhere
            uri = f"mysql+pymysql://{cls.DB_USER}:{encoded_password}@{cls.DB_HOST}/{cls.DB_NAME}"
            print("📡 Using direct database connection (PythonAnywhere)")
        else:
            # Use SSH tunnel for local development
            tunnel = cls.start_ssh_tunnel()
            if tunnel:
                local_bind_port = tunnel.local_bind_port
                uri = f"mysql+pymysql://{cls.DB_USER}:{encoded_password}@127.0.0.1:{local_bind_port}/{cls.DB_NAME}"
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
