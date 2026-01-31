@echo off
REM Farm Monitor - Quick Start Script (Windows)

echo ========================================
echo Farm Monitor - Backend Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

echo Python detected
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Check for credentials
if not exist "gee-credentials.json" (
    echo WARNING: gee-credentials.json not found
    echo Satellite features will use mock data
    echo See docs\SETUP.md for GEE setup instructions
    echo.
)

REM Create .env if needed
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo Please edit .env with your settings
    echo.
)

REM Start server
echo.
echo ========================================
echo Starting Farm Monitor API...
echo ========================================
echo Server: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo Press Ctrl+C to stop
echo.

python main.py
