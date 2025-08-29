"""
Advanced Hand Simulator Controller
Includes calibration, rotation tracking, improved gesture detection, and multi-hand support
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import math
from keyinput import press_key, release_key, mouse_click, mouse_release, mouse_move, release_all

class AdvancedHandSimulatorController:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Create hands object with improved settings
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6,
            model_complexity=1
        )
        
        # Calibration values
        self.calibration = {
            'min_x': 0.0,
            'max_x': 1.0,
            'min_y': 0.0,
            'max_y': 1.0,
            'min_z': -0.2,
            'max_z': 0.2,
            'is_calibrated': False,
            'samples': []
        }
        
        # Key mappings based on Hand Simulator image
        self.controls = {
            'movement': {
                'up': 'up',
                'down': 'down', 
                'left': 'left',
                'right': 'right'
            },
            'fingers': {
                'thumb': 'space',
                'index': 'f',
                'middle': 'd',
                'ring': 's',  # Corrected from 'g' to 's' per image
                'pinky': 'a'
            },
            'special': {
                'fist': 'left_click',
                'rotation': 'right_click',
                'hand_switch': 'shift',
            }
        }
        
        # Tracking data
        self.active_keys = set()
        self.active_hand = "right"  # Default to right hand
        self.prev_hand_pos = None
        
        # Movement smoothing values
        self.movement_history = []
        self.movement_history_max = 5
        self.smoothing_factor = 0.6
        
        # Rotation tracking
        self.prev_rotation = 0
        self.rotation_history = []
        self.wrist_base = None  # For tracking rotation
        
        # Debug mode
        self.debug_mode = False
    
    def calibrate(self, max_samples=30):
        """Calibration process to set up hand tracking boundaries"""
        print("Starting calibration process...")
        print("Please move your hand through its full range of motion")
        print("Hold your hand in front of the camera and move it around")
        
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        samples = []
        start_time = time.time()
        sample_interval = 0.1  # Sample every 100ms
        last_sample_time = 0
        
        # Reset calibration
        self.calibration['samples'] = []
        self.calibration['is_calibrated'] = False
        
        while len(samples) < max_samples:
            # Calculate progress
            progress = min(100, int((len(samples) / max_samples) * 100))
            
            ret, frame = cap.read()
            if not ret:
                continue
                
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            # Draw progress bar
            cv2.rectangle(frame, (20, h-60), (620, h-40), (0, 0, 0), -1)
            cv2.rectangle(frame, (20, h-60), (20 + int(600 * progress/100), h-40), (0, 255, 0), -1)
            cv2.putText(frame, f"Calibration Progress: {progress}%", (20, h-70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if results.multi_hand_landmarks:
                # Only sample at intervals
                current_time = time.time() - start_time
                if current_time - last_sample_time >= sample_interval:
                    # Get hand landmarks
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw landmarks
                        self.mp_drawing.draw_landmarks(
                            frame, 
                            hand_landmarks, 
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing_styles.get_default_hand_landmarks_style(),
                            self.mp_drawing_styles.get_default_hand_connections_style())
                        
                        # Extract and store landmarks for calibration
                        wrist = hand_landmarks.landmark[0]
                        mcp_points = [hand_landmarks.landmark[i] for i in [5, 9, 13, 17]]
                        
                        # Store x, y, z coordinates
                        samples.append({
                            'wrist': {'x': wrist.x, 'y': wrist.y, 'z': wrist.z},
                            'mcp': [{'x': p.x, 'y': p.y, 'z': p.z} for p in mcp_points]
                        })
                    
                    last_sample_time = current_time
            
            # Show instructions
            cv2.putText(frame, "Move your hand around naturally", (20, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Try different positions and rotations", (20, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            cv2.imshow('Hand Calibration', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Process calibration data
        if samples:
            # Find min/max values for each dimension
            min_x, max_x = float('inf'), float('-inf')
            min_y, max_y = float('inf'), float('-inf')
            min_z, max_z = float('inf'), float('-inf')
            
            for sample in samples:
                wrist = sample['wrist']
                min_x = min(min_x, wrist['x'])
                max_x = max(max_x, wrist['x'])
                min_y = min(min_y, wrist['y'])
                max_y = max(max_y, wrist['y'])
                min_z = min(min_z, wrist['z'])
                max_z = max(max_z, wrist['z'])
            
            # Add padding to boundaries (10%)
            x_pad = (max_x - min_x) * 0.1
            y_pad = (max_y - min_y) * 0.1
            z_pad = (max_z - min_z) * 0.1
            
            self.calibration = {
                'min_x': min_x - x_pad,
                'max_x': max_x + x_pad,
                'min_y': min_y - y_pad,
                'max_y': max_y + y_pad,
                'min_z': min_z - z_pad,
                'max_z': max_z + z_pad,
                'is_calibrated': True,
                'samples': samples
            }
            
            print("Calibration completed successfully!")
            print(f"X range: {self.calibration['min_x']:.2f} to {self.calibration['max_x']:.2f}")
            print(f"Y range: {self.calibration['min_y']:.2f} to {self.calibration['max_y']:.2f}")
            print(f"Z range: {self.calibration['min_z']:.2f} to {self.calibration['max_z']:.2f}")
            return True
        
        print("Calibration failed - not enough samples")
        return False
    
    def get_finger_states(self, landmarks, is_right_hand=True):
        """
        Advanced finger state detection
        Returns: Array of 5 binary values [thumb, index, middle, ring, pinky]
        """
        fingers = []
        
        # Adjust for left/right hand
        if is_right_hand:
            # Thumb - check if thumb tip is to the right of thumb IP
            if landmarks[4].x > landmarks[3].x:
                fingers.append(1)  # Extended
            else:
                fingers.append(0)  # Closed
        else:
            # For left hand, thumb is extended when x is less than thumb IP
            if landmarks[4].x < landmarks[3].x:
                fingers.append(1)  # Extended
            else:
                fingers.append(0)  # Closed
        
        # For other fingers, use more robust detection by comparing:
        # - PIP to MCP joints (knuckle to mid-joint)
        # - TIP to PIP joints (tip to mid-joint)
        # This helps with partially bent fingers
        
        # Finger landmarks: tip, pip, mcp
        finger_landmarks = [
            [8, 6, 5],   # Index
            [12, 10, 9], # Middle
            [16, 14, 13], # Ring
            [20, 18, 17]  # Pinky
        ]
        
        for finger_points in finger_landmarks:
            tip, pip, mcp = [landmarks[i] for i in finger_points]
            
            # Get finger straightness by checking if tip is higher than pip
            if tip.y < pip.y:
                fingers.append(1)  # Extended
            else:
                fingers.append(0)  # Closed
                
        return fingers
    
    def detect_rotation(self, landmarks):
        """
        Detect wrist rotation
        Returns: rotation angle in degrees (0-360)
        """
        # Get index and pinky MCP points (knuckles)
        index_mcp = landmarks[5]
        pinky_mcp = landmarks[17]
        
        # Calculate angle between these points (hand rotation)
        dx = pinky_mcp.x - index_mcp.x
        dy = pinky_mcp.y - index_mcp.y
        
        # Calculate angle in degrees (0-360)
        angle = math.degrees(math.atan2(dy, dx)) % 360
        
        # Smooth rotation
        self.rotation_history.append(angle)
        if len(self.rotation_history) > 5:
            self.rotation_history.pop(0)
        
        # Use median for stable rotation
        rotation = np.median(self.rotation_history)
        
        return rotation
    
    def normalize_position(self, pos):
        """Normalize position using calibration data"""
        if not self.calibration['is_calibrated']:
            return pos
        
        x = (pos[0] - self.calibration['min_x']) / (self.calibration['max_x'] - self.calibration['min_x'])
        y = (pos[1] - self.calibration['min_y']) / (self.calibration['max_y'] - self.calibration['min_y'])
        z = (pos[2] - self.calibration['min_z']) / (self.calibration['max_z'] - self.calibration['min_z'])
        
        # Clamp values
        x = max(0.0, min(1.0, x))
        y = max(0.0, min(1.0, y))
        z = max(0.0, min(1.0, z))
        
        return [x, y, z]
    
    def apply_controls(self, gestures, hand_pos=None, rotation=None):
        """Apply detected gestures to game controls"""
        
        # Clear previous keys that are no longer active
        for key in list(self.active_keys):
            if key in ['left_click', 'right_click']:
                mouse_release(key)
            else:
                release_key(key)
        self.active_keys.clear()
        
        # Apply finger controls with thumb working oppositely from other fingers
        fingers = gestures.get('fingers', {})
        
        # Handle thumb separately - press when OPEN (1) [OPPOSITE LOGIC]
        if 'thumb' in fingers and fingers['thumb'] == 1:  # Thumb is OPEN
            key = self.controls['fingers']['thumb']
            press_key(key)
            self.active_keys.add(key)
        
        # Handle other fingers - press when CLOSED (0) [SAME AS BEFORE]
        other_fingers = ['index', 'middle', 'ring', 'pinky']
        for finger_name in other_fingers:
            if finger_name in fingers and fingers[finger_name] == 0:  # Finger is CLOSED
                key = self.controls['fingers'][finger_name]
                press_key(key)
                self.active_keys.add(key)
        
        # Apply special gestures
        special = gestures.get('special')
        if special:
            if special == 'fist':
                mouse_click('left_click')
                self.active_keys.add('left_click')
            elif special == 'rotation':
                mouse_click('right_click') 
                self.active_keys.add('right_click')
            elif special == 'hand_switch':
                press_key(self.controls['special']['hand_switch'])
                self.active_keys.add(self.controls['special']['hand_switch'])
        
        # Apply mouse movement if hand position is provided
        if hand_pos:
            # Only move if we have previous position to compare
            if self.prev_hand_pos:
                # Map hand movements to mouse axes based on requirements
                # X axis: Horizontal movement (side to side)
                dx = (hand_pos[0] - self.prev_hand_pos[0]) * 1000
                
                # Y axis: Z movement (depth - towards/away from camera)
                dy = (hand_pos[2] - self.prev_hand_pos[2]) * 1000
                
                # Wheel: Y movement (up and down)
                wheel = (self.prev_hand_pos[1] - hand_pos[1]) * 500
                
                # Add to history for smoothing
                self.movement_history.append((dx, dy, wheel))
                if len(self.movement_history) > self.movement_history_max:
                    self.movement_history.pop(0)
                
                # Apply smoothing by averaging recent movements
                if self.movement_history:
                    dx = sum(m[0] for m in self.movement_history) / len(self.movement_history)
                    dy = sum(m[1] for m in self.movement_history) / len(self.movement_history)
                    wheel = sum(m[2] for m in self.movement_history) / len(self.movement_history)
                
                # Apply smoothing factor
                dx *= self.smoothing_factor
                dy *= self.smoothing_factor
                wheel *= self.smoothing_factor
                
                # Move mouse if movement is significant
                if abs(dx) > 1 or abs(dy) > 1:
                    mouse_move(dx, dy)
                
                # Scroll if movement is significant
                if abs(wheel) > 1:
                    mouse_move(0, 0, wheel)
            
            # Update previous position
            self.prev_hand_pos = hand_pos
    
    def run(self):
        """Main control loop"""
        # Start with calibration
        if not self.calibration['is_calibrated']:
            self.calibrate()
        
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("Advanced Hand Simulator Controller")
        print("Controls:")
        print("- Move hand horizontally for X-axis movement")
        print("- Move hand toward/away from camera for Y-axis movement")
        print("- Move hand up/down for scrolling")
        print("- CLOSE fingers for control: Thumb=Space, Index=F, Middle=D, Ring=S, Pinky=A") 
        print("- Close all fingers (fist) for Left Mouse Click")
        print("- Press 'd' to toggle debug mode")
        print("- Press 'c' to recalibrate")
        print("- Press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
                
            # Flip frame horizontally
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            
            # Convert to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            gestures = {
                'fingers': {},
                'special': None
            }
            
            hand_pos = None
            rotation = None
            
            if results.multi_hand_landmarks and results.multi_handedness:
                # Find the most prominent hand (closest to camera or with larger area)
                main_hand_idx = 0
                if len(results.multi_hand_landmarks) > 1:
                    # Use the hand with larger bounding box as main hand
                    sizes = []
                    for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        x_coords = [landmark.x for landmark in hand_landmarks.landmark]
                        y_coords = [landmark.y for landmark in hand_landmarks.landmark]
                        x_min, x_max = min(x_coords), max(x_coords)
                        y_min, y_max = min(y_coords), max(y_coords)
                        size = (x_max - x_min) * (y_max - y_min)
                        sizes.append((size, i))
                    main_hand_idx = max(sizes)[1]
                
                # Get main hand
                hand_landmarks = results.multi_hand_landmarks[main_hand_idx]
                handedness = results.multi_handedness[main_hand_idx]
                is_right_hand = (handedness.classification[0].label == "Right")
                hand_type = "right" if is_right_hand else "left"
                
                # Draw landmarks with different styles based on debug mode
                if self.debug_mode:
                    self.mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())
                else:
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Get wrist position
                wrist = hand_landmarks.landmark[0]
                raw_pos = [wrist.x, wrist.y, wrist.z]
                
                # Apply calibration if available
                if self.calibration['is_calibrated']:
                    hand_pos = self.normalize_position(raw_pos)
                else:
                    hand_pos = raw_pos
                
                # Get rotation
                rotation = self.detect_rotation(hand_landmarks.landmark)
                
                # Hand switch detection
                if self.active_hand != hand_type:
                    gestures['special'] = 'hand_switch'
                    self.active_hand = hand_type
                
                # Get finger states
                finger_states = self.get_finger_states(hand_landmarks.landmark, is_right_hand)
                gestures['fingers'] = {
                    'thumb': finger_states[0],
                    'index': finger_states[1], 
                    'middle': finger_states[2],
                    'ring': finger_states[3],
                    'pinky': finger_states[4]
                }
                
                # Check for special gestures
                # Fist: all fingers closed (0)
                if not any(finger_states):
                    gestures['special'] = 'fist'
                
                # Apply controls
                self.apply_controls(gestures, hand_pos, rotation)
                
                # Display current state
                y_pos = 30
                cv2.putText(frame, f"Hand Simulator: {hand_type.upper()} HAND", 
                           (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y_pos += 30
                
                # Show which fingers are closed (these are the active ones)
                closed_fingers = [name for name, state in gestures['fingers'].items() if state == 0]
                if closed_fingers:
                    finger_text = "Active fingers: " + ", ".join(closed_fingers)
                    cv2.putText(frame, finger_text, (10, y_pos), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    y_pos += 25
                
                if gestures['special']:
                    cv2.putText(frame, f"Special: {gestures['special']}", (10, y_pos), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                    y_pos += 25
                
                # Show rotation
                if rotation is not None:
                    cv2.putText(frame, f"Rotation: {rotation:.1f}°", (10, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
                    y_pos += 25
                
                # Show debug info
                if self.debug_mode and hand_pos:
                    pos_text = f"Position: X:{hand_pos[0]:.2f} Y:{hand_pos[1]:.2f} Z:{hand_pos[2]:.2f}"
                    cv2.putText(frame, pos_text, (10, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            else:
                # No hands detected - release all keys
                release_all()
                self.active_keys.clear()
                self.prev_hand_pos = None
                
                cv2.putText(frame, "No hands detected", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Show help
            cv2.putText(frame, "D: Debug | C: Calibrate | Q: Quit", (10, h-20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Show calibration status
            if self.calibration['is_calibrated']:
                cv2.putText(frame, "Calibrated", (w-100, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            else:
                cv2.putText(frame, "Not Calibrated", (w-150, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            cv2.imshow('Advanced Hand Simulator Controller', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('d'):
                self.debug_mode = not self.debug_mode
                print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
            elif key == ord('c'):
                print("Recalibrating...")
                self.calibrate()
        
        # Clean up
        release_all()
        self.active_keys.clear()
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    controller = AdvancedHandSimulatorController()
    controller.run()