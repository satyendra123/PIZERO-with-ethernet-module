import socket
import time
import RPi.GPIO as GPIO
import serial
import threading

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
HOST = '192.168.1.107'  # Listen on all available interfaces
PORT = 6000  # Choose a port number
current_ip = HOST  # Initialize the current IP address

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print('Connected by', addr)

# Initialize serial communication with QR scanners
ENTRY = serial.Serial('/dev/ttyAMA0', baudrate=115200, timeout=1)
EXIT = serial.Serial('/dev/ttyAMA1', baudrate=115200, timeout=1)

# Variables to store previously scanned data
prev_scanned_data_entry = ""
prev_scanned_data_exit = ""

# Function to send a heartbeat packet to the client
def send_heartbeat(conn):
    while True:
        time.sleep(5)  # Wait for 5 seconds
        try:
            conn.send('|HLT%\n'.encode('utf-8'))
        except Exception as e:
            print(f"Error sending heartbeat: {str(e)}")
            break

# Create threads for sending heartbeat packet
heartbeat_thread = threading.Thread(target=send_heartbeat, args=(conn,))
heartbeat_thread.daemon = True
heartbeat_thread.start()

# Function to read QR code from a scanner
def read_qr_code(scanner, scanner_name):
    prev_scanned_data_entry = ""
    prev_scanned_data_exit = ""
    while True:
        data = scanner.readline().decode('utf-8').strip()
        if data:
            if data.isnumeric():
                # Numeric data is treated as tag data
                protocol = "|ENCD-" if scanner_name == "Scanner 1" else "|EXCD-"
                tag_data_with_protocol = protocol + data + "%" + '\n'
                print(f"Scanned by {scanner_name}: {tag_data_with_protocol}")
                if scanner_name == "Scanner 1" and data != prev_scanned_data_entry:
                    conn.send(tag_data_with_protocol.encode('utf-8'))
                    prev_scanned_data_entry = data
                elif scanner_name == "Scanner 2" and data != prev_scanned_data_exit:
                    conn.send(tag_data_with_protocol.encode('utf-8'))
                    prev_scanned_data_exit = data
            else:
                # Non-numeric data is treated as QR data
                protocol = "|ENQR-" if scanner_name == "Scanner 1" else "|EXQR-"
                qr_data_with_protocol = protocol + data + "%" + '\n'
                print(f"Scanned by {scanner_name}: {qr_data_with_protocol}")
                if scanner_name == "Scanner 1" and data != prev_scanned_data_entry:
                    conn.send(qr_data_with_protocol.encode('utf-8'))
                    prev_scanned_data_entry = data
                elif scanner_name == "Scanner 2" and data != prev_scanned_data_exit:
                    conn.send(qr_data_with_protocol.encode('utf-8'))
                    prev_scanned_data_exit = data

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
                time.sleep(2)
                GPIO.output(ENTRY_RELAY_PIN, GPIO.HIGH)  # Deactivate the entry relay
                time.sleep(2)
                response = "Entry Gate is opened"
            elif extracted_data == "OPENEX":
                GPIO.output(EXIT_RELAY_PIN, GPIO.LOW)  # Activate the exit relay
                time.sleep(2)
                GPIO.output(EXIT_RELAY_PIN, GPIO.HIGH)  # Deactivate the exit relay
                time.sleep(2)
                response = "Exit Gate is opened"
            elif extracted_data.startswith("ENQR-") or extracted_data.startswith("EXQR-"):
                # Handle QR code data similarly to how you did before

                # Extract and send the QR code data
                try:
                    conn.send(extracted_data.encode('utf-8'))
                except BrokenPipeError:
                    print("Client disconnected")
                    break  # Exit the loop if the client disconnected
                
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
