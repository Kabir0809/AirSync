"""
AirSync Steering Wheel - Control racing games with natural hand gestures
This implementation provides a virtual steering wheel interface using a webcam
and hand gesture detection.

Requirements:
- Python 3.7+
- OpenCV
- MediaPipe
- NumPy
- vgamepad (for Windows)
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import collections
import vgamepad as vg
import threading

# Configuration constants
STEERING_SENSITIVITY = 1.5  # Multiplier for steering angle
THUMB_EXTENSION_THRESHOLD = 0.08  # Distance threshold for detecting extended thumbs
WHEEL_ROTATION_SMOOTHING = 0.8  # Smoothing factor (0-1) for steering
DEAD_ZONE = 5.0  # Degrees of movement to ignore (dead zone)
CALIBRATION_FRAMES = 60  # Number of frames to use for calibration
MAX_STEERING_ANGLE = 180  # Maximum degrees for full steering
FULL_TURN_ANGLE = 90.0  # Angle at which steering reaches maximum (full turn)

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,  # Critical - we need to track both hands
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Create virtual gamepad
gamepad = vg.VX360Gamepad()

# For storing hand position history for prediction
left_hand_history = collections.deque(maxlen=5)
right_hand_history = collections.deque(maxlen=5)

# For smoothing steering input
steering_history = collections.deque(maxlen=5)


def detect_steering_wheel(landmarks_left, landmarks_right):
    """
    Calculate the position and size of the virtual steering wheel
    based on the positions of both hands.
    
    Args:
        landmarks_left: Array of landmarks for the left hand
        landmarks_right: Array of landmarks for the right hand
        
    Returns:
        wheel_center: Center point of the wheel (x, y)
        wheel_radius: Radius of the wheel
        wheel_angle: Current angle of the wheel
    """
    # Find center point between wrists
    left_wrist = np.array([landmarks_left[0].x, landmarks_left[0].y])
    right_wrist = np.array([landmarks_right[0].x, landmarks_right[0].y])
    
    wheel_center = (left_wrist + right_wrist) / 2
    wheel_radius = np.linalg.norm(right_wrist - left_wrist) / 2
    
    # Calculate current wheel angle (line between hands)
    dx = right_wrist[0] - left_wrist[0]
    dy = right_wrist[1] - left_wrist[1]
    wheel_angle = np.degrees(np.arctan2(dy, dx))
    
    return wheel_center, wheel_radius, wheel_angle


def calculate_steering_from_neutral(current_angle, neutral_angle):
    """
    Calculate steering angle based on deviation from neutral position
    
    Args:
        current_angle: Current wheel angle in degrees
        neutral_angle: Neutral (calibrated) wheel angle in degrees
        
    Returns:
        steering_angle: Steering angle relative to neutral position
    """
    # Calculate deviation from neutral position
    angle_diff = current_angle - neutral_angle
    
    # Normalize to the range -180 to 180
    if angle_diff > 180:
        angle_diff -= 360
    elif angle_diff < -180:
        angle_diff += 360
    
    return angle_diff


def detect_throttle_brake(landmarks_left, landmarks_right):
    """
    Detect if user is accelerating (thumbs closed) or braking (thumbs extended)
    
    Args:
        landmarks_left: Array of landmarks for the left hand
        landmarks_right: Array of landmarks for the right hand
        
    Returns:
        is_accelerating: True if user is accelerating, False if braking
    """
    # Get thumb tip and index finger base positions for both hands
    left_thumb_tip = np.array([landmarks_left[4].x, landmarks_left[4].y])
    left_index_base = np.array([landmarks_left[5].x, landmarks_left[5].y])
    
    right_thumb_tip = np.array([landmarks_right[4].x, landmarks_right[4].y])
    right_index_base = np.array([landmarks_right[5].x, landmarks_right[5].y])
    
    # Calculate distances from thumb tips to index finger bases
    left_dist = np.linalg.norm(left_thumb_tip - left_index_base)
    right_dist = np.linalg.norm(right_thumb_tip - right_index_base)
    
    # Determine if thumbs are extended (braking) or closed (accelerating)
    thumbs_extended = left_dist > THUMB_EXTENSION_THRESHOLD and right_dist > THUMB_EXTENSION_THRESHOLD
    
    return not thumbs_extended  # True for acceleration, False for braking


def predict_missing_hand_position(hand_history):
    """
    Predict hand position if tracking is temporarily lost
    
    Args:
        hand_history: Deque of previous hand positions
        
    Returns:
        predicted_position: Predicted position [x, y]
    """
    if len(hand_history) < 2:
        return None
    
    # Simple linear prediction based on last two positions
    last_pos = hand_history[-1]
    second_last_pos = hand_history[-2]
    
    # Calculate velocity
    velocity = [last_pos[0] - second_last_pos[0], last_pos[1] - second_last_pos[1]]
    
    # Predict new position
    predicted_position = [last_pos[0] + velocity[0], last_pos[1] + velocity[1]]
    
    return predicted_position


def apply_steering_dead_zone(steering_angle, dead_zone=DEAD_ZONE):
    """
    Apply a dead zone to the steering angle to prevent small unintended movements
    
    Args:
        steering_angle: Raw steering angle in degrees
        dead_zone: Size of the dead zone in degrees
        
    Returns:
        adjusted_angle: Steering angle with dead zone applied
    """
    if abs(steering_angle) < dead_zone:
        return 0.0
    else:
        # Adjust the angle to account for the dead zone (maintain continuity)
        return steering_angle - (dead_zone * (1 if steering_angle > 0 else -1))


def smooth_steering(new_angle):
    """
    Apply smoothing to steering input to prevent jitter
    
    Args:
        new_angle: New steering angle
        
    Returns:
        smoothed_angle: Smoothed steering angle
    """
    steering_history.append(new_angle)
    
    # Apply exponential moving average
    weights = [WHEEL_ROTATION_SMOOTHING ** i for i in range(len(steering_history))]
    weights.reverse()  # Most recent gets highest weight
    
    weighted_sum = sum(w * a for w, a in zip(weights, steering_history))
    weight_sum = sum(weights)
    
    return weighted_sum / weight_sum if weight_sum > 0 else 0


def map_steering_to_gamepad(steering_angle, full_turn_angle=FULL_TURN_ANGLE):
    """
    Map steering angle to gamepad joystick value with proportional control
    
    Args:
        steering_angle: Current steering angle in degrees
        full_turn_angle: Angle at which steering should reach maximum
        
    Returns:
        joystick_value: Normalized joystick value (-1.0 to 1.0)
    """
    # Limit input angle to full turn range
    clamped_angle = max(-full_turn_angle, min(full_turn_angle, steering_angle))
    
    # Map to -1.0 to 1.0 range with proportional control
    # This creates a more natural feel where small angles = small turns
    joystick_value = clamped_angle / full_turn_angle
    
    return joystick_value


def draw_steering_wheel_overlay(image, wheel_center, wheel_radius, steering_angle, neutral_angle, is_accelerating):
    """
    Draw visual overlay showing the steering wheel and control status
    
    Args:
        image: Image to draw on
        wheel_center: Center point of the wheel (x, y) in normalized coordinates
        wheel_radius: Radius of the wheel in normalized coordinates
        steering_angle: Current wheel angle in degrees
        neutral_angle: Neutral (calibrated) wheel angle in degrees
        is_accelerating: True if accelerating, False if braking
    """
    h, w, _ = image.shape
    
    # Convert normalized coordinates to pixel coordinates
    center_x = int(wheel_center[0] * w)
    center_y = int(wheel_center[1] * h)
    radius = int(wheel_radius * w)
    
    # Draw the steering wheel circle
    cv2.circle(image, (center_x, center_y), radius, (0, 255, 0), 2)
    
    # Draw neutral position line
    neutral_rad = np.radians(neutral_angle)
    neutral_end_x = center_x + int(radius * np.cos(neutral_rad))
    neutral_end_y = center_y + int(radius * np.sin(neutral_rad))
    cv2.line(image, (center_x, center_y), (neutral_end_x, neutral_end_y), 
             (255, 255, 255), 1, cv2.LINE_AA)
    
    # Draw current position line
    angle_rad = np.radians(steering_angle)
    end_x = center_x + int(radius * np.cos(angle_rad))
    end_y = center_y + int(radius * np.sin(angle_rad))
    cv2.line(image, (center_x, center_y), (end_x, end_y), (0, 0, 255), 3, cv2.LINE_AA)
    
    # Calculate relative steering angle
    relative_angle = calculate_steering_from_neutral(steering_angle, neutral_angle)
    joystick_value = map_steering_to_gamepad(relative_angle)
    
    # Show steering angle value and joystick input
    cv2.putText(image, f"Angle: {relative_angle:.1f}° (Joy: {joystick_value:.2f})", 
               (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Draw steering indicator bar at bottom of screen
    bar_width = w - 80
    bar_height = 20
    bar_x = 40
    bar_y = h - 40
    
    # Draw background bar
    cv2.rectangle(image, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                 (100, 100, 100), cv2.FILLED)
    
    # Draw indicator position
    indicator_pos = int(bar_x + (bar_width / 2) + (joystick_value * bar_width / 2))
    cv2.rectangle(image, (indicator_pos - 5, bar_y - 5), 
                 (indicator_pos + 5, bar_y + bar_height + 5), 
                 (0, 0, 255), cv2.FILLED)
    
    # Draw center line
    center_x = bar_x + bar_width // 2
    cv2.line(image, (center_x, bar_y), (center_x, bar_y + bar_height), 
             (255, 255, 255), 1)
    
    # Show acceleration/brake status
    status = "ACCELERATING" if is_accelerating else "BRAKING"
    color = (0, 255, 0) if is_accelerating else (0, 0, 255)
    cv2.putText(image, status, (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)


def calibrate_steering_wheel():
    """
    Run calibration to establish neutral position for the steering wheel
    
    Returns:
        neutral_wheel_center: Calibrated center point of the wheel
        neutral_wheel_radius: Calibrated radius of the wheel
        neutral_wheel_angle: Calibrated angle of the wheel
    """
    cap = cv2.VideoCapture(0)
    
    centers = []
    radii = []
    angles = []
    
    print("Starting calibration...")
    print("Please hold your hands in a natural steering wheel position.")
    print(f"Capturing {CALIBRATION_FRAMES} frames for calibration...")
    
    frames_captured = 0
    
    while frames_captured < CALIBRATION_FRAMES:
        success, image = cap.read()
        if not success:
            continue
        
        # Flip image horizontally for a more intuitive experience
        image = cv2.flip(image, 1)
        
        # Process image with MediaPipe
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        left_hand_landmarks = None
        right_hand_landmarks = None
        
        if results.multi_hand_landmarks:
            if len(results.multi_hand_landmarks) >= 2:
                # Identify which hand is which
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    mp_drawing.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())
                    
                    # Determine if left or right hand
                    if results.multi_handedness[idx].classification[0].label == 'Left':
                        left_hand_landmarks = hand_landmarks.landmark
                    else:
                        right_hand_landmarks = hand_landmarks.landmark
                
                if left_hand_landmarks and right_hand_landmarks:
                    # Calculate steering wheel parameters
                    wheel_center, wheel_radius, wheel_angle = detect_steering_wheel(
                        left_hand_landmarks, right_hand_landmarks)
                    
                    centers.append(wheel_center)
                    radii.append(wheel_radius)
                    angles.append(wheel_angle)
                    frames_captured += 1
                    
                    # Draw calibration progress
                    progress = int((frames_captured / CALIBRATION_FRAMES) * 100)
                    cv2.putText(image, f"Calibration: {progress}%", 
                               (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Show instruction
        cv2.putText(image, "Hold hands in neutral steering position", 
                   (20, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Display the image
        cv2.imshow('AirSync Calibration', image)
        cv2.waitKey(1)
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Calculate average wheel center, radius and angle
    neutral_wheel_center = np.mean(centers, axis=0)
    neutral_wheel_radius = np.mean(radii)
    neutral_wheel_angle = np.mean(angles)
    
    print("Calibration complete!")
    print(f"Neutral wheel center: {neutral_wheel_center}")
    print(f"Neutral wheel radius: {neutral_wheel_radius}")
    print(f"Neutral wheel angle: {neutral_wheel_angle}")
    
    return neutral_wheel_center, neutral_wheel_radius, neutral_wheel_angle


def main():
    """
    Main function for AirSync Steering Wheel control
    """
    # Run calibration
    neutral_wheel_center, neutral_wheel_radius, neutral_wheel_angle = calibrate_steering_wheel()
    
    cap = cv2.VideoCapture(0)
    
    # Try to set camera parameters for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 60)  # Request 60 FPS if available
    
    # Previous hand positions for measuring rotation
    prev_left_hand = None
    prev_right_hand = None
    
    # For FPS calculation
    prev_time = time.time()
    fps_values = collections.deque(maxlen=30)
    
    print("Starting AirSync Steering Wheel. Press ESC to exit.")
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Failed to capture frame. Retrying...")
            continue
        
        # Flip image horizontally for a more intuitive experience
        image = cv2.flip(image, 1)
        
        # Calculate FPS
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        fps_values.append(fps)
        avg_fps = sum(fps_values) / len(fps_values)
        prev_time = current_time
        
        # Process image with MediaPipe
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        left_hand_landmarks = None
        right_hand_landmarks = None
        
        if results.multi_hand_landmarks:
            # Process detected hands
            if len(results.multi_hand_landmarks) >= 2:
                # Identify which hand is which
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    # Draw hand landmarks on the image
                    mp_drawing.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())
                    
                    # Determine if left or right hand
                    if results.multi_handedness[idx].classification[0].label == 'Left':
                        left_hand_landmarks = hand_landmarks.landmark
                    else:
                        right_hand_landmarks = hand_landmarks.landmark
                
                if left_hand_landmarks and right_hand_landmarks:
                    # Calculate steering wheel parameters including current angle
                    wheel_center, wheel_radius, wheel_angle = detect_steering_wheel(
                        left_hand_landmarks, right_hand_landmarks)
                    
                    # Calculate steering based on deviation from neutral angle
                    raw_steering_angle = calculate_steering_from_neutral(
                        wheel_angle, neutral_wheel_angle)
                    
                    # Apply dead zone
                    steering_angle = apply_steering_dead_zone(raw_steering_angle)
                    
                    # Apply smoothing
                    smoothed_steering = smooth_steering(steering_angle)
                    
                    # Map to gamepad values with proportional control
                    joystick_value = map_steering_to_gamepad(smoothed_steering)
                    
                    # Apply to gamepad
                    gamepad.left_joystick_float(x_value_float=joystick_value, y_value_float=0.0)
                    
                    # Get current hand positions for tracking
                    current_left_hand = np.array([
                        left_hand_landmarks[0].x, left_hand_landmarks[0].y])
                    current_right_hand = np.array([
                        right_hand_landmarks[0].x, right_hand_landmarks[0].y])
                    
                    # Update hand history for prediction
                    left_hand_history.append(current_left_hand)
                    right_hand_history.append(current_right_hand)
                    
                    # Check throttle/brake
                    is_accelerating = detect_throttle_brake(
                        left_hand_landmarks, right_hand_landmarks)
                    
                    # Apply throttle/brake to gamepad
                    if is_accelerating:
                        gamepad.right_trigger_float(1.0)  # Full acceleration
                        gamepad.left_trigger_float(0.0)   # No brake
                    else:
                        gamepad.right_trigger_float(0.0)  # No acceleration
                        gamepad.left_trigger_float(1.0)   # Full brake
                    
                    # Update gamepad state
                    gamepad.update()
                    
                    # Draw steering wheel overlay
                    draw_steering_wheel_overlay(
                        image, wheel_center, wheel_radius, wheel_angle, 
                        neutral_wheel_angle, is_accelerating)
                    
                    # Update previous hand positions
                    prev_left_hand = current_left_hand
                    prev_right_hand = current_right_hand
        else:
            # If hands not detected, try to predict positions
            if prev_left_hand is not None and prev_right_hand is not None:
                predicted_left = predict_missing_hand_position(left_hand_history)
                predicted_right = predict_missing_hand_position(right_hand_history)
                
                if predicted_left and predicted_right:
                    # Use predictions to maintain control during brief tracking loss
                    cv2.putText(image, "Using predicted hand positions", 
                               (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                    
                    # Reset after too many predictions to prevent drift
                    if len(left_hand_history) > 0 and len(right_hand_history) > 0:
                        prev_left_hand = predicted_left
                        prev_right_hand = predicted_right
        
        # Show FPS
        cv2.putText(image, f"FPS: {avg_fps:.1f}", 
                   (image.shape[1] - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Show instruction for exit
        cv2.putText(image, "Press ESC to exit", 
                   (20, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Display the image with hand landmarks
        cv2.imshow('AirSync Steering Wheel', image)
        if cv2.waitKey(5) & 0xFF == 27:  # Exit on ESC key
            break
    
    # Clean up resources
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
