# Hand Simulator Gesture Controller
# Complete gesture recognition system for Hand Simulator game control

import cv2
import mediapipe as mp
import numpy as np
import time
import collections
import threading
from keyinput import press_key, release_key

# Configuration constants
DETECTION_CONFIDENCE = 0.8
TRACKING_CONFIDENCE = 0.7
FINGER_EXTENSION_THRESHOLD = 0.1
GESTURE_SMOOTHING = 0.
CALIBRATION_FRAMES = 60

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=DETECTION_CONFIDENCE,
    min_tracking_confidence=TRACKING_CONFIDENCE
)

class HandSimulatorController:
    def __init__(self):
        self.gesture_history = collections.deque(maxlen=5)
        self.current_keys = set()
        self.previous_gesture = None
        
    def detect_finger_states(self, hand_landmarks):
        """
        Detect which fingers are extended for each hand
        Returns: [thumb, index, middle, ring, pinky] - True if extended
        """
        landmarks = hand_landmarks.landmark
        fingers = []
        
        # Thumb (special case - horizontal comparison)
        if landmarks[4].x > landmarks[3].x:  # Right hand
            fingers.append(landmarks[4].x > landmarks[3].x)
        else:  # Left hand
            fingers.append(landmarks[4].x < landmarks[3].x)
        
        # Other fingers (vertical comparison)
        finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
        finger_pips = [6, 10, 14, 18]  # PIP joints
        
        for tip, pip in zip(finger_tips, finger_pips):
            fingers.append(landmarks[tip].y < landmarks[pip].y)
            
        return fingers
    
    def detect_hand_position(self, hand_landmarks):
        """
        Detect hand position and orientation for movement control
        """
        landmarks = hand_landmarks.landmark
        wrist = landmarks[0]
        middle_finger_tip = landmarks[12]
        
        # Calculate hand direction vector
        dx = middle_finger_tip.x - wrist.x
        dy = middle_finger_tip.y - wrist.y
        
        return {
            'center_x': wrist.x,
            'center_y': wrist.y,
            'direction_x': dx,
            'direction_y': dy,
            'angle': np.degrees(np.arctan2(dy, dx))
        }
    
    def classify_gesture(self, left_hand_data, right_hand_data):
        """
        Classify the current gesture based on both hands
        """
        gesture = {
            'movement': None,
            'fingers': {},
            'special': None
        }
        
        # Movement controls (based on hand position)
        if left_hand_data and right_hand_data:
            # Both hands detected - analyze relative positions
            left_pos = self.detect_hand_position(left_hand_data)
            right_pos = self.detect_hand_position(right_hand_data)
            
            # Horizontal movement
            avg_x = (left_pos['center_x'] + right_pos['center_x']) / 2
            if avg_x < 0.3:
                gesture['movement'] = 'left'
            elif avg_x > 0.7:
                gesture['movement'] = 'right'
            
            # Vertical movement
            avg_y = (left_pos['center_y'] + right_pos['center_y']) / 2
            if avg_y < 0.3:
                gesture['movement'] = 'up'
            elif avg_y > 0.7:
                gesture['movement'] = 'down'
                
        elif left_hand_data:
            # Left hand only
            left_pos = self.detect_hand_position(left_hand_data)
            if left_pos['center_x'] < 0.3:
                gesture['movement'] = 'left'
            elif left_pos['center_y'] < 0.3:
                gesture['movement'] = 'up'
                
        elif right_hand_data:
            # Right hand only
            right_pos = self.detect_hand_position(right_hand_data)
            if right_pos['center_x'] > 0.7:
                gesture['movement'] = 'right'
            elif right_pos['center_y'] > 0.7:
                gesture['movement'] = 'down'
        
        # Finger controls
        for hand_name, hand_data in [('left', left_hand_data), ('right', right_hand_data)]:
            if hand_data:
                fingers = self.detect_finger_states(hand_data)
                gesture['fingers'][hand_name] = {
                    'thumb': fingers[0],
                    'index': fingers[1],
                    'middle': fingers[2],
                    'ring': fingers[3],
                    'pinky': fingers[4],
                    'all': all(fingers)
                }
        
        # Special gestures
        if left_hand_data and right_hand_data:
            left_fingers = gesture['fingers']['left']
            right_fingers = gesture['fingers']['right']
            
            # Check for special combinations
            if left_fingers['all'] and right_fingers['all']:
                gesture['special'] = 'submit'
            elif not any([left_fingers['thumb'], left_fingers['index'], 
                         left_fingers['middle'], left_fingers['ring'], left_fingers['pinky']]):
                gesture['special'] = 'cancel'
        
        return gesture
    
    def apply_gesture(self, gesture):
        """
        Apply the detected gesture to game controls
        """
        # Movement controls
        movement_keys = {'up': 'up', 'down': 'down', 'left': 'left', 'right': 'right'}
        
        # Release previous movement keys
        for key in movement_keys.values():
            if key in self.current_keys:
                release_key(key)
                self.current_keys.discard(key)
        
        # Apply current movement
        if gesture['movement'] and gesture['movement'] in movement_keys:
            key = movement_keys[gesture['movement']]
            press_key(key)
            self.current_keys.add(key)
        
        # Finger controls
        finger_key_map = {
            'thumb': 'space',
            'index': 'f',
            'middle': 'd',
            'ring': 's',
            'pinky': 'a'
        }
        
        # Apply finger controls for each hand
        for hand_name, finger_data in gesture['fingers'].items():
            for finger_name, is_extended in finger_data.items():
                if finger_name in finger_key_map:
                    key = finger_key_map[finger_name]
                    
                    if is_extended:
                        if key not in self.current_keys:
                            press_key(key)
                            self.current_keys.add(key)
                    else:
                        if key in self.current_keys:
                            release_key(key)
                            self.current_keys.discard(key)
        
        # Special gestures
        special_key_map = {
            'submit': 'enter',
            'cancel': 'esc'
        }
        
        if gesture['special'] and gesture['special'] in special_key_map:
            key = special_key_map[gesture['special']]
            press_key(key)
            time.sleep(0.1)
            release_key(key)
    
    def release_all_keys(self):
        """Release all currently pressed keys"""
        for key in list(self.current_keys):
            release_key(key)
        self.current_keys.clear()

