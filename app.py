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
