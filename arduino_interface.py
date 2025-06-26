import serial
import time
from config import ARDUINO_PORT, BAUD_RATE

class ArduinoController:
    def __init__(self):
        self.serial_conn = None
        self.connect()
    
    def connect(self):
        """Initialize serial connection to Arduino"""
        try:
            self.serial_conn = serial.Serial(
                port=ARDUINO_PORT,
                baudrate=BAUD_RATE,
                timeout=1
            )
            time.sleep(2)  # Wait for Arduino initialization
            return True
        except serial.SerialException as e:
            print(f"Arduino connection failed: {e}")
            return False
    
    def read_rfid(self):
        """Read patient ID from RFID scanner"""
        if not self.serial_conn:
            return None
            
        self.serial_conn.write(b'SCAN\n')
        return self.serial_conn.readline().decode().strip()
    
    def dispense_medicine(self, slot, quantity):
        """Send dispensing commands to Arduino"""
        command = f"DISPENSE:{slot}\n"
        for _ in range(quantity // 10):
            try:
                self.serial_conn.write(command.encode())
                response = self.serial_conn.readline().decode().strip()
                if response != "DONE":
                    return False
                time.sleep(0.5)
            except Exception as e:
                print(f"Dispensing error: {e}")
                return False
        return True