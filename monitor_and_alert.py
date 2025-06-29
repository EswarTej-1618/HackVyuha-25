import serial
import re
import webbrowser
import pyttsx3
import pyautogui
import time
from time import sleep

# Setup text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Choose female voice
engine.setProperty('rate', 170)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# WhatsApp alert function
def send_whatsapp_message():
    phone_number = 'your phone number here'  # Without + sign for URL
    message = 'Abnormal Heartbeat observed'

    url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
    webbrowser.open(url, new=2)
    speak("Opening WhatsApp to send message.")
    
    sleep(40)  # Wait for WhatsApp to load & user to scan QR
    speak("Sending message now.")
    pyautogui.press('enter')
    speak("Message has been sent.")
    sleep(2)

# Serial port setup
PORT = 'COM6'  # Ensure this matches your Arduino's port
BAUD_RATE = 9600

try:
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Allow Arduino time to initialize
    print(f"Connected to {PORT}. Monitoring BPM values...")
except Exception as e:
    print(f"Failed to connect to serial port: {e}")
    exit()

# Main monitoring loop
def main():
    last_checked_time = time.time()  # Track last check time

    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if "Heart Rate" in line:
                print(f"Received: {line}")
                
                match = re.search(r"Heart Rate: (\d+)", line)
                if match:
                    bpm = int(match.group(1))
                    print(f"BPM: {bpm}")

                    # Check BPM thresholds and send alert if needed
                    if bpm < 30 or bpm > 120:
                        print(" Abnormal BPM detected!")
                        send_whatsapp_message()

                    # Check every 60 seconds instead of constant monitoring
                    if time.time() - last_checked_time >= 60:
                        last_checked_time = time.time()
                        print(" Data logged. Waiting 1 minute for the next check...")
        
        except KeyboardInterrupt:
            print("Monitoring stopped by user.")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    speak("Heart Rate Monitoring System Initialized. Please ensure the Bluetooth device is connected.")
    speak("Monitoring your heart rate. Please wait for the readings.")
    main()