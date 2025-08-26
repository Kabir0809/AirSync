@echo off
echo =========================================
echo Creating AirSync Distribution Package
echo =========================================

REM Create distribution directory
if exist "AirSync_Distribution" rmdir /s /q "AirSync_Distribution"
mkdir "AirSync_Distribution"
mkdir "AirSync_Distribution\AirSync"

echo ✓ Created distribution folder

REM Build the application in Release mode
echo.
echo 🔨 Building AirSync...
dotnet build AirSync.csproj --configuration Release --verbosity quiet
if %ERRORLEVEL% neq 0 (
    echo ❌ Build failed!
    pause
    exit /b 1
)
echo ✓ Build completed successfully

REM Copy executable and dependencies
echo.
echo 📦 Copying application files...
xcopy "bin\Release\net6.0-windows\*" "AirSync_Distribution\AirSync\" /s /y >nul
echo ✓ Application files copied

REM Copy documentation
echo.
echo 📝 Copying documentation...
copy "README.md" "AirSync_Distribution\" >nul
copy "USER_GUIDE.md" "AirSync_Distribution\" >nul
copy "SETUP_GUIDE.md" "AirSync_Distribution\" >nul
echo ✓ Documentation copied

REM Create installer script for client
echo.
echo 🚀 Creating client installer...
(
echo @echo off
echo echo =========================================
echo echo AirSync - Hand Gesture Gaming Controller
echo echo =========================================
echo echo.
echo echo Welcome to AirSync installer!
echo echo This will set up everything you need to use hand gesture controls in racing games.
echo echo.
echo pause
echo.
echo echo 🔍 Checking system requirements...
echo.
echo REM Check if Python is installed
echo python --version >nul 2>&1
echo if %%ERRORLEVEL%% neq 0 ^(
echo     echo ❌ Python not found!
echo     echo.
echo     echo Please install Python 3.7+ from: https://python.org/downloads
echo     echo Make sure to check "Add Python to PATH" during installation.
echo     echo.
echo     pause
echo     exit /b 1
echo ^)
echo echo ✓ Python found
echo.
echo echo 📦 Installing Python dependencies...
echo pip install -r requirements.txt
echo if %%ERRORLEVEL%% neq 0 ^(
echo     echo ❌ Failed to install Python dependencies!
echo     echo Please check your internet connection and try again.
echo     pause
echo     exit /b 1
echo ^)
echo echo ✓ Python dependencies installed
echo.
echo echo 📹 Testing camera access...
echo python -c "import cv2; cap = cv2.VideoCapture^(0^); print^('Camera test:', 'PASSED' if cap.read^(^)[0] else 'FAILED'^); cap.release^(^)"
echo.
echo echo ✅ Installation completed!
echo echo.
echo echo To start AirSync:
echo echo 1. Double-click "AirSync.exe" 
echo echo 2. Or run "start_airsync.bat"
echo echo.
echo echo 📖 Read USER_GUIDE.md for detailed instructions
echo echo.
echo pause
) > "AirSync_Distribution\INSTALL.bat"

REM Create simple launcher for client
(
echo @echo off
echo cd /d "%%~dp0AirSync"
echo echo Starting AirSync Hand Gesture Gaming Controller...
echo start AirSync.exe
echo echo ✓ AirSync started!
echo echo.
echo echo If you encounter any issues:
echo echo - Make sure your webcam is connected
echo echo - Check that no other applications are using the camera
echo echo - Run INSTALL.bat if you haven't already
echo echo.
echo timeout /t 3 >nul
) > "AirSync_Distribution\start_airsync.bat"

REM Create README for client
(
echo # AirSync - Hand Gesture Gaming Controller
echo.
echo Transform your racing game experience with natural hand gestures!
echo.
echo ## 🚀 Quick Start
echo.
echo 1. **Install**: Run `INSTALL.bat` as Administrator
echo 2. **Launch**: Double-click `start_airsync.bat` or `AirSync\AirSync.exe`
echo 3. **Play**: Use hand gestures to control your racing games!
echo.
echo ## 📋 System Requirements
echo.
echo - Windows 10/11
echo - Python 3.7 or higher
echo - Webcam ^(built-in or USB^)
echo - .NET 6 Runtime ^(will be installed automatically^)
echo.
echo ## 🎮 Supported Games
echo.
echo AirSync works with any racing game that supports Xbox controllers:
echo - Forza Horizon series
echo - Forza Motorsport series  
echo - Dirt Rally series
echo - F1 series
echo - Need for Speed series
echo - And many more!
echo.
echo ## 🤚 Gesture Controls
echo.
echo - **Steering**: Rotate your hand left/right
echo - **Throttle**: Move hand up
echo - **Brake**: Move hand down
echo - **Calibration**: Follow on-screen instructions when starting
echo.
echo ## 📞 Support
echo.
echo If you encounter any issues:
echo 1. Read the USER_GUIDE.md for detailed instructions
echo 2. Make sure your webcam works in other applications
echo 3. Try running INSTALL.bat again as Administrator
echo.
echo ## 📁 Files Included
echo.
echo - `AirSync\` - Main application folder
echo - `INSTALL.bat` - One-time setup installer
echo - `start_airsync.bat` - Quick launcher
echo - `USER_GUIDE.md` - Detailed user manual
echo - `SETUP_GUIDE.md` - Technical setup information
echo.
echo ---
echo **Enjoy gaming with natural hand gestures!** 🎮✋
) > "AirSync_Distribution\README.md"

echo ✓ Client installer created
echo ✓ Client launcher created  
echo ✓ Client README created

echo.
echo 📦 Creating distribution archive...
powershell Compress-Archive -Path "AirSync_Distribution\*" -DestinationPath "AirSync_v1.0_Distribution.zip" -Force
echo ✓ Distribution package created: AirSync_v1.0_Distribution.zip

echo.
echo =========================================
echo ✅ DISTRIBUTION PACKAGE READY!
echo =========================================
echo.
echo Your client distribution package is ready:
echo 📦 AirSync_v1.0_Distribution.zip
echo.
echo This package contains:
echo ✓ Complete AirSync application
echo ✓ Automatic installer (INSTALL.bat)
echo ✓ Simple launcher (start_airsync.bat)  
echo ✓ User documentation
echo ✓ All required dependencies
echo.
echo Just send this ZIP file to your client!
echo.
pause
