#!/usr/bin/env python3
"""
WiiVC Injector - Standalone Builder
Builds a standalone executable using PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


class Color:
    """Terminal colors for output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def disable():
        """Disable colors on Windows if not supported."""
        Color.HEADER = ''
        Color.OKBLUE = ''
        Color.OKCYAN = ''
        Color.OKGREEN = ''
        Color.WARNING = ''
        Color.FAIL = ''
        Color.ENDC = ''
        Color.BOLD = ''


# Disable colors on Windows
if sys.platform == 'win32':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        Color.disable()


def print_header(text):
    """Print colored header."""
    print(f"\n{Color.HEADER}{Color.BOLD}{'='*50}{Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD}{text.center(50)}{Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD}{'='*50}{Color.ENDC}\n")


def print_step(step, text):
    """Print build step."""
    print(f"{Color.OKCYAN}[{step}]{Color.ENDC} {text}")


def print_success(text):
    """Print success message."""
    try:
        print(f"{Color.OKGREEN}✓ {text}{Color.ENDC}")
    except UnicodeEncodeError:
        print(f"{Color.OKGREEN}[OK] {text}{Color.ENDC}")


def print_error(text):
    """Print error message."""
    try:
        print(f"{Color.FAIL}✗ {text}{Color.ENDC}")
    except UnicodeEncodeError:
        print(f"{Color.FAIL}[ERROR] {text}{Color.ENDC}")


def print_warning(text):
    """Print warning message."""
    try:
        print(f"{Color.WARNING}⚠ {text}{Color.ENDC}")
    except UnicodeEncodeError:
        print(f"{Color.WARNING}[WARNING] {text}{Color.ENDC}")


def run_command(cmd, cwd=None):
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def check_pyinstaller():
    """Check if PyInstaller is installed, install if not."""
    print_step("1/6", "Checking PyInstaller...")

    try:
        import PyInstaller
        print_success(f"PyInstaller {PyInstaller.__version__} found")
        return True
    except ImportError:
        print_warning("PyInstaller not found. Installing...")
        success, output = run_command(f"{sys.executable} -m pip install pyinstaller")

        if success:
            print_success("PyInstaller installed successfully")
            return True
        else:
            print_error("Failed to install PyInstaller")
            print(output)
            return False


def check_dependencies():
    """Check if all dependencies are installed."""
    print_step("2/6", "Checking dependencies...")

    required = ['PyQt5', 'Pillow']
    missing = []

    for package in required:
        try:
            __import__(package)
            print_success(f"{package} found")
        except ImportError:
            missing.append(package)
            print_warning(f"{package} not found")

    if missing:
        print_warning(f"Installing missing packages: {', '.join(missing)}")
        success, output = run_command(f"{sys.executable} -m pip install {' '.join(missing)}")

        if not success:
            print_error("Failed to install dependencies")
            print(output)
            return False

    print_success("All dependencies satisfied")
    return True


def clean_build_files():
    """Clean previous build artifacts."""
    print_step("3/6", "Cleaning previous builds...")

    dirs_to_clean = ['build', 'dist', 'standalone/build', 'standalone/dist']
    files_to_clean = ['*.spec', 'standalone/*.spec']

    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print_success(f"Removed {dir_path}/")

    # Clean spec files
    for pattern in files_to_clean:
        import glob
        for file in glob.glob(pattern):
            os.remove(file)
            print_success(f"Removed {file}")

    print_success("Build directory cleaned")
    return True


def check_resources():
    """Check if required resources exist."""
    print_step("4/6", "Checking resources...")

    resources = {
        'resources/icon.ico': 'Application icon',
        'resources/wiitdb.txt': 'Game database',
    }

    all_exist = True
    for path, desc in resources.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print_success(f"{desc}: {path} ({size:,} bytes)")
        else:
            print_warning(f"{desc} not found: {path}")
            all_exist = False

    return all_exist


