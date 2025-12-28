#!/usr/bin/env python3
"""Build standalone EXE using PyInstaller."""
import PyInstaller.__main__
import os
import shutil
import zipfile
from pathlib import Path

# Get project root
project_root = Path(__file__).parent
run_py = project_root / "run.py"
core_path = project_root / "core"

# Check if resources exists (optional)
resources_path = project_root / "resources"
icon_path = project_root / "resources" / "images" / "icon.ico"

# Build data files list - add core folder directly
print("Adding core folder to bundle...")
data_files = [
    f'--add-data={core_path}{os.pathsep}{core_path.name}',  # Add core folder
]

if resources_path.exists():
    data_files.append(f'--add-data={resources_path}{os.pathsep}{resources_path.name}')

# Build with PyInstaller
args = [
    str(run_py),  # Main entry point
    '--onefile',  # Single executable
    '--windowed',  # No console window (GUI app)
    '--name=Meta-Injector',
    f'--icon={icon_path}' if icon_path.exists() else '--icon=NONE',

    # Hidden imports (PyQt5 submodules)
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=PyQt5.QtWidgets',
    '--hidden-import=PIL',
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=requests',

    # Exclude unnecessary modules to reduce size
    '--exclude-module=pytest',
    '--exclude-module=setuptools',
    '--exclude-module=numpy',
    '--exclude-module=pandas',
    '--exclude-module=matplotlib',
    '--exclude-module=tkinter',
    '--exclude-module=IPython',
    '--exclude-module=jupyter',
    '--exclude-module=scipy',
    '--exclude-module=test',
    '--exclude-module=unittest',

    # Build directories
    '--distpath=dist',
    '--workpath=build',
    '--specpath=.',

    # Clean previous build
    '--clean',

    # No UPX (can cause antivirus false positives)
    '--noupx',
]

# Add data files
args.extend(data_files)

print("Building standalone EXE...")
print(f"Entry point: {run_py}")
print(f"Output: dist/WiiU-Expedition-VC.exe")
print()

PyInstaller.__main__.run(args)

print("\n" + "="*80)
print("Build complete!")
print(f"Executable: {project_root / 'dist' / 'WiiU-Expedition-VC.exe'}")
print("="*80)
