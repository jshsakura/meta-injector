#!/usr/bin/env python3
"""Build standalone executable for WiiVC Injector."""
import os
import sys
import shutil
import subprocess
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
STANDALONE_DIR = PROJECT_ROOT / "standalone"

def clean_build():
    """Clean previous build artifacts."""
    print("[*] Cleaning previous build...")

    dirs_to_clean = [
        PROJECT_ROOT / "build",
        PROJECT_ROOT / "dist",
        STANDALONE_DIR / "build",
        STANDALONE_DIR / "dist",
    ]

    for dir_path in dirs_to_clean:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   Removed: {dir_path}")

    # Remove spec files
    for spec_file in PROJECT_ROOT.glob("*.spec"):
        spec_file.unlink()
        print(f"   Removed: {spec_file}")

def install_dependencies():
    """Ensure PyInstaller is installed."""
    print("\n[*] Checking dependencies...")
    try:
        import PyInstaller
        print(f"   OK PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("   Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("   OK PyInstaller installed")

def build_exe():
    """Build standalone executable using PyInstaller."""
    print("\n[*] Building executable...")

    # Paths
    icon_path = PROJECT_ROOT / "resources" / "images" / "icon.ico"
    main_script = PROJECT_ROOT / "run.py"

    # PyInstaller command - use python -m to avoid venv issues
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name=WiiVC-Injector",
        "--onefile",  # Single executable - everything in one .exe
        "--windowed",  # No console window
        f"--icon={icon_path}",

        # Add data files - pack only resources into the exe
        # core folder (75MB) is kept external to reduce exe size (22MB like TeconMoon)
        f"--add-data={PROJECT_ROOT / 'resources'};resources",
        f"--add-data={PROJECT_ROOT / 'src' / 'wiivc_injector'};wiivc_injector",

        # Hidden imports
        "--hidden-import=PyQt5",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=requests",
        "--hidden-import=sqlite3",
        "--hidden-import=json",
        "--hidden-import=ssl",
        "--hidden-import=urllib",
        "--hidden-import=urllib.request",

        # Exclude unnecessary modules to reduce size
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        "--exclude-module=pandas",
        "--exclude-module=scipy",
        "--exclude-module=tkinter",

        # Working directory
        f"--workpath={STANDALONE_DIR / 'build'}",
        f"--distpath={STANDALONE_DIR / 'dist'}",
        f"--specpath={STANDALONE_DIR}",

        str(main_script)
    ]

    print(f"   Running: {' '.join(cmd[:5])}...")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        print("   [FAILED] Build failed!")
        return False

    print("   OK Build completed successfully!")
    return True

def create_release_package():
    """Create release package with necessary files."""
    print("\n[*] Creating release package...")

    dist_dir = STANDALONE_DIR / "dist"
    release_dir = STANDALONE_DIR / "release"

    # Clean release directory
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir(parents=True, exist_ok=True)

    # Copy executable
    exe_name = "WiiVC-Injector.exe"
    exe_path = dist_dir / exe_name

    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / exe_name)
        print(f"   OK Copied: {exe_name}")
    else:
        print(f"   [FAILED] Executable not found: {exe_path}")
        return False

    # Copy core tools (only essential files, exclude BASE/C2W/DOL/IMG/NKIT/SOX)
    core_src = PROJECT_ROOT / "core"
    core_dst = release_dir / "core"

    if core_src.exists():
        core_dst.mkdir(parents=True, exist_ok=True)

        # Copy only essential folders
        essential_folders = ["EXE", "WIT", "JAR", "Galaxy1GamePad_v1.2"]
        for folder in essential_folders:
            src_folder = core_src / folder
            dst_folder = core_dst / folder
            if src_folder.exists():
                shutil.copytree(src_folder, dst_folder, dirs_exist_ok=True)

        # Copy shortnamepath.cmd if exists
        if (core_src / "shortnamepath.cmd").exists():
            shutil.copy2(core_src / "shortnamepath.cmd", core_dst / "shortnamepath.cmd")

        # Clean JAR content rules - remove generated files (images, fw.img)
        # These are auto-generated during build, no need to include in distribution
        jar_dir = core_dst / "JAR"
        if jar_dir.exists():
            for template_dir in jar_dir.iterdir():
                if template_dir.is_dir() and template_dir.name not in ["tmp", "output"]:
                    # Remove meta folder contents (images will be auto-generated)
                    meta_dir = template_dir / "meta"
                    if meta_dir.exists():
                        for file in meta_dir.iterdir():
                            if file.suffix in ['.tga', '.png', '.jpg']:
                                file.unlink()
                    # Remove code folder contents (fw.img will be copied from base_files)
                    code_dir = template_dir / "code"
                    if code_dir.exists():
                        for file in code_dir.iterdir():
                            if file.name in ['fw.img', 'frisbiiU.rpx']:
                                file.unlink()

        print(f"   OK Copied: core/ (essential tools only, cleaned templates)")

    # Copy resources (icon, images, database - already embedded in exe)
    # No need to copy resources folder to release - they're packed into the .exe
    # The exe already has resources embedded via PyInstaller --add-data

    # Create README
    readme_path = release_dir / "README.txt"
    readme_content = """WiiVC Injector - Batch Mode
=============================

이 프로그램은 Wii와 GameCube 게임을 WiiU VC로 변환하는 배치 변환 도구입니다.

사용 방법:
1. WiiVC-Injector.exe를 실행합니다
2. "설정" 버튼을 눌러 암호화 키를 입력합니다
   - Wii U Common Key (필수)
   - Rhythm Heaven Fever Title Key (필수)
   - Xenoblade Chronicles Title Key (선택)
   - Super Mario Galaxy 2 Title Key (선택)
3. "파일 추가" 버튼으로 게임 ISO/WBFS 파일을 추가합니다
4. "빌드 시작" 버튼을 눌러 변환을 시작합니다

출력 파일:
- 빌드 결과는 "빌드결과" 폴더에 저장됩니다

주의사항:
- 첫 실행 시 Nintendo CDN에서 베이스 파일을 다운로드합니다 (인터넷 연결 필요)
- 다운로드한 파일은 base_files/ 폴더에 캐시되어 재사용됩니다

문의: https://github.com/TeconMoon/WiiU-Expedition-VC-Injector
"""

    readme_path.write_text(readme_content, encoding='utf-8')
    print(f"   OK Created: README.txt")

    # Show final size
    exe_size = exe_path.stat().st_size / (1024 * 1024)
    print(f"\n   [*] Executable size: {exe_size:.2f} MB")
    print(f"   [*] Release package: {release_dir}")

    return True

def main():
    """Main build process."""
    print("=" * 60)
    print("WiiVC Injector - Standalone Build Script")
    print("=" * 60)

    # Step 1: Clean
    clean_build()

    # Step 2: Install dependencies
    install_dependencies()

    # Step 3: Build executable
    if not build_exe():
        print("\n[FAILED] Build failed!")
        return 1

    # Step 4: Create release package
    if not create_release_package():
        print("\n[FAILED] Failed to create release package!")
        return 1

    print("\n" + "=" * 60)
    print("[SUCCESS] Build completed successfully!")
    print("=" * 60)
    print(f"\n[*] Release package: {STANDALONE_DIR / 'release'}")
    print(f"[*] Ready to distribute!\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
