"""
Keyboard and mouse input module for Hand Simulator Controller
Provides cross-platform key press, release, and mouse control functionality
"""

try:
    from pynput.keyboard import Key, Controller as KeyboardController
    from pynput.mouse import Button, Controller as MouseController
    import time
    PYNPUT_AVAILABLE = True
except ImportError:
    print("Warning: pynput not installed. Install with: pip install pynput")
    PYNPUT_AVAILABLE = False

class InputController:
    def __init__(self):
        if PYNPUT_AVAILABLE:
            self.keyboard = KeyboardController()
            self.mouse = MouseController()
        else:
            self.keyboard = None
            self.mouse = None
        
        # Key mapping for string keys to pynput Key objects
        self.key_map = {
            # Arrow keys
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            
            # Special keys
            'space': Key.space,
            'enter': Key.enter,
            'esc': Key.esc,
            'ctrl': Key.ctrl_l,
            'alt': Key.alt_l,
            'shift': Key.shift_l,
            'tab': Key.tab,
            'backspace': Key.backspace,
            'delete': Key.delete,
            
            # Function keys
            'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
            'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
            'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
        }
        
        # Mouse button mapping
        self.mouse_map = {
            'left_click': Button.left,
            'right_click': Button.right,
            'middle_click': Button.middle
        }
        
        # Currently pressed keys
        self.pressed_keys = set()
        self.pressed_mouse_buttons = set()
    
    def _get_key(self, key_str):
        """Convert string key to appropriate key object"""
        if not PYNPUT_AVAILABLE:
            return None
            
        key_str = str(key_str).lower()
        
        # Check if it's a special key
        if key_str in self.key_map:
            return self.key_map[key_str]
        
        # For single character keys, return as string
        if len(key_str) == 1:
            return key_str
        
        # Return as string for other cases
        return key_str
    
    def press_key(self, key_str):
        """Press and hold a key"""
        if not PYNPUT_AVAILABLE or self.keyboard is None:
            print(f"Cannot press key '{key_str}' - pynput not available")
            return False
        
        try:
            key = self._get_key(key_str)
            if key and key_str not in self.pressed_keys:
                self.keyboard.press(key)
                self.pressed_keys.add(key_str)
                return True
        except Exception as e:
            print(f"Error pressing key '{key_str}': {e}")
        return False
    
    def release_key(self, key_str):
        """Release a key"""
        if not PYNPUT_AVAILABLE or self.keyboard is None:
            print(f"Cannot release key '{key_str}' - pynput not available")
            return False
        
        try:
            key = self._get_key(key_str)
            if key and key_str in self.pressed_keys:
                self.keyboard.release(key)
                self.pressed_keys.discard(key_str)
                return True
        except Exception as e:
            print(f"Error releasing key '{key_str}': {e}")
        return False
    
    def tap_key(self, key_str, duration=0.1):
        """Press and release a key with optional duration"""
        if self.press_key(key_str):
            time.sleep(duration)
            self.release_key(key_str)
            return True
        return False
    
    def mouse_click(self, button='left_click'):
        """Press and hold a mouse button"""
        if not PYNPUT_AVAILABLE or self.mouse is None:
            print(f"Cannot click mouse '{button}' - pynput not available")
            return False
        
        try:
            btn = self.mouse_map.get(button, Button.left)
            if button not in self.pressed_mouse_buttons:
                self.mouse.press(btn)
                self.pressed_mouse_buttons.add(button)
                return True
        except Exception as e:
            print(f"Error clicking mouse '{button}': {e}")
        return False
    
    def mouse_release(self, button='left_click'):
        """Release a mouse button"""
        if not PYNPUT_AVAILABLE or self.mouse is None:
            print(f"Cannot release mouse '{button}' - pynput not available")
            return False
        
        try:
            btn = self.mouse_map.get(button, Button.left)
            if button in self.pressed_mouse_buttons:
                self.mouse.release(btn)
                self.pressed_mouse_buttons.discard(button)
                return True
        except Exception as e:
            print(f"Error releasing mouse '{button}': {e}")
        return False
    
    def mouse_move(self, dx, dy, wheel=0):
        """Move mouse by delta x, y and scroll wheel"""
        if not PYNPUT_AVAILABLE or self.mouse is None:
            return False
        
        try:
            if dx != 0 or dy != 0:
                self.mouse.move(dx, dy)
            
            if wheel != 0:
                self.mouse.scroll(0, wheel)
            return True
        except Exception as e:
            print(f"Error moving mouse: {e}")
        return False
    
    def release_all(self):
        """Release all currently pressed keys and mouse buttons"""
        # Release all keys
        for key_str in list(self.pressed_keys):
            self.release_key(key_str)
        
        # Release all mouse buttons
        for button in list(self.pressed_mouse_buttons):
            self.mouse_release(button)

# Global controller instance
_input_controller = InputController()

# Public API functions
def press_key(key_str):
    """Press and hold a key"""
    return _input_controller.press_key(key_str)

def release_key(key_str):
    """Release a key"""
    return _input_controller.release_key(key_str)

def tap_key(key_str, duration=0.1):
    """Press and release a key with optional duration"""
    return _input_controller.tap_key(key_str, duration)

def mouse_click(button='left_click'):
    """Press and hold a mouse button"""
    return _input_controller.mouse_click(button)

def mouse_release(button='left_click'):
    """Release a mouse button"""
    return _input_controller.mouse_release(button)

def mouse_move(dx, dy, wheel=0):
    """Move mouse by delta x, y and scroll wheel"""
    return _input_controller.mouse_move(dx, dy, wheel)

def release_all():
    """Release all currently pressed keys and buttons"""
    _input_controller.release_all()

def is_available():
    """Check if input control is available"""
    return PYNPUT_AVAILABLE

# Test function
def test_keys():
    """Test keyboard and mouse functionality"""
    if not is_available():
        print("Input control not available - install pynput")
        return
    
    print("Testing keyboard and mouse functionality...")
    print("This will press keys and move the mouse in 3 seconds...")
    time.sleep(3)
    
    # Test keyboard
    test_keys = ['a', 'space', 'up', 'down', 'left', 'right']
    for key in test_keys:
        print(f"Testing key: {key}")
        tap_key(key, 0.2)
        time.sleep(0.5)
    
    # Test mouse
    print("Testing mouse movement...")
    for i in range(4):
        # Move in a small square
        mouse_move(50, 0)
        time.sleep(0.2)
        mouse_move(0, 50)
        time.sleep(0.2)
        mouse_move(-50, 0)
        time.sleep(0.2)
        mouse_move(0, -50)
        time.sleep(0.2)
    
    # Test mouse clicks
    print("Testing mouse clicks...")
    mouse_click('left_click')
    time.sleep(0.5)
    mouse_release('left_click')
    time.sleep(0.5)
    
    mouse_click('right_click')
    time.sleep(0.5)
    mouse_release('right_click')
    
    print("Input test complete!")

if __name__ == "__main__":
    test_keys()