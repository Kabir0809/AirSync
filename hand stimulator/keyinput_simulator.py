# Enhanced keyinput module for Hand Simulator
# Includes mouse control and additional keys for Hand Simulator

import ctypes
import time

# Virtual Key Codes and scan codes for Hand Simulator controls
keys = {
    # Movement keys
    "up": {"vk": 0x26, "scan": 0x48, "extended": True},
    "down": {"vk": 0x28, "scan": 0x50, "extended": True},
    "left": {"vk": 0x25, "scan": 0x4B, "extended": True},
    "right": {"vk": 0x27, "scan": 0x4D, "extended": True},
    
    # Finger controls
    "space": {"vk": 0x20, "scan": 0x39},  # Thumb
    "f": {"vk": 0x46, "scan": 0x21},      # Index finger
    "d": {"vk": 0x44, "scan": 0x20},      # Middle finger
    "s": {"vk": 0x53, "scan": 0x1F},      # Ring finger (FIXED: changed from 'g' to 's')
    "a": {"vk": 0x41, "scan": 0x1E},      # Pinky
    
    # Special controls
    "enter": {"vk": 0x0D, "scan": 0x1C},  # Submit
    "esc": {"vk": 0x1B, "scan": 0x01},    # Cancel/Escape
    "c": {"vk": 0x43, "scan": 0x2E},      # Hold rotator
    "ctrl": {"vk": 0x11, "scan": 0x1D},   # Crouch
    "h": {"vk": 0x48, "scan": 0x23},      # Hand
    "shift": {"vk": 0x10, "scan": 0x2A}, # Left Shift
    
    # Additional game keys
    "w": {"vk": 0x57, "scan": 0x11},
    "e": {"vk": 0x45, "scan": 0x12},
    "r": {"vk": 0x52, "scan": 0x13},
    "t": {"vk": 0x54, "scan": 0x14},
    "y": {"vk": 0x59, "scan": 0x15},
    "q": {"vk": 0x51, "scan": 0x10},
    "g": {"vk": 0x47, "scan": 0x22},      # Keeping original 'g' key for other functions
    
    # Function keys
    "f1": {"vk": 0x70, "scan": 0x3B},
    "f2": {"vk": 0x71, "scan": 0x3C},
    "f3": {"vk": 0x72, "scan": 0x3D},
    "f4": {"vk": 0x73, "scan": 0x3E},
    
    # Number keys
    "1": {"vk": 0x31, "scan": 0x02},
    "2": {"vk": 0x32, "scan": 0x03},
    "3": {"vk": 0x33, "scan": 0x04},
    "4": {"vk": 0x34, "scan": 0x05},
    "5": {"vk": 0x35, "scan": 0x06},
}

# Define Windows API constants
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

# Mouse constants
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x1000

PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

