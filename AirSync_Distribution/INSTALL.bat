@echo off
echo =========================================
echo AirSync - Hand Gesture Gaming Controller
echo =========================================
echo.
echo Welcome to AirSync installer!
echo This will set up everything you need to use hand gesture controls in racing games.
echo.
pause

echo 🔍 Checking system requirements...

REM Check if Python is installed
if %ERRORLEVEL% neq 0 (
    echo ❌ Python not found!
    echo.
    echo Please install Python 3.7+ from: https://python.org/downloads
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
echo ✓ Python found

echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install Python dependencies!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo ✓ Python dependencies installed

echo 📹 Testing camera access...
python -c "import cv2; cap = cv2.VideoCapture^(0^); print^('Camera test:', 'PASSED' if cap.read^(^)[0] else 'FAILED'^); cap.release^(^)"

echo ✅ Installation completed!
echo.
echo To start AirSync:
echo 1. Double-click "AirSync.exe" 
echo 2. Or run "start_airsync.bat"
echo.
echo 📖 Read USER_GUIDE.md for detailed instructions
echo.
pause
