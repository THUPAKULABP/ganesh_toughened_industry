@echo off
setlocal enabledelayedexpansion

echo ===========================================
echo   Ganesh Toughened Industry Application
echo ===========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://python.org
    echo.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
set MISSING_PACKAGES=0

python -c "import PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Pillow...
    python -m pip install Pillow
    set MISSING_PACKAGES=1
)

python -c "import reportlab" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing reportlab...
    python -m pip install reportlab
    set MISSING_PACKAGES=1
)

python -c "import qrcode" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing qrcode...
    python -m pip install qrcode
    set MISSING_PACKAGES=1
)

if %MISSING_PACKAGES% equ 1 (
    echo.
    echo Required packages have been installed.
    echo.
)

REM Create necessary directories if they don't exist
if not exist "assets\images" mkdir assets\images
if not exist "assets\fonts" mkdir assets\fonts
if not exist "config" mkdir config
if not exist "utils" mkdir utils
if not exist "backups" mkdir backups

REM Check if database exists, if not create it
if not exist "ganesh_toughened_industry.db" (
    echo Initializing database...
    python -c "from database import Database; db = Database(); print('Database initialized successfully')"
)

echo.
echo Starting the application...
echo.

REM Run the application
python main.py

REM If the application crashes, show a message
if %errorlevel% neq 0 (
    echo.
    echo The application crashed. Please check the error message above.
    echo.
    echo If the problem persists, please contact support.
    pause
)

