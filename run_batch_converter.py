#!/usr/bin/env python3
"""Launcher for Batch WBFS Converter."""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from wiivc_injector.batch_converter import main

if __name__ == '__main__':
    main()
