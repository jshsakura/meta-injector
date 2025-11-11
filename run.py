#!/usr/bin/env python3
"""Quick launcher for WiiVC Injector during development."""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from wiivc_injector.main_window_new import main

if __name__ == '__main__':
    main()
