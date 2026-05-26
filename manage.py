#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import webbrowser
import threading
import time


def open_browser():
    """Open browser after server starts."""
    time.sleep(2)  # Wait for server to start
    url = "http://127.0.0.1:8000/"
    webbrowser.open(url)
    print(f"\n{'='*60}")
    print(f"Browser opened automatically: {url}")
    print(f"{'='*60}\n")


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cattle_disease_system.settings')
    try:
        from django.core.management import execute_from_command_line
        
        # If running server, open browser automatically
        if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
            # Start browser in background thread
            browser_thread = threading.Thread(target=open_browser, daemon=True)
            browser_thread.start()
        
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
