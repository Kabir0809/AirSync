import math
import keyinput
import cv2
import mediapipe as mp
import time

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
font = cv2.FONT_HERSHEY_SIMPLEX

# 0 For webcam input:
cap = cv2.VideoCapture(0)

# Initializing current time and precious time for calculating the FPS
previousTime = 0
currentTime = 0

# Variables to track key states
w_pressed = False
a_pressed = False
s_pressed = False
d_pressed = False

# Function to ensure keys are properly released
def release_all_keys():
    global w_pressed, a_pressed, s_pressed, d_pressed
    if w_pressed:
        keyinput.release_key('w')
        w_pressed = False
    if a_pressed:
        keyinput.release_key('a')
        a_pressed = False
    if s_pressed:
        keyinput.release_key('s')
        s_pressed = False
    if d_pressed:
        keyinput.release_key('d')
        d_pressed = False

# Function to safely press keys
def press_key_safely(key):
    global w_pressed, a_pressed, s_pressed, d_pressed
    try:
        if key == 'w' and not w_pressed:
            keyinput.press_key('w')
            w_pressed = True
        elif key == 'a' and not a_pressed:
            keyinput.press_key('a')
            a_pressed = True
        elif key == 's' and not s_pressed:
            keyinput.press_key('s')
            s_pressed = True
        elif key == 'd' and not d_pressed:
            keyinput.press_key('d')
            d_pressed = True
    except Exception as e:
        print(f"Error pressing key {key}: {e}")

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read(cv2.WINDOW_NORMAL)
    if not success:
      print("Ignoring empty camera frame.")
      continue

    fp = cv2.flip(image, 1)  # --------> flipped_fp

    # Calculating the FPS
    currentTime = time.time()
    fps = 1 / (currentTime-previousTime)
    previousTime = currentTime
    
    # Displaying background colour for fps 
    cv2.rectangle(fp, (0, 0), (120,40), (0,0,0), -1)
     
    # Displaying FPS on the image     -------> Frames per second
    cv2.putText(fp, str(int(fps))+" FPS", (0, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
    
    # To improve performance, optionally mark the fp as not writeable to
    fp.flags.writeable = False
    fp = cv2.cvtColor(fp, cv2.COLOR_BGR2RGB)
    results = hands.process(fp)
    fpHeight, fpWidth, _ = fp.shape
   
    # Draw the hand annotations on the fp.
    fp.flags.writeable = True
    fp = cv2.cvtColor(fp, cv2.COLOR_RGB2BGR)
    co=[]
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            fp,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
        for point in mp_hands.HandLandmark:
           if str(point) == "0":
              normalizedLandmark = hand_landmarks.landmark[point]
              pixelCoordinatesLandmark = mp_drawing._normalized_to_pixel_coordinates(normalizedLandmark.x,
                                                                                    normalizedLandmark.y,
                                                                                    fpWidth, fpHeight)

              # Check if coordinates are valid before appending
              if pixelCoordinatesLandmark is not None:
                  co.append(list(pixelCoordinatesLandmark))
                  print(f"Added coordinates: {pixelCoordinatesLandmark}")
              else:
                  print("Warning: Got None coordinates for wrist landmark")
    
    if len(co) == 2:
        try:
            xm, ym = (co[0][0] + co[1][0]) / 2, (co[0][1] + co[1][1]) / 2
            radius = 150
            m=(co[1][1]-co[0][1])/(co[1][0]-co[0][0])
        except:
            continue
        
        a = 1 + m ** 2
        b = -2 * xm - 2 * co[0][0] * (m ** 2) + 2 * m * co[0][1] - 2 * m * ym
        c = xm ** 2 + (m ** 2) * (co[0][0] ** 2) + co[0][1] ** 2 + ym ** 2 - 2 * co[0][1] * ym - 2 * co[0][1] * co[0][
            0] * m + 2 * m * ym * co[0][0] - 22500

        # centre horizontal line or diameter of the circle
        try:
            xa = (-b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
            xb = (-b - (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
            ya = m * (xa - co[0][0]) + co[0][1]
            yb = m * (xb - co[0][0]) + co[0][1]
            
            if m!=0:
              ap = 1 + ((-1/m) ** 2)
              bp = -2 * xm - 2 * xm * ((-1/m) ** 2) + 2 * (-1/m) * ym - 2 * (-1/m) * ym
              cp = xm ** 2 + ((-1/m) ** 2) * (xm ** 2) + ym ** 2 + ym ** 2 - 2 * ym * ym - 2 * ym * xm * (-1/m) + 2 * (-1/m) * ym * xm - 22500
              
              xap = (-bp + (bp ** 2 - 4 * ap * cp) ** 0.5) / (2 * ap)
              xbp = (-bp - (bp ** 2 - 4 * ap * cp) ** 0.5) / (2 * ap)
              yap = (-1 / m) * (xap - xm) + ym
              ybp = (-1 / m) * (xbp - xm) + ym
        except:
            # Reset all keys if we can't calculate turning
            release_all_keys()
            continue

        cv2.circle(img=fp, center=(int(xm), int(ym)), radius=radius, color=(15,185,255), thickness=15)

        l = (int(math.sqrt((co[0][0] - co[1][0]) ** 2 * (co[0][1] - co[1][1]) ** 2)) - 150) // 2
        cv2.line(fp, (int(xa), int(ya)), (int(xb), int(yb)), (15,185,255), 20)
        
        # Adjust the turning threshold to be more responsive for GTA 4
        turn_threshold = 50  # Lowered from 65 for more responsive turning

        if co[0][0] < co[1][0] and co[0][1] - co[1][1] > turn_threshold:
            # When turning left, also maintain forward acceleration for GTA 4
            print("Turning Left")
            # Release opposite keys first
            if s_pressed:
                keyinput.release_key('s')
                s_pressed = False
            if d_pressed:
                keyinput.release_key('d')
                d_pressed = False
                
            # Apply current control keys
            press_key_safely('w')  # Keep accelerating
            press_key_safely('a')  # Turn left
            
            cv2.putText(fp, "Turning Left", (130,30), font, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.line(fp, (int(xap), int(yap)), (int(xm), int(ym)), (255, 0, 0), 20)

        elif co[1][0] > co[0][0] and co[1][1] - co[0][1] > turn_threshold:
            print("Turning Right")
            # Release opposite keys first
            if s_pressed:
                keyinput.release_key('s')
                s_pressed = False
            if a_pressed:
                keyinput.release_key('a')
                a_pressed = False
                
            # Apply current control keys
            press_key_safely('w')  # Keep accelerating
            press_key_safely('d')  # Turn right
            
            cv2.putText(fp, "Turn Right", (130,30), font, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.line(fp, (int(xbp), int(ybp)), (int(xm), int(ym)), (255, 0, 0), 20)

        else:
            print("keeping straight")
            # Release turning keys
            if a_pressed:
                keyinput.release_key('a')
                a_pressed = False
            if d_pressed:
                keyinput.release_key('d')
                d_pressed = False
            if s_pressed:
                keyinput.release_key('s')
                s_pressed = False
                
            # Keep accelerating forward
            press_key_safely('w')
            
            cv2.putText(fp, "keep straight", (130,30), font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            if ybp>yap:
                cv2.line(fp, (int(xbp), int(ybp)), (int(xm), int(ym)), (15,185,255), 20)
            else:
                cv2.line(fp, (int(xap), int(yap)), (int(xm), int(ym)), (15,185,255), 20)

    elif len(co)==1:
       print("Reverse")
       # Release forward and turning keys
       if w_pressed:
           keyinput.release_key('w')
           w_pressed = False
       if a_pressed:
           keyinput.release_key('a')
           a_pressed = False
       if d_pressed:
           keyinput.release_key('d')
           d_pressed = False
           
       # Apply brake/reverse
       press_key_safely('s')
       
       cv2.putText(fp, "Reverse", (130,30), font, 1.0, (0, 0, 255), 2, cv2.LINE_AA)
    else:
       # If no hands detected, release all keys for safety
       release_all_keys()

    cv2.imshow('Motion controlled game system using computer vision', fp)
    
    if cv2.waitKey(5) & 0xFF == ord('q'):
      # Clean up before exiting
      release_all_keys()
      break

cap.release()
cv2.destroyAllWindows()

