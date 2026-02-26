import cv2
import numpy as np
import socket
import time

# --- ROBOT SETTINGS ---
ROBOT_IP = "192.168.1.10"  # <-- ROBOT IP ADDRESS
ROBOT_PORT = 4210

# ==========================================
# 🎯 CALIBRATION RESULTS 
# ==========================================
# 1. CENTER POINT (The angle where the robot looks straight ahead)
CENTER_PAN = 88   
CENTER_TILT = 89  

# 2. SENSITIVITY (Slider 88 -> 0.088)
# The intensity of the robot's movement. Keeps it locked on target.
SENSITIVITY_MULTIPLIER = 0.088 

# --- DIRECTION SETTINGS ---
REVERSE_PAN = True     
REVERSE_TILT = False   

# MOTOR LIMITS (Safety constraints)
PAN_MIN = 0
PAN_MAX = 180
TILT_MIN = 40
TILT_MAX = 140

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cap = cv2.VideoCapture(0)

# Red Color Boundaries (HSV format)
lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

# Go to center on startup
last_pan = CENTER_PAN
last_tilt = CENTER_TILT

print(f"TERMINATOR ACTIVE! Center: {CENTER_PAN},{CENTER_TILT} | Sensitivity: {SENSITIVITY_MULTIPLIER}")
print("Press 'q' to exit.")

while True:
    ret, frame = cap.read()
    if not ret: break

    h, w, _ = frame.shape 
    frame_blur = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Default Target: CENTER
    target_pan = CENTER_PAN
    target_tilt = CENTER_TILT
    target_found = False

    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        
        if radius > 5:
            target_found = True
            
            # Draw Crosshairs
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.line(frame, (int(x), int(y)-10), (int(x), int(y)+10), (0, 0, 255), 2) # Vertical line
            cv2.line(frame, (int(x)-10, int(y)), (int(x)+10, int(y)), (0, 0, 255), 2) # Horizontal line

            # --- 🧠 CALCULATION ---
            # 1. How far is the target from the center? (Pixel difference)
            diff_x = x - (w / 2)
            diff_y = y - (h / 2)

            # 2. Convert Pixels to Degrees (Multiply by sensitivity)
            delta_pan = diff_x * SENSITIVITY_MULTIPLIER
            delta_tilt = diff_y * SENSITIVITY_MULTIPLIER
            
            # 3. Direction Calculation
            if REVERSE_PAN:
                target_pan = CENTER_PAN - delta_pan
            else:
                target_pan = CENTER_PAN + delta_pan

            if REVERSE_TILT:
                target_tilt = CENTER_TILT - delta_tilt
            else:
                target_tilt = CENTER_TILT + delta_tilt

            cv2.putText(frame, "LOCKED", (int(x)-40, int(y)-20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Motor Limits (Prevent forcing the servos)
    target_pan = max(PAN_MIN, min(target_pan, PAN_MAX))
    target_tilt = max(TILT_MIN, min(target_tilt, TILT_MAX))

    # Do not overwork the motor (Send signal only if difference is > 0.5 degrees)
    if abs(target_pan - last_pan) > 0.5 or abs(target_tilt - last_tilt) > 0.5:
        try:
            msg = f"{int(target_pan)},{int(target_tilt)}"
            sock.sendto(msg.encode(), (ROBOT_IP, ROBOT_PORT))
            last_pan = target_pan
            last_tilt = target_tilt
        except:
            pass

    cv2.imshow("TERMINATOR VISION", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