def press_key(key):
    """Press a keyboard key"""
    if key == "left_click":
        mouse_click(button="left", action="down")
        return
    elif key == "right_click":
        mouse_click(button="right", action="down")
        return
    
    if key not in keys:
        print(f"Warning: Key '{key}' not mapped.")
        return
    
    key_info = keys[key]
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    
    # Set flags
    flags = KEYEVENTF_SCANCODE
    if key_info.get("extended", False):
        flags |= KEYEVENTF_EXTENDEDKEY
    
    ii_.ki = KeyBdInput(key_info["vk"], key_info["scan"], flags, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def release_key(key):
    """Release a keyboard key"""
    if key == "left_click":
        mouse_click(button="left", action="up")
        return
    elif key == "right_click":
        mouse_click(button="right", action="up")
        return
    
    if key not in keys:
        print(f"Warning: Key '{key}' not mapped.")
        return
    
    key_info = keys[key]
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    
    # Set flags for key release
    flags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP
    if key_info.get("extended", False):
        flags |= KEYEVENTF_EXTENDEDKEY
    
    ii_.ki = KeyBdInput(key_info["vk"], key_info["scan"], flags, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def mouse_click(button="left", action="down"):
    """Perform mouse click"""
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    
    if button == "left":
        if action == "down":
            flags = MOUSEEVENTF_LEFTDOWN
        else:
            flags = MOUSEEVENTF_LEFTUP
    else:  # right button
        if action == "down":
            flags = MOUSEEVENTF_RIGHTDOWN
        else:
            flags = MOUSEEVENTF_RIGHTUP
    
    ii_.mi = MouseInput(0, 0, 0, flags, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_)  # 0 for mouse input
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def mouse_move(dx, dy, wheel=0):
    """
    Move mouse relatively by dx, dy and optionally scroll wheel
    
    Args:
        dx: horizontal movement (positive = right, negative = left)
        dy: vertical movement (positive = down, negative = up)
        wheel: mouse wheel movement (positive = up/away, negative = down/toward)
    """
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    
    # First handle regular movement if needed
    if dx != 0 or dy != 0:
        flags = MOUSEEVENTF_MOVE
        ii_.mi = MouseInput(int(dx), int(dy), 0, flags, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(0), ii_)  # 0 for mouse input
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    
    # Then handle wheel if needed
    if wheel != 0:
        flags = MOUSEEVENTF_WHEEL
        wheel_amount = int(wheel)  # Positive = scroll up, negative = scroll down
        ii_.mi = MouseInput(0, 0, wheel_amount, flags, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def tap_key(key, duration=0.1):
    """Press and release a key quickly"""
    press_key(key)
    time.sleep(duration)
    release_key(key)

def hold_key(key, duration=1.0):
    """Hold a key for specified duration"""
    press_key(key)
    time.sleep(duration)
    release_key(key)

def press_key_combination(keys_list):
    """Press multiple keys simultaneously"""
    for key in keys_list:
        press_key(key)

def release_key_combination(keys_list):
    """Release multiple keys"""
    for key in keys_list:
        release_key(key)

def release_all():
    """Release all currently pressed keys and mouse buttons"""
    # Common keys to ensure are released
    important_keys = ['a', 's', 'd', 'f', 'space', 'ctrl', 'shift', 'up', 'down', 'left', 'right']
    
    for key in important_keys:
        release_key(key)
    
    # Release mouse buttons
    mouse_click("left", "up")
    mouse_click("right", "up")

def type_text(text, delay=0.05):
    """Type text by sending individual key presses"""
    for char in text:
        if char.lower() in keys:
            tap_key(char.lower(), delay)
        elif char == " ":
            tap_key("space", delay)

# Test function
def test_keys():
    """Test key functionality"""
    print("Testing Hand Simulator key mappings...")
    
    test_sequence = [
        ("space", "Thumb"),
        ("f", "Index finger"), 
        ("d", "Middle finger"),
        ("s", "Ring finger"),  # Fixed: changed from 'g' to 's'
        ("a", "Pinky"),
        ("up", "Move up"),
        ("down", "Move down"),
        ("left", "Move left"),
        ("right", "Move right"),
        ("shift", "Change hands"),
        ("enter", "Submit"),
        ("esc", "Cancel")
    ]
    
    for key, description in test_sequence:
        print(f"Testing {description} ({key})...")
        tap_key(key, 0.2)
        time.sleep(0.5)
    
    print("\nTesting mouse functions...")
    
    # Test mouse clicks
    print("Testing left click...")
    mouse_click("left", "down")
    time.sleep(0.3)
    mouse_click("left", "up")
    time.sleep(0.5)
    
    print("Testing right click...")
    mouse_click("right", "down")
    time.sleep(0.3)
    mouse_click("right", "up")
    time.sleep(0.5)
    
    # Test mouse movement
    print("Testing mouse movement (square pattern)...")
    for _ in range(4):
        mouse_move(50, 0)
        time.sleep(0.3)
        mouse_move(0, 50)
        time.sleep(0.3)
        mouse_move(-50, 0)
        time.sleep(0.3)
        mouse_move(0, -50)
        time.sleep(0.3)
    
    # Test scroll wheel
    print("Testing mouse wheel...")
    mouse_move(0, 0, 120)  # Scroll up
    time.sleep(0.5)
    mouse_move(0, 0, -120)  # Scroll down
    time.sleep(0.5)
    
    print("Key and mouse test complete!")

if __name__ == "__main__":
    test_keys()