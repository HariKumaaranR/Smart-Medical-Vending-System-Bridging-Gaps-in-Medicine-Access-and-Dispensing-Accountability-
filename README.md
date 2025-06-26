# Smart Medical Vending System 🏥💊

![System Demo](docs/demo.gif)

An end-to-end automated medicine dispensing solution with RFID authentication and cloud-based record keeping.

## Features ✨
- **Secure Patient Login** via RFID cards
- **Precision Medicine Dispensing** with servo-controlled mechanism
- **Real-time Inventory Tracking** with Google Sheets integration
- **Intuitive Staff Dashboard** built with Tkinter
- **Comprehensive Data Logging** for audit compliance

## Hardware Requirements 🔧
| Component | Quantity | Notes |
|-----------|----------|-------|
| Arduino Uno | 1 | Controller |
| RFID-RC522 | 1 | Patient authentication |
| SG90 Servo Motors | 4 | Continuous rotation |
| Stepper Motors | 2 | NEMA 17 recommended |
| Limit Switches | 2 | For homing position |

## Software Stack 💻

## flowchart TD
    A[Python GUI] --> B[Arduino Firmware]
    A --> C[Google Sheets API]
    B --> D[Servo Control]
    B --> E[Stepper Control]
    
Installation 🛠️
Arduino Setup
Install required libraries:
bash
arduino-cli lib install "MFRC522" "Servo"
Python Setup
bash

cd python
pip install -r requirements.txt
Configuration ⚙️
Update RFID UIDs in arduino/medical_vending.ino

Add Google Sheets credentials as credentials.json

Adjust dispensing parameters in config.json:

json
{
  "servo_rotation_time": 1000,
  "arduino_port": "COM4"
}
Usage 📋
Patient Authentication:

Scan registered RFID card

System verifies identity

Medicine Dispensing:

Select medication from GUI

System automatically positions and dispenses

Data Recording:

Transaction logged to Google Sheets

Inventory levels updated in real-time

Troubleshooting 🐞
Issue	Solution
Servo not rotating	Check pulse width settings
RFID not detected	Verify 3.3V connection
Sheets sync failure	Reauthenticate service account


Developed by 

HARIKUMAARAN R

SURYA KUMAR M

SHRUTHI S

DHARSHINI B

DIVYA DHARSHINI G



