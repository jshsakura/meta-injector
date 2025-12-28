"""Package release build with all required files."""
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# Get project root
project_root = Path(__file__).parent
dist_dir = project_root / "dist"
exe_file = dist_dir / "Meta-Injector.exe"

# Create release folder
release_name = f"WiiU-Expedition-VC-Injector-v1.0-{datetime.now().strftime('%Y%m%d')}"
release_dir = dist_dir / release_name
release_zip = dist_dir / f"{release_name}.zip"

print("=" * 70)
print("Packaging Release Build")
print("=" * 70)

# Clean up old release
if release_dir.exists():
    shutil.rmtree(release_dir)
    print(f"[OK] Cleaned old release folder")

if release_zip.exists():
    release_zip.unlink()
    print(f"[OK] Cleaned old release ZIP")

# Create release folder
release_dir.mkdir(exist_ok=True)

# Copy EXE
shutil.copy(exe_file, release_dir / "WiiU-Expedition-VC-Injector.exe")
print(f"[OK] Copied EXE ({exe_file.stat().st_size / 1024 / 1024:.1f} MB)")

# Copy core folder
core_src = project_root / "core"
core_dest = release_dir / "core"
shutil.copytree(core_src, core_dest)
print(f"[OK] Copied core folder")

# Copy README
readme_files = ["README.md", "README.en.md"]
for readme in readme_files:
    readme_path = project_root / readme
    if readme_path.exists():
        shutil.copy(readme_path, release_dir / readme)
        print(f"[OK] Copied {readme}")

# Create ZIP
print(f"\nCreating ZIP archive: {release_zip.name}")
with zipfile.ZipFile(release_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
    for file in release_dir.rglob('*'):
        if file.is_file():
            arcname = file.relative_to(dist_dir)
            zf.write(file, arcname)

# Get sizes
exe_size = exe_file.stat().st_size / 1024 / 1024
zip_size = release_zip.stat().st_size / 1024 / 1024

print("\n" + "=" * 70)
print("Release Package Created!")
print("=" * 70)
print(f"EXE Size: {exe_size:.1f} MB")
print(f"ZIP Size: {zip_size:.1f} MB")
print(f"\nRelease folder: {release_dir}")
print(f"Release ZIP: {release_zip}")
print("=" * 70)
