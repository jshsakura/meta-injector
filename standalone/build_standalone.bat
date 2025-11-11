@echo off
REM ========================================
REM WiiVC Injector Standalone Builder
REM ========================================

echo.
echo ========================================
echo Building WiiVC Injector Standalone
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>NUL
if errorlevel 1 (
    echo [ERROR] PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Clean previous builds
echo [1/5] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /f /q "*.spec"

REM Build with PyInstaller
echo [2/5] Running PyInstaller...
pyinstaller --clean ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "WiiVC-Injector" ^
    --icon="..\resources\icon.ico" ^
    --add-data "..\resources;resources" ^
    --hidden-import "PyQt5" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL._tkinter_finder" ^
    "..\src\wiivc_injector\main.py"

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo [3/5] Build completed successfully!

REM Create release directory
echo [4/5] Creating release package...
if not exist "release" mkdir "release"

REM Copy executable
copy "dist\WiiVC-Injector.exe" "release\" >NUL

REM Create README
echo Creating WiiVC Injector standalone executable... > "release\README.txt"
echo. >> "release\README.txt"
echo Simply run WiiVC-Injector.exe to start the application. >> "release\README.txt"
echo. >> "release\README.txt"
echo System Requirements: >> "release\README.txt"
echo - Windows 7 or higher >> "release\README.txt"
echo - No Python installation required >> "release\README.txt"
echo. >> "release\README.txt"
echo Original by TeconMoon >> "release\README.txt"
echo Python port by Community >> "release\README.txt"

echo [5/5] Package created in 'release' folder!

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo Executable: standalone\release\WiiVC-Injector.exe
echo.

pause
