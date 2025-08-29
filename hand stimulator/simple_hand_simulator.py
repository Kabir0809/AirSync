# Simple Hand Simulator Controller
# Basic implementation for quick testing

import cv2
import mediapipe as mp
import numpy as np
import time
from keyinput import press_key, release_key, mouse_move, mouse_click, mouse_release

class SimpleHandSimulator:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Current active keys
        self.active_keys = set()
        
        # Key mappings based on your Hand Simulator image
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
                'ring': 's',  # Fixed: Changed from 'g' to 's' based on image
                'pinky': 'a'
            },
            'special': {
                'fist': 'left_click',
                'rotation': 'right_click',
                'hand_switch': 'shift',
            }
        }
        
        # Track which hand is active
        self.active_hand = "right"  # Default to right hand
        
        # Previous hand position for movement
        self.prev_hand_pos = None
        self.movement_smoothing = 0.5  # Smoothing factor
    
    def get_finger_states(self, landmarks, is_right_hand=True):
        """
        Detect finger states (1=extended/open, 0=closed/down)
        Returns: Array of 5 binary values [thumb, index, middle, ring, pinky]
        """
        fingers = []
        
        # Adjust for left/right hand
        if is_right_hand:
            # Thumb - check x position relative to index base
            if landmarks[4].x > landmarks[3].x:
                fingers.append(1)  # Extended
            else:
                fingers.append(0)  # Closed
        else:
            # For left hand, thumb is extended when x is less than previous joint
            if landmarks[4].x < landmarks[3].x:
                fingers.append(1)  # Extended
            else:
                fingers.append(0)  # Closed
                
        # Other fingers - check y position (tip vs pip)
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        
        for tip, pip in zip(finger_tips, finger_pips):
            # Extended when tip is higher (smaller y) than pip
            if landmarks[tip].y < landmarks[pip].y:
                fingers.append(1)  # Extended
            else:
                fingers.append(0)  # Closed
                
        return fingers
    
    def detect_movement(self, wrist_pos):
        """Detect hand movement for directional control"""
        x, y = wrist_pos.x, wrist_pos.y
        
        movement = []
        
        # Horizontal movement
        if x < 0.3:
            movement.append('left')
        elif x > 0.7:
            movement.append('right')
            
        # Vertical movement  
        if y < 0.3:
            movement.append('up')
        elif y > 0.7:
            movement.append('down')
            
        return movement
    
    def detect_hand_type(self, handedness):
        """Determine if the hand is left or right"""
        if handedness.classification[0].label == "Right":
            return "right"
        else:
            return "left"
    
    def apply_controls(self, gestures, hand_pos=None):
        """Apply detected gestures to game controls"""
        
        # Clear previous keys
        for key in list(self.active_keys):
            if key in ['left_click', 'right_click']:
                mouse_release(key)
            else:
                release_key(key)
        self.active_keys.clear()
        
        # Apply movement
        for movement in gestures.get('movement', []):
            if movement in self.controls['movement']:
                key = self.controls['movement'][movement]
                press_key(key)
                self.active_keys.add(key)
        
        # Apply finger controls - INVERTED LOGIC:
        # Now we press keys when fingers are CLOSED (0), not when open (1)
        fingers = gestures.get('fingers', {})
        finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
        
        for i, finger_name in enumerate(finger_names):
            # Only press key when finger is closed (0), not open (1)
            if fingers.get(finger_name, 1) == 0:  # Default to open if not found
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
                dx = (hand_pos[0] - self.prev_hand_pos[0]) * 1000  # X movement (horizontal)
                dy = (hand_pos[2] - self.prev_hand_pos[2]) * 1000  # Z movement (depth for Y axis)
                wheel = (self.prev_hand_pos[1] - hand_pos[1]) * 500  # Y movement (vertical for scroll)
                
                # Apply smoothing
                dx *= self.movement_smoothing
                dy *= self.movement_smoothing
                
                # Move mouse
                if abs(dx) > 1 or abs(dy) > 1:
                    mouse_move(dx, dy)
                
                # Scroll
                if abs(wheel) > 1:
                    mouse_move(0, 0, wheel)
            
            # Update previous position
            self.prev_hand_pos = hand_pos
    
    def run(self):
        """Main control loop"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("Simple Hand Simulator Controller")
        print("Controls:")
        print("- Move hands to edges for movement")
        print("- Close fingers for control: Thumb=Space, Index=F, Middle=D, Ring=S, Pinky=A") 
        print("- Closed fist = Left Mouse Click")
        print("- Open hand with rotation = Right Mouse Click") 
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
                'movement': [],
                'fingers': {},
                'special': None
            }
            
            hand_pos = None
            
            if results.multi_hand_landmarks and results.multi_handedness:
                # Find the most prominent hand (closest to camera)
                main_hand_idx = 0
                if len(results.multi_hand_landmarks) > 1:
                    # Use the hand with larger bounding box as main hand
                    sizes = []
                    for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        x_min = min(landmark.x for landmark in hand_landmarks.landmark)
                        x_max = max(landmark.x for landmark in hand_landmarks.landmark)
                        y_min = min(landmark.y for landmark in hand_landmarks.landmark)
                        y_max = max(landmark.y for landmark in hand_landmarks.landmark)
                        size = (x_max - x_min) * (y_max - y_min)
                        sizes.append((size, i))
                    main_hand_idx = max(sizes)[1]
                
                # Get main hand
                hand_landmarks = results.multi_hand_landmarks[main_hand_idx]
                handedness = results.multi_handedness[main_hand_idx]
                hand_type = self.detect_hand_type(handedness)
                
                # Draw landmarks
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Get wrist position for movement
                wrist = hand_landmarks.landmark[0]
                movement = self.detect_movement(wrist)
                gestures['movement'].extend(movement)
                
                # Get 3D position for mouse control
                hand_pos = [wrist.x, wrist.y, wrist.z]
                
                # Get finger states
                is_right_hand = (hand_type == "right")
                finger_states = self.get_finger_states(hand_landmarks.landmark, is_right_hand)
                gestures['fingers'] = {
                    'thumb': finger_states[0],
                    'index': finger_states[1], 
                    'middle': finger_states[2],
                    'ring': finger_states[3],
                    'pinky': finger_states[4]
                }
                
                # Check for special gestures
                # Fist: all fingers closed
                if not any(finger_states):
                    gestures['special'] = 'fist'
                
                # Hand switch detection based on active hand changing
                if self.active_hand != hand_type:
                    gestures['special'] = 'hand_switch'
                    self.active_hand = hand_type
                
                # Apply controls
                self.apply_controls(gestures, hand_pos)
                
                # Display current state
                y_pos = 30
                cv2.putText(frame, f"Hand Simulator: {hand_type.upper()} HAND", 
                           (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y_pos += 30
                
                if gestures['movement']:
                    move_text = "Movement: " + ", ".join(gestures['movement'])
                    cv2.putText(frame, move_text, (10, y_pos), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                    y_pos += 25
                
                # Show which fingers are closed (now these are the active ones)
                closed_fingers = [name for name, state in gestures['fingers'].items() if state == 0]
                if closed_fingers:
                    finger_text = "Closed fingers: " + ", ".join(closed_fingers)
                    cv2.putText(frame, finger_text, (10, y_pos), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    y_pos += 25
                
                if gestures['special']:
                    cv2.putText(frame, f"Special: {gestures['special']}", (10, y_pos), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            else:
                # No hands detected - release all keys
                for key in list(self.active_keys):
                    if key in ['left_click', 'right_click']:
                        mouse_release(key)
                    else:
                        release_key(key)
                self.active_keys.clear()
                self.prev_hand_pos = None
                
                cv2.putText(frame, "No hands detected", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.putText(frame, "Press 'q' to quit", (10, h-20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('Simple Hand Simulator Controller', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        # Clean up
        for key in list(self.active_keys):
            if key in ['left_click', 'right_click']:
                mouse_release(key)
            else:
                release_key(key)
        self.active_keys.clear()
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    controller = SimpleHandSimulator()
    controller.run()