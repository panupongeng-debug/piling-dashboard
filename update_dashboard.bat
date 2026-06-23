@echo off
REM Pile Dashboard Auto-Update Batch File
REM This script runs the Python updater and updates pile_data.json
REM Schedule this to run periodically via Windows Task Scheduler

cd /d "%~dp0"

echo.
echo ========================================
echo Pile Dashboard Data Updater
echo ========================================
echo.

REM Run Python script
python update_pile_dashboard.py

if %ERRORLEVEL% == 0 (
    echo.
    echo ✓ Update completed successfully
    echo.
) else (
    echo.
    echo ✗ Update failed with error code %ERRORLEVEL%
    echo.
    pause
)

REM Exit without closing window if run manually, close if scheduled
if "%1"=="scheduled" exit /b %ERRORLEVEL%
