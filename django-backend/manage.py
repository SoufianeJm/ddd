#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging
from io import StringIO

# Configure logging to suppress most output in production
logging.basicConfig(level=logging.ERROR)

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slr_project.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Auto-start server if no arguments provided (for desktop app)
    if len(sys.argv) == 1:
        # Set default arguments for desktop app
        sys.argv = ['manage.py', 'runserver', '127.0.0.1:8000', '--noreload']
        
        # Suppress Django startup messages in production build
        if getattr(sys, 'frozen', False):
            # We're running in a PyInstaller bundle
            sys.stderr = StringIO()  # Suppress error messages
            
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
