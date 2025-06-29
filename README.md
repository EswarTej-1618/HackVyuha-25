# Intentional Gaze, Blink, and Heartbeat Monitoring System

A multi-component assistive technology project that combines **computer vision**, **speech feedback**, **Bluetooth communication**, **Arduino robotics**, and **health monitoring**. This system enables hands-free robot control using gaze and blink detection, and monitors heart rate with automated WhatsApp alerts for abnormal readings.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Setup & Usage](#setup--usage)
  - [1. Hardware Setup](#1-hardware-setup)
  - [2. Arduino Setup](#2-arduino-setup)
  - [3. Python Setup](#3-python-setup)
  - [4. Heartbeat Monitoring & Alerts](#4-heartbeat-monitoring--alerts)
- [How It Works](#how-it-works)
- [Customization](#customization)
- [Security & Privacy](#security--privacy)
- [Acknowledgements](#acknowledgements)

---

## Features

- **Gaze & Blink Detection:** Uses webcam and Mediapipe to detect intentional gaze direction (left/right) and blinks.
- **Speech Feedback:** Provides real-time voice prompts and status updates.
- **Bluetooth Communication:** Sends gaze/blink data to Arduino for robot control.
- **Robot Chassis Control:** Arduino robot receives commands for movement (forward, reverse, stop, turn) based on gaze/blink.
- **Heartbeat Monitoring:** Arduino reads pulse sensor, displays BPM on OLED, and sends data via Bluetooth/Serial.
- **Automated WhatsApp Alerts:** Python scripts monitor heart rate and send WhatsApp messages if abnormal BPM is detected.

---

## Project Structure

```
Hacthon/
│
├── code1.py                      # Main Python script for gaze/blink detection and Bluetooth comms
├── heartbeat.py                  # Python script for heart rate monitoring and WhatsApp alert (with buffer clearing)
├── monitor_and_alert.py          # Alternate Python script for heart rate monitoring and WhatsApp alert
│
├── arduino_heartbeat/
│   └── arduino_heartbeat.ino     # Arduino sketch: pulse sensor, OLED, Bluetooth
│
├── heartbeat2/
│   └── heartbeat2.ino            # Arduino sketch: pulse sensor, OLED (no Bluetooth)
│
└── Bot_code/
    └── main_2.ino                # Arduino sketch: robot chassis, Bluetooth, obstacle avoidance
```

---

## Requirements

### Python

- Python 3.7+
- [OpenCV](https://pypi.org/project/opencv-python/)
- [Mediapipe](https://pypi.org/project/mediapipe/)
- [pyttsx3](https://pypi.org/project/pyttsx3/)
- [pyserial](https://pypi.org/project/pyserial/)
- [pyautogui](https://pypi.org/project/pyautogui/) (for WhatsApp automation)

Install dependencies:
```sh
pip install opencv-python mediapipe pyttsx3 pyserial pyautogui
```

### Arduino

- Arduino UNO/Nano or compatible board
- Pulse Sensor (A0)
- OLED Display (SSD1306, I2C, 128x64)
- HC-05/HC-06 Bluetooth module (for robot/heartbeat comms)
- Robot chassis with L298N motor driver (for Bot_code)
- [Adafruit SSD1306](https://github.com/adafruit/Adafruit_SSD1306) and [Adafruit GFX](https://github.com/adafruit/Adafruit-GFX-Library) libraries

---

## Setup & Usage

### 1. Hardware Setup

- Connect webcam to PC.
- Connect pulse sensor to Arduino A0.
- Connect OLED display via I2C (SDA/SCL).
- Connect Bluetooth module to Arduino (RX/TX as per sketch).
- Assemble robot chassis and connect motors to L298N (if using Bot_code).

### 2. Arduino Setup

- Open the relevant `.ino` file in Arduino IDE:
  - `arduino_heartbeat.ino` for heartbeat monitoring with Bluetooth.
  - `heartbeat2.ino` for heartbeat monitoring without Bluetooth.
  - `main_2.ino` for robot chassis control.
- Install required libraries via Library Manager.
- Select the correct board and port, then upload.

### 3. Python Setup

- Edit `BLUETOOTH_PORT` in `code1.py` to match your Bluetooth COM port (default: `COM3`).
- Run the main detection script:
  ```sh
  python code1.py
  ```
- The script will provide voice feedback and start webcam-based detection.

### 4. Heartbeat Monitoring & Alerts

- Edit `PORT` in `heartbeat.py` or `monitor_and_alert.py` to match your Arduino's COM port (default: `COM6`).
- Replace `'your phone number here'` with your WhatsApp number in international format (without `+`).
- Run the script:
  ```sh
  python heartbeat.py
  ```
- The script will monitor BPM and send a WhatsApp message if BPM is abnormal.

---

## How It Works

- **Gaze/Blink Detection:** Python uses Mediapipe to analyze webcam frames for eye landmarks, calculates gaze direction and blinks, and sends results to Arduino via Bluetooth.
- **Robot Control:** Arduino receives gaze/blink data, interprets commands, and moves the robot accordingly. Obstacle avoidance is handled via ultrasonic sensors.
- **Heartbeat Monitoring:** Arduino reads pulse sensor, calculates BPM, displays it on OLED, and sends data to PC via Serial/Bluetooth.
- **Alerting:** Python script reads BPM from Serial, and if BPM is out of safe range, opens WhatsApp Web and sends an alert message automatically.

---

## Customization

- **COM Ports:** Update `BLUETOOTH_PORT` and `PORT` in Python scripts to match your system.
- **Thresholds:** Adjust blink/gaze/heartbeat thresholds in Python and Arduino code for your environment.
- **WhatsApp Number:** Replace placeholder with your actual number in Python scripts.
- **Robot Actions:** Modify robot movement logic in `main_2.ino` as needed.

---

## Security & Privacy

- No sensitive personal data is stored or transmitted by default.
- Your Windows username (`LOGIC`) may appear in file paths; change before sharing if desired.
- WhatsApp automation requires WhatsApp Web login and may expose your number if not handled privately.

---

## Acknowledgements

- [Mediapipe](https://google.github.io/mediapipe/) by Google
- [OpenCV](https://opencv.org/)
- [Adafruit](https://www.adafruit.com/) for display libraries
- [pyttsx3](https://pypi.org/project/pyttsx3/)
- [pyserial](https://pypi.org/project/pyserial/)
- [pyautogui](https://pypi.org/project/pyautogui/)

---

## License

This project is for educational and prototyping
