"""Clean server runner without GLib warnings."""
import os
import sys

# Suppress warnings at OS level (file descriptor level) before any imports
if sys.platform == 'win32':
    # Set environment variables
    os.environ['GSETTINGS_BACKEND'] = 'memory'
    os.environ['GIO_USE_VFS'] = 'local'
    os.environ['GLIB_DEBUG'] = '0'
    os.environ['G_MESSAGES_DEBUG'] = ''
    
    # Redirect stderr to devnull temporarily to suppress C-level warnings
    stderr_fd = sys.stderr.fileno()
    old_stderr = os.dup(stderr_fd)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, stderr_fd)
    os.close(devnull)

# Import modules (warnings will be suppressed)
from waitress import serve
from app import create_app

# Restore stderr after imports
if sys.platform == 'win32':
    os.dup2(old_stderr, stderr_fd)
    os.close(old_stderr)

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV') or 'development')
    
    print(" * Serving on http://127.0.0.1:5000")
    print(" * Serving on http://0.0.0.0:5000")
    print(" * Press CTRL+C to quit")
    
    serve(app, host='0.0.0.0', port=5000, threads=8)
