@echo off
REM Quick build without cleanup - faster for testing

echo Building WiiVC Injector (Quick Mode)...

pyinstaller WiiVC-Injector.spec

if errorlevel 1 (
    echo Build FAILED!
    pause
    exit /b 1
)

echo Build SUCCESS!
echo Executable: dist\WiiVC-Injector.exe
echo.

REM Ask to run
set /p run="Run now? (y/n): "
if /i "%run%"=="y" (
    start dist\WiiVC-Injector.exe
)
