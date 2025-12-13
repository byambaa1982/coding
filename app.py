# app.py
"""Application entry point."""

import os
import sys

# Suppress GLib warnings on Windows - MUST be set before any imports
if sys.platform == 'win32':
    os.environ['GSETTINGS_BACKEND'] = 'memory'
    os.environ['GIO_USE_VFS'] = 'local'
    os.environ['GLIB_DEBUG'] = '0'
    os.environ['G_MESSAGES_DEBUG'] = ''

import warnings
warnings.filterwarnings('ignore')
    
from app import create_app
from app.extensions import db
from app.models import TutorialUser, NewTutorial, Lesson, Exercise, PasswordReset

# Create Flask app
app = create_app(os.getenv('FLASK_ENV') or 'development')

# Shell context for Flask CLI
@app.shell_context_processor
def make_shell_context():
    """Add models to shell context."""
    return {
        'db': db,
        'TutorialUser': TutorialUser,
        'NewTutorial': NewTutorial,
        'Lesson': Lesson,
        'Exercise': Exercise,
        'PasswordReset': PasswordReset
    }


if __name__ == '__main__':
    # For production-like serving in development (no warnings)
    if os.getenv('USE_WAITRESS', '').lower() == 'true':
        from waitress import serve
        print(f" * Running on http://127.0.0.1:5000")
        print(f" * Running on http://0.0.0.0:5000")
        serve(app, host='0.0.0.0', port=5000, threads=8)
    else:
        # Flask development server with auto-reload
        app.run(debug=True, host='0.0.0.0', port=5000)
