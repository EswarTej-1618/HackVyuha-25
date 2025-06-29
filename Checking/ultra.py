import cv2 as cv
import numpy as np
import time
import serial
import threading
import mediapipe as mp

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

# ---- Setup OpenCV and Mediapipe ----
cam = cv.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

blink_count = 0
prev_eye_state = "open"
last_detected_gaze = "None"
blink_start_time = None

gaze_left_start_time = None
gaze_right_start_time = None
GAZE_CONFIRM_TIME = 0.6

INTERVAL_SECONDS = 15
interval_start_time = time.time()

def detect_gaze_and_blink(frame):
    global blink_count, prev_eye_state, blink_start_time, last_detected_gaze, gaze_left_start_time, gaze_right_start_time

    rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    result = face_mesh.process(rgb_frame)

    if result.multi_face_landmarks:
        landmarks = result.multi_face_landmarks[0].landmark
        frame_h, frame_w, _ = frame.shape

        # ---- Gaze Detection ----
        r_outer = landmarks[33].x * frame_w
        r_inner = landmarks[133].x * frame_w
        r_iris = landmarks[468].x * frame_w
        r_center = (r_outer + r_inner) / 2.0
        r_width = abs(r_inner - r_outer)
        r_offset = (r_iris - r_center) / r_width

        l_outer = landmarks[263].x * frame_w
        l_inner = landmarks[362].x * frame_w
        l_iris = landmarks[473].x * frame_w
        l_center = (l_outer + l_inner) / 2.0
        l_width = abs(l_outer - l_inner)
        l_offset = (l_iris - l_center) / l_width

        average_offset = (r_offset + l_offset) / 2.0
        threshold = 0.15
        new_gaze_text = ""

        if average_offset < -threshold:
            if gaze_left_start_time is None:
                gaze_left_start_time = time.time()
            elif (time.time() - gaze_left_start_time) >= GAZE_CONFIRM_TIME:
                new_gaze_text = "Looking Left"
        else:
            gaze_left_start_time = None

        if average_offset > threshold:
            if gaze_right_start_time is None:
                gaze_right_start_time = time.time()
            elif (time.time() - gaze_right_start_time) >= GAZE_CONFIRM_TIME:
                new_gaze_text = "Looking Right"
        else:
            gaze_right_start_time = None

        if new_gaze_text:
            last_detected_gaze = new_gaze_text

        # ---- Blink Detection ----
        r_top = landmarks[159].y * frame_h
        r_bottom = landmarks[145].y * frame_h
        r_height = abs(r_bottom - r_top)

        l_top = landmarks[386].y * frame_h
        l_bottom = landmarks[374].y * frame_h
        l_height = abs(l_bottom - l_top)

        avg_eye_height = (r_height + l_height) / 2.0

        if avg_eye_height < 8:
            if prev_eye_state == "open":
                blink_start_time = time.time()
                prev_eye_state = "closed"
        else:
            if blink_start_time and (time.time() - blink_start_time) > 0.4:
                blink_count += 1
            prev_eye_state = "open"
            blink_start_time = None

        # ---- Overlay Text ----
        cv.putText(frame, f"Gaze: {last_detected_gaze}", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 215, 255), 2)
        cv.putText(frame, f"Blinks: {blink_count}", (50, 100), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 215, 255), 2)

    elapsed_time = time.time() - interval_start_time

    if elapsed_time >= INTERVAL_SECONDS:
        print(f"Sending data: Blinks={blink_count}, Gaze={last_detected_gaze}")
        if bt_serial:
            try:
                bt_serial.write(f"{blink_count},{last_detected_gaze}\n".encode())
                print("Sent to Bluetooth device!")
            except Exception as e:
                print(f"Bluetooth send error: {e}")

        blink_count = 0
        interval_start_time = time.time()

    return frame

# ---- Start Ultrasonic Listener Thread ----
ultra_thread = threading.Thread(target=read_ultrasonic, daemon=True)
ultra_thread.start()

# ---- Main Loop ----
try:
    while True:
        ret, frame = cam.read()
        if not ret:
            break

        frame = cv.flip(frame, 1)
        processed_frame = detect_gaze_and_blink(frame)
        cv.imshow("Gaze & Blink Detection", processed_frame)

        if cv.waitKey(5) == 27:
            break
except KeyboardInterrupt:
    print("Exited by user.")
finally:
    if bt_serial:
        bt_serial.close()
    cam.release()
    cv.destroyAllWindows()
    print("Resources released.")