def main():
    """
    Main function for Hand Simulator gesture control
    """
    controller = HandSimulatorController()
    cap = cv2.VideoCapture(0)
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # For FPS calculation
    prev_time = time.time()
    fps_values = collections.deque(maxlen=30)
    
    print("Hand Simulator Controller started. Press ESC to exit.")
    print("Controls:")
    print("- Hand position: Arrow keys")
    print("- Fingers: Space, F, D, G, A")
    print("- All fingers up: Enter (Submit)")
    print("- Fist: Escape (Cancel)")
    
    try:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                continue
            
            # Flip image horizontally for mirror effect
            image = cv2.flip(image, 1)
            
            # Calculate FPS
            current_time = time.time()
            fps = 1 / (current_time - prev_time)
            fps_values.append(fps)
            avg_fps = sum(fps_values) / len(fps_values)
            prev_time = current_time
            
            # Process with MediaPipe
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            left_hand_data = None
            right_hand_data = None
            
            # Process detected hands
            if results.multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    # Draw hand landmarks
                    mp_drawing.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())
                    
                    # Determine hand side
                    if results.multi_handedness[idx].classification[0].label == 'Left':
                        left_hand_data = hand_landmarks
                    else:
                        right_hand_data = hand_landmarks
                
                # Classify and apply gesture
                gesture = controller.classify_gesture(left_hand_data, right_hand_data)
                controller.apply_gesture(gesture)
                
                # Display gesture information
                y_offset = 50
                if gesture['movement']:
                    cv2.putText(image, f"Movement: {gesture['movement']}", 
                               (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    y_offset += 30
                
                for hand_name, finger_data in gesture['fingers'].items():
                    active_fingers = [name for name, state in finger_data.items() if state and name != 'all']
                    if active_fingers:
                        cv2.putText(image, f"{hand_name}: {', '.join(active_fingers)}", 
                                   (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                        y_offset += 25
                
                if gesture['special']:
                    cv2.putText(image, f"Special: {gesture['special']}", 
                               (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
            else:
                # No hands detected - release all keys
                controller.release_all_keys()
            
            # Display FPS
            cv2.putText(image, f"FPS: {avg_fps:.1f}", 
                       (image.shape[1] - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display instructions
            cv2.putText(image, "Press ESC to exit", 
                       (20, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Hand Simulator Controller', image)
            
            # Exit on ESC key
            if cv2.waitKey(5) & 0xFF == 27:
                break
                
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        controller.release_all_keys()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()