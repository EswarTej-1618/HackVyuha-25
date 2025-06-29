import serial
import time as sleep
import mediapipe as mp
import cv2 as cv
import pyttsx3

# Engine setup for speech
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 170)

# Function to speak
def speak(text):
    engine.say(text)
    engine.runAndWait()

speak("Good Morning sir !")
speak("Intentional Gaze and Blink Detection System Initialized. Please ensure the Bluetooth device is connected.")
# Bluetooth Setup
BLUETOOTH_PORT = 'COM3'  # Replace with the correct port if needed
BAUD_RATE = 9600

try:
    bt_serial = serial.Serial(BLUETOOTH_PORT, BAUD_RATE, timeout=1)
    sleep.sleep(2)  # Allow time for the connection to initialize
    print(f"Bluetooth connected on {BLUETOOTH_PORT}.")
    speak("Bluetooth connection established successfully.")
except Exception as e:
    print(f"Bluetooth connection failed: {e}")
    speak("Bluetooth connection failed. Please check the device and try again.")
    bt_serial = None
    exit()

INTERVAL_SEC = 7
interval_start_time = sleep.time()
time_left = INTERVAL_SEC

# Setup OpenCV and Mediapipe
cam = cv.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

blink_count = 0     # Count of blinks detected
prev_eye_state = "open"   # Tracks whether the eye was previously open 
last_detected_gaze = "None"
blink_start_time = None
prev_gaze_text = ""

# New variables for confirming gaze detection
gaze_left_start_time = None
gaze_right_start_time = None
GAZE_CONFIRM_TIME = 0.6  # confirm delay

while True:
    success, frame = cam.read()
    if not success:
        continue

    frame = cv.flip(frame, 1)
    frame_h, frame_w, _ = frame.shape
    rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    result = face_mesh.process(rgb_frame)

    if result.multi_face_landmarks:
        landmarks = result.multi_face_landmarks[0].landmark

        # --- Gaze Detection ---
        # Right eye landmarks
        r_outer = landmarks[33].x * frame_w
        r_inner = landmarks[133].x * frame_w
        r_iris = landmarks[468].x * frame_w
        r_center = (r_outer + r_inner) / 2.0
        r_width = abs(r_inner - r_outer)
        r_offset = (r_iris - r_center) / r_width

        # Left eye landmarks
        l_outer = landmarks[263].x * frame_w
        l_inner = landmarks[362].x * frame_w
        l_iris = landmarks[473].x * frame_w
        l_center = (l_outer + l_inner) / 2.0
        l_width = abs(l_outer - l_inner)
        l_offset = (l_iris - l_center) / l_width

        # Averaging both eyes’ positions
        average_offset = (r_offset + l_offset) / 2.0
        threshold = 0.15
        new_gaze_text = ""

        if average_offset < -threshold:
            if gaze_left_start_time is None:
                gaze_left_start_time = sleep.time()
            elif (sleep.time() - gaze_left_start_time) >= GAZE_CONFIRM_TIME:
                new_gaze_text = "Looking Left"
        else:
            gaze_left_start_time = None  # Reset left gaze confirmation

        if average_offset > threshold:
            if gaze_right_start_time is None:
                gaze_right_start_time = sleep.time()
            elif (sleep.time() - gaze_right_start_time) >= GAZE_CONFIRM_TIME:
                new_gaze_text = "Looking Right"
        else:
            gaze_right_start_time = None  # Reset right gaze confirmation

        if new_gaze_text != "":
            last_detected_gaze = new_gaze_text

        prev_gaze_text = new_gaze_text

        # --- Blink Detection ---
        r_top = landmarks[159].y * frame_h
        r_bottom = landmarks[145].y * frame_h
        r_height = abs(r_bottom - r_top)

        l_top = landmarks[386].y * frame_h
        l_bottom = landmarks[374].y * frame_h
        l_height = abs(l_bottom - l_top)

        avg_eye_height = (r_height + l_height) / 2.0

        if avg_eye_height < 8:
            if prev_eye_state == "open":
                blink_start_time = sleep.time()
                prev_eye_state = "closed"
        else:
            if blink_start_time and (sleep.time() - blink_start_time) > 0.4:
                blink_count += 1
            prev_eye_state = "open"
            blink_start_time = None

        # --- Green Markers for Iris Position ---
        cv.circle(frame, (int(r_iris), int(landmarks[468].y * frame_h)), 3, (0, 255, 0), -1)
        cv.circle(frame, (int(l_iris), int(landmarks[473].y * frame_h)), 3, (0, 255, 0), -1)

        # --- Overlay Text ---
        gold_color = (0, 215, 255)
        cv.putText(frame, f"Intentional Gaze: {last_detected_gaze}", (50, 50),
                    cv.FONT_HERSHEY_SIMPLEX, 1, gold_color, 2)
        cv.putText(frame, f"Blink Count: {blink_count}", (50, 100),
                    cv.FONT_HERSHEY_SIMPLEX, 1, gold_color, 2)
        cv.putText(frame, f"Time Left: {time_left:.1f} sec", (50, 150),
                    cv.FONT_HERSHEY_SIMPLEX, 1, gold_color, 2)

    elapsed_time = sleep.time() - interval_start_time
    time_left = INTERVAL_SEC - int(elapsed_time)

    # --- Interval-based Bluetooth Data Transmission ---
    if elapsed_time >= INTERVAL_SEC:
        print(f"Sending data: Blinks={blink_count}, Gaze={last_detected_gaze}")
        
        if bt_serial:
            try:
                bt_serial.write(f"{str(blink_count)},{str(last_detected_gaze)}".encode())
                print("Sent to Bluetooth device!")
                # speak(f"sent blinks {blink_count} and Gazing  {last_detected_gaze}")
                # Reset counters and timer ONLY after successful transmission
                interval_start_time = sleep.time()
                blink_count = 0
                last_detected_gaze = "None"

            except Exception as e:
                print(f"Bluetooth send error: {e}")

    cv.imshow("Intentional Gaze & Blink Detection", frame)

    # Exit if the ESC key is pressed
    if cv.waitKey(1) & 0xFF == 27:
        break

cam.release()
cv.destroyAllWindows()