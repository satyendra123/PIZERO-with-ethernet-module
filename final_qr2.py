import socket
import time
import RPi.GPIO as GPIO
import serial
import threading

# Get the local IP address dynamically
def get_ip_address():
    try:
        # Create a socket to connect to an external server (Google DNS)
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
PORT = 6000  # Specify the port number you want to use

if HOST:
    print(f"Detected IP address: {HOST}")
else:
    print("Failed to detect IP address. Check your network connection.")

# Set up GPIO pins for relays
ENTRY_RELAY_PIN = 17  # Replace with the actual GPIO pin number for the entry relay
EXIT_RELAY_PIN = 18   # Replace with the actual GPIO pin number for the exit relay

# Set up GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(ENTRY_RELAY_PIN, GPIO.OUT)
GPIO.setup(EXIT_RELAY_PIN, GPIO.OUT)
GPIO.output(ENTRY_RELAY_PIN, GPIO.HIGH)
GPIO.output(EXIT_RELAY_PIN, GPIO.HIGH)

# Initialize socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print('Connected by', addr)

# Initialize serial communication with QR scanners
ENTRY = serial.Serial('/dev/ttyAMA0', baudrate=115200, timeout=1)
EXIT = serial.Serial('/dev/ttyAMA1', baudrate=115200, timeout=1)

# Variables to store the most recent scanned data for each scanner
prev_scanned_data_entry = {"Scanner 1": "", "Scanner 2": ""}
prev_scanned_data_exit = {"Scanner 1": "", "Scanner 2": ""}

# Function to send a heartbeat packet to the client
def send_heartbeat(conn):
    while True:
        time.sleep(3)  # Wait for 3 seconds
        try:
            conn.send('|HLT%\n'.encode('utf-8'))
        except Exception as e:
            print(f"Error sending heartbeat: {str(e)}")
            break

# Create threads for sending heartbeat packet
heartbeat_thread = threading.Thread(target=send_heartbeat, args=(conn,))
heartbeat_thread.daemon = True
heartbeat_thread.start()

# Function to read QR code data
def read_qr_code(scanner, scanner_name):
    global prev_scanned_data_entry, prev_scanned_data_exit

    while True:
        data = scanner.readline().decode('utf-8').strip()
        if data:
            # Check if the scanned data is different from the previous one
            if data != prev_scanned_data_entry[scanner_name] and data != prev_scanned_data_exit[scanner_name]:
                # Remove "TG" and "END" from the scanned data
                cleaned_data = data.replace("TG", "").replace("END", "")
                # Remove "QR" and "END" from the cleaned data
                cleaned_data = cleaned_data.replace("QR", "").replace("END", "")

                if cleaned_data.isnumeric():
                    protocol = "|ENCD-" if scanner_name == "Scanner 1" else "|EXCD-"
                else:
                    protocol = "|ENQR-" if scanner_name == "Scanner 1" else "|EXQR-"

                # Remove duplicate substrings if present
                cleaned_data = protocol + remove_duplicate_substring(cleaned_data) + "%" + '\n'
                print(f"Scanned by {scanner_name}: {cleaned_data}")
                conn.send(cleaned_data.encode('utf-8'))

                # Update the most recent scanned data
                if scanner_name == "Scanner 1":
                    prev_scanned_data_entry[scanner_name] = cleaned_data
                elif scanner_name == "Scanner 2":
                    prev_scanned_data_exit[scanner_name] = cleaned_data

# Create threads for reading from scanners
thread1 = threading.Thread(target=read_qr_code, args=(ENTRY, "Scanner 1"))
thread2 = threading.Thread(target=read_qr_code, args=(EXIT, "Scanner 2"))
thread1.daemon = True
thread2.daemon = True
thread1.start()
thread2.start()

# Main Loop
while True:
    # Handle data received from the client
    data = conn.recv(1024).decode('utf-8')  # Adjust the buffer size as needed
    if not data:
        break  # No data received, exit the loop

    # Process the received data
    response = ""

    if data.startswith("|"):
        start_index = data.find("|") + 1
        end_index = data.find("%")

        if start_index != -1 and end_index != -1:
            extracted_data = data[start_index:end_index]

            if extracted_data == "OPENEN":
                GPIO.output(ENTRY_RELAY_PIN, GPIO.LOW)  # Activate the entry relay
                time.sleep(1)
                GPIO.output(ENTRY_RELAY_PIN, GPIO.HIGH)  # Deactivate the entry relay
                time.sleep(1)
                response = "Entry Gate is opened"
                response = "|OK%"

            elif extracted_data == "OPENEX":
                GPIO.output(EXIT_RELAY_PIN, GPIO.LOW)  # Activate the exit relay
                time.sleep(1)
                GPIO.output(EXIT_RELAY_PIN, GPIO.HIGH)  # Deactivate the exit relay
                time.sleep(1)
                response = "Exit Gate is opened"
                response = "|OK%"

            elif extracted_data.startswith("ENQR-"):
                # Handle QR code data for entry
                qr_code = extracted_data[len("ENQR-"):].strip()
                # Implement your logic for entry QR code validation here
                if qr_code.isalnum():
                    response = "|OPENEN%"
                else:
                    response = "|INVALIDEN%"

            elif extracted_data.startswith("EXQR-"):
                # Handle QR code data for exit
                qr_code = extracted_data[len("EXQR-"):].strip()
                # Implement your logic for exit QR code validation here
                if qr_code.isalnum():
                    response = "|OPENEX%"
                else:
                    response = "|INVALIDEX%"

            elif extracted_data.startswith("ENCD-"):
                # Handle card data for entry
                card_data = extracted_data[len("ENCD-"):].strip()
                # Implement your logic for entry card data validation here
                if card_data.isnumeric():
                    response = "|OPENEN%"
                else:
                    response = "|INVALIDEN%"

            elif extracted_data.startswith("EXCD-"):
                # Handle card data for exit
                card_data = extracted_data[len("EXCD-"):].strip()
                # Implement your logic for exit card data validation here
                if card_data.isnumeric():
                    response = "|OPENEX%"
                else:
                    response = "|INVALIDEX%"

    print(f"Received data: {data}")
    print(f"Sending response: {response}")

    # Send the response back to the client
    try:
        conn.send(response.encode('utf-8'))
    except BrokenPipeError:
        print("Client disconnected")
        break  # Exit the loop if the client disconnected

# Clean up GPIO and close the connection when the loop exits
GPIO.cleanup()
conn.close()
