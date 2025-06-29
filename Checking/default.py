import cv2 as cv
import numpy as np
import time
import serial
import threading

# ---- Bluetooth Setup ----
BLUETOOTH_PORT = 'COM7'  # Replace with your HC-05 COM port
BAUD_RATE = 9600

try:
    bt_serial = serial.Serial(BLUETOOTH_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"Bluetooth connected on {BLUETOOTH_PORT}.")
except Exception as e:
    print(f"Bluetooth connection failed: {e}")
    bt_serial = None

# ---- Ultrasonic Reading Thread ----
def read_ultrasonic():
    while True:
        if bt_serial and bt_serial.in_waiting: 
            try:
                line = bt_serial.readline().decode().strip()
                if line.startswith("DIST:"):
                    print(f"[Ultrasonic] {line}")
                time.sleep(0.5)  # Delay to avoid spamming
            except:
                pass

# ---- Eye Blink Detection Setup ----
face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_alt.xml')
eyes_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml')

if face_cascade.empty() or eyes_cascade.empty():
    print("Error loading cascades.")
    exit(0)

cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Error opening camera.")
    exit(0)

blink_count = 0
eye_closed_frames = 0
EYE_CLOSED_THRESHOLD = 3
INTERVAL_SECONDS = 15
interval_start_time = time.time()

def detect_and_display(frame):
    global blink_count, eye_closed_frames, interval_start_time

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    gray = cv.equalizeHist(gray)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        faceROI = gray[y:y+h, x:x+w]
        eyes = eyes_cascade.detectMultiScale(faceROI)

        if len(eyes) == 0:
            eye_closed_frames += 1
        else:
            if eye_closed_frames >= EYE_CLOSED_THRESHOLD:
                blink_count += 1
                print(f"Blink detected! Total blinks: {blink_count}")
            eye_closed_frames = 0

        for (ex, ey, ew, eh) in eyes:
            eye_center = (x + ex + ew//2, y + ey + eh//2)
            radius = int(round((ew + eh) * 0.25))
            frame = cv.circle(frame, eye_center, radius, (255, 0, 0), 4)

    elapsed_time = time.time() - interval_start_time

    cv.putText(frame, f"Blinks: {blink_count}", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv.putText(frame, f"Time Left: {INTERVAL_SECONDS - int(elapsed_time)}s", (10, 60), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    if elapsed_time >= INTERVAL_SECONDS:
        print(f"Sending blink count: {blink_count}")
        if bt_serial:
            try:
                bt_serial.write(f"{blink_count}\n".encode())
                print("Sent to Bluetooth device!")
            except Exception as e:
                print(f"Bluetooth send error: {e}")
        blink_count = 0
        interval_start_time = time.time()

    cv.imshow('Blink Detection', frame)

# ---- Start Ultrasonic Listener Thread ----
ultra_thread = threading.Thread(target=read_ultrasonic, daemon=True)
ultra_thread.start()

# ---- Main Loop ----
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("No camera frame.")
            break
        detect_and_display(frame)

        if cv.waitKey(5) == 27:
            break
except KeyboardInterrupt:
    print("Exited by user.")
finally:
    if bt_serial:
        bt_serial.close()
    cap.release()
    cv.destroyAllWindows()
    print("Resources released.")