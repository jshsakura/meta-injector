#!/usr/bin/env python3
"""Launch WiiVC Injector in Batch Mode."""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PyQt5.QtWidgets import QApplication
from wiivc_injector.batch_window import BatchWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("WiiVC Injector Batch")
    app.setOrganizationName("TeconMoon")

    window = BatchWindow()
    window.show()

    sys.exit(app.exec_())
