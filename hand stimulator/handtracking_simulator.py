"""
Hand Tracking Test Module for Hand Simulator
Tests MediaPipe hand detection accuracy and visualizes landmark detection
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import math

class HandSimulatorDetector:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Create hands object with high accuracy settings
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6,
            model_complexity=1
        )
        
        # Visualization settings
        self.show_finger_angles = False
        self.show_3d_coordinates = False
        self.show_rotation = True
        self.fps_history = []
        
    def calculate_finger_angles(self, landmarks):
        """Calculate angles for each finger"""
        # Define landmarks for each finger (tip, pip, mcp)
        finger_landmarks = [
            [4, 3, 2],   # Thumb
            [8, 6, 5],   # Index
            [12, 10, 9], # Middle
            [16, 14, 13], # Ring
            [20, 18, 17]  # Pinky
        ]
        
        angles = []
        
        for points in finger_landmarks:
            # Get 3D coordinates of three points
            a = np.array([landmarks[points[0]].x, landmarks[points[0]].y, landmarks[points[0]].z])
            b = np.array([landmarks[points[1]].x, landmarks[points[1]].y, landmarks[points[1]].z])
            c = np.array([landmarks[points[2]].x, landmarks[points[2]].y, landmarks[points[2]].z])
            
            # Calculate vectors
            vec1 = b - a
            vec2 = c - b
            
            # Calculate angle using dot product
            dot = np.dot(vec1, vec2)
            norm = np.linalg.norm(vec1) * np.linalg.norm(vec2)
            
            # Avoid division by zero
            if norm < 1e-6:
                angles.append(0)
            else:
                # Clamp to avoid floating point errors
                cos_angle = max(-1.0, min(1.0, dot / norm))
                angle = np.degrees(np.arccos(cos_angle))
                angles.append(angle)
        
        return angles
    
    def detect_rotation(self, landmarks):
        """Detect hand rotation angle"""
        # Use index and pinky MCP as reference for rotation
        index_mcp = np.array([landmarks[5].x, landmarks[5].y])
        pinky_mcp = np.array([landmarks[17].x, landmarks[17].y])
        
        # Calculate angle
        dx = pinky_mcp[0] - index_mcp[0]
        dy = pinky_mcp[1] - index_mcp[1]
        
        # Calculate angle in degrees (0-360)
        angle = math.degrees(math.atan2(dy, dx)) % 360
        
        return angle
    
    def calculate_fps(self, frame_time):
        """Calculate and smooth FPS"""
        fps = 1.0 / frame_time if frame_time > 0 else 0
        self.fps_history.append(fps)
        
        # Keep history to a reasonable size
        if len(self.fps_history) > 30:
            self.fps_history.pop(0)
        
        # Return average FPS
        return sum(self.fps_history) / len(self.fps_history)
    
    def draw_custom_landmarks(self, frame, landmarks, width, height):
        """Draw custom landmarks with detailed information"""
        connections = self.mp_hands.HAND_CONNECTIONS
        
        # Draw each landmark
        for i, landmark in enumerate(landmarks):
            # Convert normalized coordinates to pixel coordinates
            x, y = int(landmark.x * width), int(landmark.y * height)
            
            # Adjust circle size by Z depth
            z_value = landmark.z
            radius = int(5 - z_value * 40)
            radius = max(2, min(radius, 8))
            
            # Color based on landmark type (knuckles, fingertips, etc.)
            if i in [4, 8, 12, 16, 20]:  # Fingertips
                color = (0, 0, 255)  # Red
            elif i in [2, 5, 9, 13, 17]:  # Knuckles
                color = (0, 255, 0)  # Green
            elif i == 0:  # Wrist
                color = (255, 0, 0)  # Blue
            else:
                color = (255, 255, 255)  # White
            
            # Draw the landmark
            cv2.circle(frame, (x, y), radius, color, -1)
            
            # Show landmark number if in detailed view
            if self.show_3d_coordinates:
                cv2.putText(frame, f"{i}", (x+5, y+5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
        
        # Draw connections
        for connection in connections:
            start_idx, end_idx = connection
            start_point = landmarks[start_idx]
            end_point = landmarks[end_idx]
            
            start_x, start_y = int(start_point.x * width), int(start_point.y * height)
            end_x, end_y = int(end_point.x * width), int(end_point.y * height)
            
            # Draw the connection line
            cv2.line(frame, (start_x, start_y), (end_x, end_y), (255, 255, 255), 1)
    
    def process_frame(self, frame, start_time):
        """Process a single frame for hand tracking analysis"""
        # Flip the frame horizontally
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        # Calculate frame processing time and FPS
        frame_time = time.time() - start_time
        fps = self.calculate_fps(frame_time)
        
        # Draw FPS
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, h-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Handle detected hands
        if results.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Get handedness
                handedness = "Right" if results.multi_handedness[i].classification[0].label == "Right" else "Left"
                
                # Draw basic landmarks
                if not self.show_3d_coordinates:
                    self.mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())
                else:
                    # Draw custom landmarks with depth info
                    self.draw_custom_landmarks(frame, hand_landmarks.landmark, w, h)
                
                # Display hand information
                y_pos = 30 + i * 120
                cv2.putText(frame, f"Hand #{i+1}: {handedness}", (10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                y_pos += 25
                
                # Calculate finger angles if enabled
                if self.show_finger_angles:
                    angles = self.calculate_finger_angles(hand_landmarks.landmark)
                    finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
                    
                    for j, (name, angle) in enumerate(zip(finger_names, angles)):
                        cv2.putText(frame, f"{name}: {angle:.1f}°", (10, y_pos), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                        y_pos += 20
                
                # Show rotation if enabled
                if self.show_rotation:
                    rotation = self.detect_rotation(hand_landmarks.landmark)
                    cv2.putText(frame, f"Rotation: {rotation:.1f}°", (10, y_pos), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                    y_pos += 20
                
                # Show 3D coordinates of wrist if enabled
                if self.show_3d_coordinates:
                    wrist = hand_landmarks.landmark[0]
                    cv2.putText(frame, f"Wrist: X:{wrist.x:.2f} Y:{wrist.y:.2f} Z:{wrist.z:.2f}", 
                               (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
        else:
            cv2.putText(frame, "No hands detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Display controls
        cv2.putText(frame, "A: Angles | Z: 3D Coords | R: Rotation | Q: Quit", 
                   (10, h-30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return frame
    
    def run(self):
        """Run the hand tracking test"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("Hand Tracking Test")
        print("Controls:")
        print("- A: Toggle finger angles")
        print("- Z: Toggle 3D coordinates")
        print("- R: Toggle rotation display")
        print("- Q: Quit")
        
        while True:
            start_time = time.time()
            ret, frame = cap.read()
            
            if not ret:
                print("Failed to capture frame - check camera connection")
                break
            
            frame = self.process_frame(frame, start_time)
            cv2.imshow('Hand Tracking Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('a'):
                self.show_finger_angles = not self.show_finger_angles
                print(f"Finger angles: {'ON' if self.show_finger_angles else 'OFF'}")
            elif key == ord('z'):
                self.show_3d_coordinates = not self.show_3d_coordinates
                print(f"3D coordinates: {'ON' if self.show_3d_coordinates else 'OFF'}")
            elif key == ord('r'):
                self.show_rotation = not self.show_rotation
                print(f"Rotation: {'ON' if self.show_rotation else 'OFF'}")
        
        cap.release()
        cv2.destroyAllWindows()

def main():
    detector = HandSimulatorDetector()
    detector.run()

if __name__ == "__main__":
    main()