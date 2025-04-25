import cv2
from pynput.keyboard import Controller, Key 
from pynput.mouse import Controller as MouseController, Button  
import handtracking as htm  
import time

cap = cv2.VideoCapture(0)  
cap.set(3, 640) 
cap.set(4, 480)  

detector = htm.handDetector(maxHands=1, detectionCon=0.75, trackCon=0.75)  

keyboard = Controller()  
mouse = MouseController()  

# Control states
control_mode = "keyboard"  
switch_time = time.time()  
switch_delay = 5.0  # Delay 

mouse_pressed = False  # To track mouse clicks

def debounce_switch():
    """Returns True if the time delay for switching is satisfied."""
    global switch_time
    current_time = time.time()
    if current_time - switch_time > switch_delay:
        switch_time = current_time
        return True
    return False

while True:
    success, img = cap.read()  
    img = detector.findHands(img)  
    lmList, bbox = detector.findPosition(img)  # Get landmark positions 

    if len(lmList) != 0:  
        fingers = detector.fingersUp()  
        # Gesture to switch to mouse mode (Thumb and Pinky up)
        # if fingers[0] == 1 and fingers[4] == 1 and all(f == 0 for f in fingers[1:4]) and control_mode != "mouse":
        #     if debounce_switch():  # Prevent accidental switching
        #         control_mode = "mouse"
        #         print("Switched to Mouse Mode")
        
        # Gesture to switch to keyboard mode (Index and Middle finger up)
        if fingers[0] == 1 and fingers[4] == 1 and all(f == 0 for f in fingers[1:4]) and control_mode != "keyboard":
            if debounce_switch():
                control_mode = "keyboard"
                print("Switched to Keyboard Mode")

        if control_mode == "keyboard":
            # Keyboard controls
            # if all(fingers):  # Jump (Space)wawa
            #     keyboard.press(Key.space)
            # else:
            #     keyboard.release(Key.space)

            # Esc gesture: Thumb and Ring finger up
            if fingers[0] == 1 and fingers[3] == 1 and all(f == 0 for f in [1, 2, 4]):
                keyboard.press(Key.esc)
            else:
                keyboard.release(Key.esc)

            # Move Forward (W): Index finger up
            if fingers[1] == 1 and all(f == 0 for f in fingers[:1] + fingers[2:]):  # Only index finger up
                keyboard.press("w")
                keyboard.release("s")
            else:
                keyboard.release("w")

            # Turn Left (A): Thumb up
            if fingers[0] == 1 and fingers[1] == 1 and all(f == 0 for f in fingers[2:]):  # Only thumb up
                keyboard.press("w")
                keyboard.press("a")
            else:
                keyboard.release("a")

            # Turn Right (D):
            if fingers[1] == 1 and fingers[2] == 1 and all(f == 0 for f in fingers[:1] + fingers[3:]): 
                keyboard.press("w") 
                keyboard.press("d")
            else:
                keyboard.release("d")

            # Brake/Reverse (S): I
            if all(fingers) :
                keyboard.press("s")
            else:
                keyboard.release("s")

            # # Honk (H): Thumb and Pinky up
            # if fingers[0] == 1 and fingers[4] == 1:
            #     keyboard.press("h")
            # else:
            #     keyboard.release("h")

        elif control_mode == "mouse":
            # Mouse controls
            if fingers[0] == 1 and fingers[1] == 0:  # Pinch gesture: Thumb up, index down
                if not mouse_pressed:
                    mouse.click(Button.left, 1)  # Perform a left-click
                    mouse_pressed = True
            else:
                mouse_pressed = False  # Release mouse click state

            # Scroll gesture: All fingers up
            if all(fingers):
                mouse.scroll(0, 1)  # Scroll up 

            # # Fist gesture: Scroll down
            # if fingers == [0, 0, 0, 0, 0]:
            #     mouse.scroll(0, -1)  # Scroll down

            # Index finger up to move the mouse pointer
            if fingers[1] == 1 and all(f == 0 for f in fingers[:1] + fingers[2:]):  # Only index finger up
                x, y = lmList[8][1:3]  # Get position of index finger tip
                screen_x, screen_y = mouse.position  # Current mouse position
                mouse.move(x - screen_x, y - screen_y)  # Move the mouse pointer accordingly

    cv2.imshow("image", img)  # Display camera feed
    cv2.waitKey(1)  # Wait for 1 ms to process next frame