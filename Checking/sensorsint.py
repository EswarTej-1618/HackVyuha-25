import serial
import time as sleep

# Bluetooth Setup
BLUETOOTH_PORT = 'COM8'  # Replace with the correct port if needed
BAUD_RATE = 9600

try:
    bt_serial = serial.Serial(BLUETOOTH_PORT, BAUD_RATE, timeout=1)
    sleep.sleep(2)  # Allow time for the connection to initialize
    print(f"Bluetooth connected on {BLUETOOTH_PORT}.")
except Exception as e:
    print(f"Bluetooth connection failed: {e}")
    bt_serial = None

while bt_serial:  # Ensure connection exists before reading
    raw_value = bt_serial.readline()
    
    try:
        value = raw_value.decode('utf-8', errors='ignore').strip()  # Ignores invalid bytes
        print(f"Received: {value}")
    except UnicodeDecodeError:
        print(f"Unicode error: {raw_value}")  # Print raw bytes for debugging
    
    sleep.sleep(0.1)  # Delay to avoid spamming