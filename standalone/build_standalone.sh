#!/bin/bash
# ========================================
# WiiVC Injector Standalone Builder (Linux/Mac)
# ========================================

echo ""
echo "========================================"
echo "Building WiiVC Injector Standalone"
echo "========================================"
echo ""

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "[ERROR] PyInstaller not found. Installing..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install PyInstaller"
        exit 1
    fi
fi

# Clean previous builds
echo "[1/5] Cleaning previous builds..."
rm -rf dist build *.spec

# Build with PyInstaller
echo "[2/5] Running PyInstaller..."
pyinstaller --clean \
    --noconfirm \
    --onefile \
    --windowed \
    --name "WiiVC-Injector" \
    --icon="../resources/icon.ico" \
    --add-data "../resources:resources" \
    --hidden-import "PyQt5" \
    --hidden-import "PIL" \
    --hidden-import "PIL._tkinter_finder" \
    "../src/wiivc_injector/main.py"

if [ $? -ne 0 ]; then
    echo "[ERROR] Build failed!"
    exit 1
fi

echo "[3/5] Build completed successfully!"

# Create release directory
echo "[4/5] Creating release package..."
mkdir -p release

# Copy executable
cp dist/WiiVC-Injector release/

# Create README
cat > release/README.txt << EOF
WiiVC Injector Standalone

Simply run WiiVC-Injector to start the application.

System Requirements:
- Linux/macOS
- No Python installation required

Original by TeconMoon
Python port by Community
EOF

chmod +x release/WiiVC-Injector

echo "[5/5] Package created in 'release' folder!"

echo ""
echo "========================================"
echo "Build Complete!"
echo "========================================"
echo "Executable: standalone/release/WiiVC-Injector"
echo ""
