import socket
import time
import RPi.GPIO as GPIO
import serial
import threading
import queue

# Get the local IP address dynamically
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(('8.8.8.8', 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception:
        return None

# Function to remove duplicate substring
def remove_duplicate_substring(input_value):
    input_string = str(input_value)
    length = len(input_string)

    for i in range(1, length // 2 + 1):
        substr = input_string[:i]
        repeat_count = length // i

        if substr * repeat_count == input_string:
            return substr

    return input_string

# Get the IP address dynamically
HOST = get_ip_address()
PORT = 6000

if HOST:
    print(f"Detected IP address: {HOST}")
else:
    print("Failed to detect IP address. Check your network connection.")

# Set up GPIO pins for relays
ENTRY_RELAY_PIN = 17

# Set up GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(ENTRY_RELAY_PIN, GPIO.OUT)
GPIO.output(ENTRY_RELAY_PIN, GPIO.HIGH)

# Initialize socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print('Connected by', addr)

# Initialize serial communication with QR scanner
ENTRY = serial.Serial('/dev/ttyAMA0', baudrate=115200, timeout=1)

# Variables to store the most recent scanned data for each scanner
prev_scanned_data_entry = {"Scanner 1": ""}

# Create a queue for GPIO operations
gpio_queue = queue.Queue()

# Function for GPIO operations
def perform_gpio_operations():
    while True:
        operation = gpio_queue.get()
        if operation is None:
            break
        if operation == "OPENEN":
            GPIO.output(ENTRY_RELAY_PIN, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(ENTRY_RELAY_PIN, GPIO.HIGH)

# Create a thread for GPIO operations
gpio_thread = threading.Thread(target=perform_gpio_operations)
gpio_thread.daemon = True
gpio_thread.start()

# Function to send a heartbeat packet to the client
def send_heartbeat(conn):
    while True:
        time.sleep(3)
        try:
            conn.send('|HLT%\n'.encode('utf-8'))
        except Exception as e:
            print(f"Error sending heartbeat: {str(e)}")
            break

# Create thread for sending heartbeat packet
heartbeat_thread = threading.Thread(target=send_heartbeat, args=(conn,))
heartbeat_thread.daemon = True
heartbeat_thread.start()

# Function to read QR code data
def read_qr_code(scanner, scanner_name):
    global prev_scanned_data_entry

    while True:
        data = scanner.readline().decode('utf-8').strip()
        if data:
            if data != prev_scanned_data_entry[scanner_name]:
                cleaned_data = data.replace("TG", "").replace("END", "")
                cleaned_data = cleaned_data.replace("QR", "").replace("END", "")

                if cleaned_data.isnumeric():
                    protocol = "|ENCD-" if scanner_name == "Scanner 1" else "|EXCD-"
                else:
                    protocol = "|ENQR-" if scanner_name == "Scanner 1" else "|EXQR-"

                cleaned_data = protocol + remove_duplicate_substring(cleaned_data) + "%" + '\n'
                print(f"Scanned by {scanner_name}: {cleaned_data}")
                conn.send(cleaned_data.encode('utf-8'))

                if scanner_name == "Scanner 1":
                    prev_scanned_data_entry[scanner_name] = cleaned_data

# Create thread for reading from the entry scanner



thread1 = threading.Thread(target=read_qr_code, args=(ENTRY, "Scanner 1"))
thread1.daemon = True
thread1.start()

# Main Loop
while True:
    data = conn.recv(1024).decode('utf-8')
    if not data:
        break

    response = ""

    if data.startswith("|"):
        start_index = data.find("|") + 1
        end_index = data.find("%")

        if start_index != -1 and end_index != -1:
            extracted_data = data[start_index:end_index]

            if extracted_data == "OPENEN":
                gpio_queue.put("OPENEN")
                response = "|OK%"

            elif extracted_data.startswith("ENQR-"):
                qr_code = extracted_data[len("ENQR-"):].strip()
                if qr_code.isalnum():
                    response = "|OPENEN%"
                else:
                    response = "|INVALIDEN%"

            elif extracted_data.startswith("ENCD-"):
                card_data = extracted_data[len("ENCD-"):].strip()
                if card_data.isnumeric():
                    response = "|OPENEN%"
                else:
                    response = "|INVALIDEN%"

    print(f"Received data: {data}")
    print(f"Sending response: {response}")

    try:
        conn.send(response.encode('utf-8'))
    except BrokenPipeError:
        print("Client disconnected")
        break

# Clean up GPIO and close the connection when the loop exits
GPIO.cleanup()
conn.close()

# Signal the GPIO thread to exit
gpio_queue.put(None)
# Wait for the GPIO thread to finish
gpio_thread.join()
