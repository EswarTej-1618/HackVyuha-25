import cv2 as cv
import mediapipe as mp
import time
import serial

print("Initializing...")

BLUETOOTH_PORT = 'COM3'  # Replace with your HC-05 COM port
BAUD_RATE = 9600

try:
    bt_serial = serial.Serial(BLUETOOTH_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"Bluetooth connected on {BLUETOOTH_PORT}.")
except Exception as e:
    print(f"Bluetooth connection failed: {e}")
    bt_serial = None


# Initialize Webcam
cam = cv.VideoCapture(0)
if not cam.isOpened():
    print("Error: Camera not detected.")
    exit()

cv.namedWindow("Blink & Gaze Detection", cv.WINDOW_NORMAL)

# Mediapipe Setup
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

intentional_gaze = ""
intentional_blinks = 0
blink_start_time = None
gaze_start_time = None
prev_gaze_text = ""
prev_eye_state = "open"
start_time = time.time()

while True:
    success, frame = cam.read()
    if not success:
        print("Error: Failed to read frame")
        continue

    frame = cv.flip(frame, 1)
    frame_h, frame_w, _ = frame.shape
    rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    result = face_mesh.process(rgb_frame)

    if result.multi_face_landmarks:
        landmarks = result.multi_face_landmarks[0].landmark

        # Gaze Detection
        r_outer = landmarks[33].x * frame_w
        r_inner = landmarks[133].x * frame_w
        r_center = (r_outer + r_inner) / 2.0
        r_iris = landmarks[468].x * frame_w
        r_offset = (r_iris - r_center) / abs(r_inner - r_outer)

        l_outer = landmarks[263].x * frame_w
        l_inner = landmarks[362].x * frame_w
        l_center = (l_outer + l_inner) / 2.0
        l_iris = landmarks[473].x * frame_w
        l_offset = (l_iris - l_center) / abs(l_outer - l_inner)

        avg_offset = (r_offset + l_offset) / 2.0
        threshold = 0.15
        new_gaze_text = ""

        if avg_offset < -threshold:
            new_gaze_text = "Left"
        elif avg_offset > threshold:
            new_gaze_text = "Right"

        # Detect intentional gaze shift
        if new_gaze_text != prev_gaze_text and new_gaze_text != "":
            gaze_start_time = time.time()
        elif gaze_start_time and (time.time() - gaze_start_time) > 1:
            intentional_gaze = new_gaze_text

        prev_gaze_text = new_gaze_text

        # Blink Detection
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
            if blink_start_time and (time.time() - blink_start_time) > 0.5:
                intentional_blinks += 1
            prev_eye_state = "open"
            blink_start_time = None

        # Overlay Text
        cv.putText(frame, f"Gaze: {intentional_gaze if intentional_gaze else 'None'}", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 215, 255), 2)
        cv.putText(frame, f"Blinks: {intentional_blinks}", (10, 70), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    else:
        print("No face detected, skipping frame")

    cv.imshow("Blink & Gaze Detection", frame)

    # Send Data Every 6 Seconds
    if time.time() - start_time >= 6:
        if bt_serial:
            try:
                if intentional_gaze != "":
                    bt_serial.write(intentional_gaze.encode())
                    print(f"Sent: {intentional_gaze}") 
                elif intentional_blinks > 0:
                    bt_serial.write(str(intentional_blinks).encode())
                    print(f"Sent: {intentional_blinks}")
                else:
                    print("No significant gaze or blink detected")
            except serial.SerialException as e:
                print(f"Error: Failed to send data via Bluetooth - {e}")

        # Reset values after sending data
        intentional_gaze = ""
        intentional_blinks = 0
        start_time = time.time()

    if cv.waitKey(1) & 0xFF == 27:  # Exit on 'ESC' key
        break

# Cleanup
if bt_serial:
    bt_serial.close()
cam.release()
cv.destroyAllWindows()
print("Resources released successfully")