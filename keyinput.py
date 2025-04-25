import ctypes
import time

# Virtual Key Codes (VK) and scan codes for game controls
# This expanded dictionary includes both VK and scan codes for better compatibility
keys = {
    # Movement keys with both VK and scan codes
    "w": {"vk": 0x57, "scan": 0x11},  # W key
    "a": {"vk": 0x41, "scan": 0x1E},  # A key
    "s": {"vk": 0x53, "scan": 0x1F},  # S key
    "d": {"vk": 0x44, "scan": 0x20},  # D key
    
    # Additional common game controls
    "space": {"vk": 0x20, "scan": 0x39},  # Jump/Handbrake
    "shift": {"vk": 0x10, "scan": 0x2A},  # Sprint/NOS
    "ctrl": {"vk": 0x11, "scan": 0x1D},   # Crouch
    "e": {"vk": 0x45, "scan": 0x12},      # Enter/Exit vehicle
    "r": {"vk": 0x52, "scan": 0x13},      # Reload
    "f": {"vk": 0x46, "scan": 0x21},      # Enter vehicle/Interact
    "c": {"vk": 0x43, "scan": 0x2E},      # Look behind in racing games
    "x": {"vk": 0x58, "scan": 0x2D},      # Brake/Reverse alternative
    
    # Arrow keys (extended keys)
    "up": {"vk": 0x26, "scan": 0x48, "extended": True},
    "down": {"vk": 0x28, "scan": 0x50, "extended": True},
    "left": {"vk": 0x25, "scan": 0x4B, "extended": True},
    "right": {"vk": 0x27, "scan": 0x4D, "extended": True},
}

# Define constants
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

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
    """Press a keyboard key using both VK and scan code for better game compatibility"""
    if key not in keys:
        raise ValueError(f"Key '{key}' not mapped.")
    
    key_info = keys[key]
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    
    # Set flags based on whether it's an extended key
    flags = KEYEVENTF_SCANCODE
    if key_info.get("extended", False):
        flags |= KEYEVENTF_EXTENDEDKEY
    
    # Use both vk and scan code for better compatibility across games
    ii_.ki = KeyBdInput(key_info["vk"], key_info["scan"], flags, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def release_key(key):
    """Release a keyboard key using both VK and scan code for better game compatibility"""
    if key not in keys:
        raise ValueError(f"Key '{key}' not mapped.")
    
    key_info = keys[key]
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    
    # Set flags based on whether it's an extended key
    flags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP
    if key_info.get("extended", False):
        flags |= KEYEVENTF_EXTENDEDKEY
    
    # Use both vk and scan code for better compatibility across games
    ii_.ki = KeyBdInput(key_info["vk"], key_info["scan"], flags, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

# Add these additional utility functions for game control

def key_press_and_release(key, duration=0.1):
    """Press a key, hold it for the specified duration, then release it"""
    press_key(key)
    time.sleep(duration)  # Hold the key for this duration
    release_key(key)

def press_keys_combination(keys_list):
    """Press multiple keys simultaneously"""
    for key in keys_list:
        press_key(key)

def release_keys_combination(keys_list):
    """Release multiple keys that were pressed simultaneously"""
    for key in keys_list:
        release_key(key)

def tap_key(key, duration=0.1):
    """Briefly tap a key - useful for actions like changing weapons or entering vehicles"""
    key_press_and_release(key, duration)
