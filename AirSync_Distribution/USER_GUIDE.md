# 🎮 AirSync Gaming Controller - User Guide

## Quick Start

### 1. First Time Setup

```batch
# Run setup to install requirements
setup.bat

# Build the application
build.bat

# Start the application
start.bat
```

### 2. Using the Application

#### Main Interface

- **START Button**: Begin hand gesture detection
- **STOP Button**: Stop gesture detection
- **Check Dependencies**: Verify Python packages
- **Install Dependencies**: Install required Python packages
- **Application Log**: View real-time status and debug info

#### System Status Indicators

- 🟢 **Green Circle**: System running normally
- 🟡 **Orange Circle**: Ready to start / Stopped
- 🔴 **Red Circle**: Error occurred

### 3. Hand Gesture Controls

#### Steering

- Hold both hands as if gripping a steering wheel
- Rotate hands left/right to steer
- The app will calibrate your neutral position automatically

#### Acceleration & Braking

- **Both Thumbs UP**: Idle/Coast (no input)
- **Left Thumb UP + Right Thumb DOWN**: Accelerate
- **Left Thumb DOWN + Right Thumb UP**: Brake
- **Both Thumbs DOWN**: Handbrake/Emergency brake

#### Additional Controls

- **Left Index Finger UP**: A Button (for menu navigation)
- **ESC Key**: Exit the Python detection window

### 4. Calibration Process

When you click START:

1. **Calibration Phase**: Hold hands in comfortable steering position
2. **Progress Bar**: Shows calibration progress (0-100%)
3. **Completion**: System learns your neutral hand position
4. **Active Phase**: Begin controlling your game

### 5. Troubleshooting

#### Common Issues

**❌ Python not found**

- Install Python 3.7+ from https://python.org
- Make sure "Add to PATH" is checked during installation
- Restart command prompt after installation

**❌ Camera not working**

- Check camera permissions in Windows Settings
- Close other applications using the camera
- Try a different USB port for external cameras
- Update camera drivers

**❌ Game not responding**

- Ensure your game supports Xbox controllers
- Check game controller settings
- Try starting the game after AirSync is running
- Some games may need to be restarted to detect the virtual controller

**❌ Poor hand tracking**

- Improve lighting (avoid backlighting)
- Keep hands within camera frame
- Remove background clutter
- Ensure good contrast between hands and background

**❌ Jerky/Unstable control**

- Adjust STEERING_SENSITIVITY in test.py (lower = less sensitive)
- Increase DEAD_ZONE for more stability
- Ensure steady hand movements

#### Performance Tips

- **Lighting**: Use good, even lighting from the front
- **Camera Position**: Place camera at eye level when hands are in driving position
- **Background**: Use a plain background behind your hands
- **Hand Position**: Keep hands clearly visible and separated
- **Clothing**: Avoid wearing gloves or jewelry that might interfere

### 6. Advanced Configuration

#### Modifying Settings

Edit `test.py` to adjust these parameters:

```python
# Sensitivity and response
STEERING_SENSITIVITY = 3.0      # Higher = more sensitive steering
DEAD_ZONE = 5.0                # Degrees to ignore (prevents jitter)
WHEEL_ROTATION_SMOOTHING = 0.8  # Smoothing factor (0-1)

# Detection thresholds
THUMB_EXTENSION_THRESHOLD = 0.08   # Thumb up/down sensitivity
FINGER_EXTENSION_THRESHOLD = 0.1   # Index finger detection

# Calibration
CALIBRATION_FRAMES = 60         # Frames for neutral position learning
```

#### Game Compatibility

AirSync emulates an Xbox 360 controller with these mappings:

- **Left Joystick X-Axis**: Steering
- **Right Trigger**: Acceleration
- **Left Trigger**: Brake
- **Y Button**: Handbrake
- **A Button**: Menu/Action button

### 7. Supported Games

#### Tested Racing Games

- **Forza Horizon Series**: Full compatibility
- **Forza Motorsport Series**: Full compatibility
- **Need for Speed Series**: Most titles supported
- **F1 Games**: Full compatibility
- **Dirt Rally**: Full compatibility
- **Project CARS**: Full compatibility
- **Assetto Corsa**: Full compatibility

#### Setup for Specific Games

1. Start AirSync first
2. Launch your racing game
3. Go to controller settings in game
4. Select "Xbox 360 Controller" or similar
5. Map controls if needed (usually automatic)

### 8. Technical Information

#### System Requirements

- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.7 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Camera**: USB webcam or built-in camera (720p or higher recommended)
- **CPU**: Multi-core processor recommended for real-time processing

#### File Structure

```
AirSync_.net/
├── AirSync.exe         # Main application (after building)
├── test.py            # Python gesture detection script
├── requirements.txt   # Python dependencies
├── setup.bat         # System requirements checker
├── build.bat         # Application builder
├── start.bat         # Quick launcher
└── README.md         # Documentation
```

### 9. Getting Help

#### Debug Information

- Check the **Application Log** in the main window
- Look for error messages in red
- Green messages indicate normal operation
- Orange messages are warnings or status updates

#### Contact & Support

- Check GitHub issues for common problems
- Submit bug reports with log information
- Include system specifications when reporting issues

### 10. Tips for Best Experience

#### Hand Positioning

- Keep hands about 12-18 inches from camera
- Maintain natural driving position
- Avoid crossing hands or blocking view
- Keep thumbs clearly visible

#### Environmental Setup

- Use consistent lighting
- Minimize background movement
- Position camera at steering wheel height
- Ensure stable camera mounting

#### Gaming Setup

- Start AirSync before your game
- Test controls in game settings first
- Adjust game sensitivity settings as needed
- Practice with simple driving games first

---

## 🏁 Happy Gaming!

Enjoy the future of gaming with natural hand gesture controls. Remember, practice makes perfect - you'll get more accurate and comfortable with the controls over time!
