@echo off
echo ========================================
echo Starting EnhanceFund Server
echo with WebSocket Support (Daphne)
echo ========================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo WARNING: Virtual environment not detected!
    echo Please activate your virtual environment first.
    echo.
    pause
)

REM Check if daphne is installed
daphne --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Daphne is not installed!
    echo Please run: pip install daphne==4.1.0
    echo.
    pause
    exit /b 1
)

echo Starting server on http://localhost:8000
echo WebSocket available at ws://localhost:8000/ws/notifications/
echo.
echo Press Ctrl+C to stop the server
echo.

daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application


