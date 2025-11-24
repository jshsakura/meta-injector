"""Main entry point for WiiVC Injector."""
import sys
import os

# Add the parent directory to the path for standalone builds
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = sys._MEIPASS
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

# Try relative import first (for package), fallback to absolute import (for standalone)
try:
    from .main_window_new import main
except ImportError:
    # For standalone builds, add the directory to sys.path
    if application_path not in sys.path:
        sys.path.insert(0, application_path)
    from main_window_new import main

if __name__ == '__main__':
    main()
