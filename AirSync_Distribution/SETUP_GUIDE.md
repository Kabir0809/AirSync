# 🚀 AirSync Gaming Controller - Complete Setup Guide

## Overview

AirSync is a hand gesture gaming controller that lets you control racing games with natural hand movements. You have two options to run it:

1. **Option A**: Full GUI Application (requires .NET SDK)
2. **Option B**: Direct Python Script (immediate use)

---

## 🎯 Option A: Full GUI Application (Recommended)

### Step 1: Install Prerequisites

#### Install .NET 6 SDK

1. Go to: https://dotnet.microsoft.com/download/dotnet/6.0
2. Download: ".NET 6.0 SDK" for Windows x64
3. Run installer and follow prompts
4. Restart command prompt after installation

#### Install Python 3.7+ (if not already installed)

1. Go to: https://python.org/downloads/
2. Download latest Python 3.x for Windows
3. **IMPORTANT**: Check "Add to PATH" during installation
4. Restart command prompt after installation

### Step 2: Setup and Build

```batch
# Check system requirements
setup.bat

# Build the GUI application
build.bat

# Run the application
start.bat
```

### Step 3: Use the GUI

- Modern Material Design interface
- Start/Stop buttons
- Real-time status monitoring
- Dependency management
- Application logs

---

## ⚡ Option B: Direct Python Script (Quick Start)

### Step 1: Verify Requirements

```batch
# Test Python availability
python --version

# Check if packages are installed
python -c "import cv2, mediapipe, numpy, vgamepad"
```

### Step 2: Install Missing Packages (if needed)

```batch
pip install opencv-python mediapipe numpy vgamepad
```

### Step 3: Run Direct Demo

```batch
# Run the gesture detection directly
demo.bat
```

---

## 🎮 How to Use

### Hand Gesture Controls

| Gesture              | Action     |
| -------------------- | ---------- |
| Both thumbs UP       | Idle/Coast |
| Left UP + Right DOWN | Accelerate |
| Left DOWN + Right UP | Brake      |
| Both thumbs DOWN     | Handbrake  |
| Left index finger UP | A Button   |
| ESC key              | Exit       |

### Steering

- Hold hands like gripping a steering wheel
- Rotate left/right to steer
- Automatic calibration for your hand position

### Setup Process

1. **Launch**: Start AirSync (GUI or demo)
2. **Calibration**: Hold hands in neutral steering position
3. **Gaming**: Launch your racing game
4. **Control**: Use natural hand gestures

---

## 🎯 Game Compatibility

### Fully Tested Games

- Forza Horizon Series ✅
- Forza Motorsport Series ✅
- Need for Speed Series ✅
- F1 Games ✅
- Dirt Rally ✅
- Project CARS ✅
- Assetto Corsa ✅

### Game Setup

1. Start AirSync first
2. Launch racing game
3. Go to controller settings
4. Select "Xbox 360 Controller"
5. Controls should work automatically

---

## 🔧 Troubleshooting

### Common Issues

**Python not found**

```batch
# Install Python with PATH option
# Or manually add to PATH:
# C:\Users\[username]\AppData\Local\Programs\Python\Python310\
```

**Camera not working**

- Check Windows camera permissions
- Close other camera apps (Skype, Teams, etc.)
- Try different USB port
- Update camera drivers

**Poor hand tracking**

- Use good lighting (front-lit, avoid backlighting)
- Plain background behind hands
- Keep hands 12-18 inches from camera
- Ensure hands are clearly separated

**Game not responding**

- Ensure game supports Xbox controllers
- Start AirSync before the game
- Check game controller settings
- Restart game if needed

---

## 📁 File Structure

After setup, you'll have:

```
AirSync_.net/
├── 📱 GUI Application Files
│   ├── AirSync.exe (after building)
│   ├── MainWindow.xaml
│   └── App.xaml
├── 🐍 Python Core
│   ├── test.py (main detection script)
│   └── requirements.txt
├── 🔧 Setup Scripts
│   ├── setup.bat (system check)
│   ├── build.bat (build GUI)
│   ├── start.bat (run GUI)
│   └── demo.bat (direct Python)
└── 📚 Documentation
    ├── README.md
    ├── USER_GUIDE.md
    └── SETUP_GUIDE.md (this file)
```

---

## 🎯 Quick Commands Reference

```batch
# System setup and checking
setup.bat              # Check all requirements
python --version       # Verify Python installation
dotnet --version       # Verify .NET installation

# Running the application
build.bat              # Build GUI application
start.bat              # Run GUI application
demo.bat               # Run direct Python script

# Troubleshooting
pip install -r requirements.txt    # Install Python packages
pip list                           # Show installed packages
```

---

## 💡 Pro Tips

### For Best Performance

1. **Lighting**: Use even, front-facing light
2. **Camera**: Position at eye level when hands are in driving position
3. **Background**: Use plain wall or surface behind hands
4. **Hands**: Keep clearly visible and separated
5. **Practice**: Start with simple driving games

### Customization

Edit `test.py` to adjust:

- `STEERING_SENSITIVITY`: Control steering responsiveness
- `DEAD_ZONE`: Reduce jitter by ignoring small movements
- `CALIBRATION_FRAMES`: More frames = more accurate calibration

---

## 🏁 Ready to Race!

Choose your preferred option:

- **GUI Application**: Full-featured with modern interface
- **Direct Script**: Quick start for immediate gaming

Both provide the same hand gesture detection capabilities. The GUI adds user-friendly controls and monitoring.

Happy gaming! 🎮