def build_executable():
    """Build the executable using PyInstaller."""
    print_step("5/6", "Building executable...")

    # Determine paths
    project_root = Path.cwd()
    src_path = project_root / 'src' / 'wiivc_injector' / 'main.py'
    resources_path = project_root / 'resources'
    icon_path = resources_path / 'icon.ico'

    # Build command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        '--onefile',
        '--windowed',
        '--name', 'WiiU-Expedition-VC-Injector',
    ]

    # Add icon if exists
    if icon_path.exists():
        cmd.extend(['--icon', str(icon_path)])

    # Add resources
    cmd.extend([
        '--add-data', f'{resources_path}{os.pathsep}resources',
        '--hidden-import', 'PyQt5',
        '--hidden-import', 'PIL',
        '--hidden-import', 'PIL._tkinter_finder',
        str(src_path)
    ])

    print(f"Running: {' '.join(cmd)}")

    # Run PyInstaller
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print_success("Build completed successfully!")
        return True
    else:
        print_error("Build failed!")
        print(result.stderr)
        return False


def create_release_package():
    """Create release package."""
    print_step("6/6", "Creating release package...")

    # Create release directory
    release_dir = Path('release')
    release_dir.mkdir(exist_ok=True)

    # Copy executable
    exe_name = 'WiiU-Expedition-VC-Injector.exe' if sys.platform == 'win32' else 'WiiU-Expedition-VC-Injector'
    src_exe = Path('dist') / exe_name

    if not src_exe.exists():
        print_error(f"Executable not found: {src_exe}")
        return False

    dst_exe = release_dir / exe_name
    shutil.copy2(src_exe, dst_exe)

    exe_size = dst_exe.stat().st_size
    print_success(f"Copied executable: {exe_name} ({exe_size:,} bytes / {exe_size/1024/1024:.1f} MB)")

    # Create README
    readme_content = """WiiU Expedition VC Injector (위유 원정대 VC 인젝터)

Simply run WiiU-Expedition-VC-Injector.exe to start the application.

System Requirements:
- Windows 7 or higher (for .exe)
- Linux/macOS (for standalone binary)
- No Python installation required
- All dependencies included

Features:
- Support for Wii Retail, Wii Homebrew, Wii NAND, and GC Retail
- Custom icon, banner, DRC, and logo images
- Automatic game info extraction
- GamePad emulation options
- Advanced patching options
- SD Card utilities

Based on TeconMoon's WiiVC Injector
Python Edition: WiiU Expedition (위유 원정대)

For issues and updates, visit:
https://github.com/yourusername/WiiU-Expedition-VC-Injector
"""

    readme_path = release_dir / 'README.txt'
    readme_path.write_text(readme_content, encoding='utf-8')
    print_success("Created README.txt")

    print_success(f"Release package created in '{release_dir}/'")
    return True


def main():
    """Main build process."""
    print_header("WiiU Expedition VC Injector - Builder")

    # Check if running from project root
    if not os.path.exists('src/wiivc_injector'):
        print_error("Error: Must run from project root directory")
        print("Current directory:", os.getcwd())
        return 1

    # Build steps
    steps = [
        ("Check PyInstaller", check_pyinstaller),
        ("Check dependencies", check_dependencies),
        ("Clean build files", clean_build_files),
        ("Check resources", check_resources),
        ("Build executable", build_executable),
        ("Create release package", create_release_package),
    ]

    for i, (name, func) in enumerate(steps, 1):
        if not func():
            print_error(f"\nBuild failed at step {i}: {name}")
            return 1

    # Success summary
    print_header("Build Complete!")
    try:
        print(f"{Color.OKGREEN}✓ Executable: dist/WiiU-Expedition-VC-Injector.exe{Color.ENDC}")
        print(f"{Color.OKGREEN}✓ Release package: release/{Color.ENDC}")
    except UnicodeEncodeError:
        print(f"{Color.OKGREEN}[OK] Executable: dist/WiiU-Expedition-VC-Injector.exe{Color.ENDC}")
        print(f"{Color.OKGREEN}[OK] Release package: release/{Color.ENDC}")
    print(f"\n{Color.BOLD}Run the application:{Color.ENDC}")

    if sys.platform == 'win32':
        print(f"  {Color.OKCYAN}release\\WiiU-Expedition-VC-Injector.exe{Color.ENDC}")
    else:
        print(f"  {Color.OKCYAN}./release/WiiU-Expedition-VC-Injector{Color.ENDC}")

    print()
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_error("\n\nBuild cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
