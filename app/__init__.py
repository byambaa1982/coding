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
    from app.admin import admin_bp
    from app.catalog import catalog_bp
    from app.payment import payment_bp
    from app.account import account_bp
    from app.learning import learning_bp
    from app.python_practice import python_practice_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(catalog_bp, url_prefix='/catalog')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(account_bp, url_prefix='/account')
    app.register_blueprint(learning_bp, url_prefix='/learn')
    app.register_blueprint(python_practice_bp, url_prefix='/python-practice')
    
    # Custom Jinja2 filters
    import json
    
    @app.template_filter('from_json')
    def from_json_filter(value):
        """Parse JSON string to Python object."""
        if value:
            try:
                return json.loads(value)
            except:
                return []
        return []
    
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
