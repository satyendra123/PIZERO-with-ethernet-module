import serial
import time 
import threading  # Import the threading module for parallel processing

# Configure the serial ports for the two scanners
ser1 = serial.Serial('/dev/ttyAMA0', baudrate=115200, timeout=1)
ser2 = serial.Serial('/dev/ttyAMA1', baudrate=115200, timeout=1)  

def read_qr_code(ser):
    ser.write(b'READ_QR\r\n')  # Send command to read QR code
    response = ser.readline()  # Read response from scanner
    return response.decode('utf-8').strip()

def scanner_thread(ser):
    try:
        while True:
            qr_code = read_qr_code(ser)
            if qr_code:
                print("QR Entry Code from Scanner:", ser.name, qr_code)
    except KeyboardInterrupt:
        ser.close()

def main():
    try:
        # Create threads for both scanners
        thread1 = threading.Thread(target=scanner_thread, args=(ser1,))
        thread2 = threading.Thread(target=scanner_thread, args=(ser2,))

        # Start the threads
        thread1.start()
        thread2.start()

        # Wait for both threads to finish
        thread1.join()
        thread2.join()

    except KeyboardInterrupt:
        ser1.close()
        ser2.close()

if __name__ == "__main__":
    main()



