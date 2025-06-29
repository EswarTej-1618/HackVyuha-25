import speech_recognition as sr
import pyttsx3
import serial
import time

# Bluetooth Setup
BLUETOOTH_PORT = 'COM3'  # Replace with your Bluetooth module's port
BAUD_RATE = 9600

try:
    bt_serial = serial.Serial(BLUETOOTH_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Allow time for the connection to initialize
    print(f"Bluetooth connected on {BLUETOOTH_PORT}.")
except Exception as e:
    print(f"Bluetooth connection failed: {e}")
    bt_serial = None
    exit()
# Engine setup for speech
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 170)

# Function to speak
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function for voice input
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, phrase_time_limit=7)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"You said: {query}\n")
    except Exception:
        print("Could you please say that again?")
        return "None"
    
    return query.lower()

while True:
    query = takeCommand()
    speak(f"You said: {query}")
    if bt_serial:
        if "left" in query:
            speak("Sending left command to Bluetooth device")
            bt_serial.write(b'left')
        elif "right" in query:
            speak("Sending right command to Bluetooth device")
            bt_serial.write(b'right')
        elif "stop" in query:
            speak("Stopping the Bluetooth device")
            bt_serial.write(b'2')  # Stop command
        elif "forward" in query:
            speak("Sending forward command to Bluetooth device")
            bt_serial.write(b'1')  # Forward command
        elif "reverse" in query:
            speak("Sending reverse command to Bluetooth device")
            bt_serial.write(b'3')  # Reverse command
        elif "exit" in query:
            speak("Exiting...")
            # if bt_serial:
            #     bt_serial.close()
            exit()