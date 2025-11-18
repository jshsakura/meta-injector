#!/usr/bin/env python3
"""Quick launcher for WiiVC Injector - Batch Mode by default."""
import sys
import locale
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PyQt5.QtWidgets import QApplication
from wiivc_injector.batch_window import BatchWindow
from wiivc_injector.translations import tr

def main():
    """Launch batch mode window."""
    app = QApplication(sys.argv)
    app.setApplicationName("WiiVC Injector Batch")
    app.setOrganizationName("TeconMoon")

    # Auto-detect language based on system locale
    try:
        # Set locale to system default
        locale.setlocale(locale.LC_ALL, '')
        system_lang = locale.getlocale()[0]

        if system_lang and ('korean' in system_lang.lower() or system_lang.startswith('ko')):
            tr.set_language('ko')
            print("[INFO] Language set to Korean")
        else:
            tr.set_language('en')
            print("[INFO] Language set to English")
    except Exception as e:
        print(f"[WARN] Failed to detect locale: {e}")
        tr.set_language('ko')  # Default to Korean for Windows Korean systems
        print("[INFO] Defaulting to Korean")

    window = BatchWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
