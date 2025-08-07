#!/usr/bin/env python
"""
Django Launcher for Desktop Application
Handles migrations and starts the server automatically
"""

import os
import sys
import django
import subprocess
import time
import threading
from pathlib import Path

def setup_django():
    """Initialize Django with appropriate settings"""
    # Detect if running in development (non-frozen)
    is_dev = not getattr(sys, 'frozen', False)
    
    if is_dev:
        # Development: use regular settings with STATICFILES_DIRS
        print("[INFO] Running in development mode")
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slr_project.settings')
    else:
        # Production: use desktop settings optimized for PyInstaller
        print("[INFO] Running in production mode")
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slr_project.settings_desktop')
    
    django.setup()

def run_migrations():
    """Run makemigrations and migrate"""
    print("[DB] Setting up database...")
    
    try:
        from django.core.management import execute_from_command_line
        
        # Make migrations
        print("  - Making migrations...")
        execute_from_command_line(['manage.py', 'makemigrations', '--noinput'])
        
        # Apply migrations
        print("  - Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        
        print("[DB] Database setup complete!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database setup failed: {e}")
        return False

def collect_static():
    """Collect static files only if needed"""
    from django.conf import settings
    from pathlib import Path
    
    # Check if staticfiles directory exists and has files
    staticfiles_dir = Path(settings.STATIC_ROOT)
    
    if staticfiles_dir.exists() and any(staticfiles_dir.iterdir()):
        print("[STATIC] Static files already exist, skipping collection...")
        return True
    
    print("[STATIC] Collecting static files...")
    
    try:
        from django.core.management import execute_from_command_line
        # Use --noinput but remove --clear to avoid deleting existing files
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("[STATIC] Static files collected!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Static files collection failed: {e}")
        return False

def start_server():
    """Start Django development server"""
    print("[SERVER] Starting Django server...")
    
    try:
        from django.core.management import execute_from_command_line
        
        # Start server on 127.0.0.1:8000
        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000', '--noreload', '--insecure'])
        
    except Exception as e:
        print(f"[ERROR] Server failed to start: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    print("[FACTURATION] Django Backend Starting...")
    
    # Setup Django
    setup_django()
    
    # Run database migrations
    if not run_migrations():
        print("[ERROR] Failed to setup database. Exiting...")
        sys.exit(1)
    
    # Collect static files
    if not collect_static():
        print("[WARNING] Static files collection failed, but continuing...")
    
    # Start the server
    print("[INFO] Starting server at http://127.0.0.1:8000")
    print("[INFO] Electron will connect automatically...")
    print("[INFO] Press Ctrl+C to stop")
    
    start_server()

if __name__ == '__main__':
    main()
