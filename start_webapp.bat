@echo off
echo ============================================================
echo RiskIQ Web Application Startup
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "backend\api\app.py" (
    echo Error: Please run this script from the project root directory
    echo Expected structure: Project_2_RiskIQ\start_webapp.bat
    pause
    exit /b 1
)

if not exist "frontend\index.html" (
    echo Error: Frontend files not found
    echo Please ensure frontend\ directory exists with index.html
    pause
    exit /b 1
)

echo Starting RiskIQ Web Application...
echo.
echo Backend API will run on: http://localhost:8000
echo Frontend will run on: http://localhost:3000
echo.
echo Press Ctrl+C to stop both servers
echo.

python start_webapp.py

pause
