#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>

// RFID Configuration
#define SS_PIN 10
#define RST_PIN 9
MFRC522 mfrc522(SS_PIN, RST_PIN);

// Servo Motors (Continuous Rotation)
Servo servo1, servo2, servo3, servo4;

// Stepper Motor Pins
#define DIR_PIN_VERT 2
#define STEP_PIN_VERT 3
#define DIR_PIN_HORIZ 4
#define STEP_PIN_HORIZ 5

// Limit Switches
#define LIMIT_SW_VERT 6
#define LIMIT_SW_HORIZ 7

// Patient RFID UIDs (Update with your actual cards)
byte patient1UID[] = {0x73, 0xC1, 0xEF, 0x19};
byte patient2UID[] = {0x03, 0xF1, 0x3A, 0xDA};
byte patient3UID[] = {0x13, 0x63, 0xE3, 0xD9};

// Dispensing Parameters
const int ROTATION_TIME = 1000;  // ms for 1 full rotation
const int SERVO_CW = 0;          // Clockwise speed
const int SERVO_CCW = 180;       // Counter-clockwise speed
const int SERVO_STOP = 90;       // Stop position

// Movement Constants (Adjust based on your mechanism)
const long VERT_STEPS_FULL = 4900;
const long VERT_STEPS_HALF = 2200;
const long HORIZ_STEPS = 1700;
const int STEP_DELAY = 800;      // microseconds

String currentPatientID = "";
bool systemReady = false;

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();

  // Servo Setup
  servo1.attach(8, 1000, 2000);
  servo2.attach(11, 1000, 2000);
  servo3.attach(A0, 1000, 2000);
  servo4.attach(A1, 1000, 2000);
  stopAllServos();

  // Stepper Setup
  pinMode(DIR_PIN_VERT, OUTPUT);
  pinMode(STEP_PIN_VERT, OUTPUT);
  pinMode(DIR_PIN_HORIZ, OUTPUT);
  pinMode(STEP_PIN_HORIZ, OUTPUT);

  // Limit Switch Setup
  pinMode(LIMIT_SW_VERT, INPUT_PULLUP);
  pinMode(LIMIT_SW_HORIZ, INPUT_PULLUP);

  // Homing Sequence
  homeVertical();
  homeHorizontal();
  
  systemReady = true;
  Serial.println("SYSTEM_READY");
}

void loop() {
  handleSerialCommands();
  
  if (systemReady) {
    checkRFID();
  }
}

void handleSerialCommands() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "SCAN") {
      startRFIDScan();
    } 
    else if (command.startsWith("DISPENSE:")) {
      int slot = command.substring(9).toInt();
      if (slot >= 1 && slot <= 4) {
        dispenseMedicine(slot);
        Serial.println("DISPENSE_COMPLETE:" + String(slot));
      }
    }
    else if (command == "HOME") {
      homeVertical();
      homeHorizontal();
      Serial.println("HOMING_COMPLETE");
    }
  }
}

void startRFIDScan() {
  Serial.println("SCANNING_STARTED");
  unsigned long startTime = millis();
  bool cardDetected = false;

  while (millis() - startTime < 5000) {  // 5 second timeout
    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
      cardDetected = true;
      break;
    }
    delay(100);
  }

  if (cardDetected) {
    if (compareUID(mfrc522.uid.uidByte, patient1UID)) {
      currentPatientID = "PATIENT_01";
    } 
    else if (compareUID(mfrc522.uid.uidByte, patient2UID)) {
      currentPatientID = "PATIENT_02";
    }
    else if (compareUID(mfrc522.uid.uidByte, patient3UID)) {
      currentPatientID = "PATIENT_03";
    }
    else {
      currentPatientID = "UNKNOWN_CARD";
    }
    
    Serial.println("RFID_DETECTED:" + currentPatientID);
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
  } else {
    Serial.println("SCAN_TIMEOUT");
  }
}

bool compareUID(byte *readUID, byte *storedUID) {
  for (byte i = 0; i < 4; i++) {
    if (readUID[i] != storedUID[i]) {
      return false;
    }
  }
  return true;
}

void dispenseMedicine(int slot) {
  switch(slot) {
    case 1:  // Top-Right
      moveVertical(false, VERT_STEPS_FULL);
      moveHorizontal(true, HORIZ_STEPS);
      rotateServo(servo1);
      moveHorizontal(false, HORIZ_STEPS);
      moveVertical(true, VERT_STEPS_FULL);
      break;
      
    case 2:  // Top-Left
      moveVertical(false, VERT_STEPS_FULL);
      rotateServo(servo2);
      moveVertical(true, VERT_STEPS_FULL);
      break;
      
    case 3:  // Bottom-Right
      moveVertical(false, VERT_STEPS_HALF);
      moveHorizontal(true, HORIZ_STEPS);
      rotateServo(servo3);
      moveHorizontal(false, HORIZ_STEPS);
      moveVertical(true, VERT_STEPS_HALF);
      break;
      
    case 4:  // Bottom-Left
      moveVertical(false, VERT_STEPS_HALF);
      rotateServo(servo4);
      moveVertical(true, VERT_STEPS_HALF);
      break;
  }
}

void rotateServo(Servo &servo) {
  servo.write(SERVO_CCW);  // Rotate counter-clockwise
  delay(ROTATION_TIME);
  servo.write(SERVO_STOP); // Stop servo
  delay(300);              // Stabilization delay
}

void stopAllServos() {
  servo1.write(SERVO_STOP);
  servo2.write(SERVO_STOP);
  servo3.write(SERVO_STOP);
  servo4.write(SERVO_STOP);
}

// Stepper Motor Functions
void moveVertical(bool up, long steps) {
  digitalWrite(DIR_PIN_VERT, up ? HIGH : LOW);
  for (long i = 0; i < steps; i++) {
    if (digitalRead(LIMIT_SW_VERT) == LOW && !up) break;
    digitalWrite(STEP_PIN_VERT, HIGH);
    delayMicroseconds(STEP_DELAY);
    digitalWrite(STEP_PIN_VERT, LOW);
    delayMicroseconds(STEP_DELAY);
  }
}

void moveHorizontal(bool left, long steps) {
  digitalWrite(DIR_PIN_HORIZ, left ? HIGH : LOW);
  for (long i = 0; i < steps; i++) {
    if (digitalRead(LIMIT_SW_HORIZ) == LOW && left) break;
    digitalWrite(STEP_PIN_HORIZ, HIGH);
    delayMicroseconds(STEP_DELAY);
    digitalWrite(STEP_PIN_HORIZ, LOW);
    delayMicroseconds(STEP_DELAY);
  }
}

void homeVertical() {
  digitalWrite(DIR_PIN_VERT, HIGH); // Move up
  while (digitalRead(LIMIT_SW_VERT) == HIGH) {
    digitalWrite(STEP_PIN_VERT, HIGH);
    delayMicroseconds(STEP_DELAY);
    digitalWrite(STEP_PIN_VERT, LOW);
    delayMicroseconds(STEP_DELAY);
  }
  moveVertical(false, 100); // Back off slightly
}

void homeHorizontal() {
  digitalWrite(DIR_PIN_HORIZ, LOW); // Move right
  while (digitalRead(LIMIT_SW_HORIZ) == HIGH) {
    digitalWrite(STEP_PIN_HORIZ, HIGH);
    delayMicroseconds(STEP_DELAY);
    digitalWrite(STEP_PIN_HORIZ, LOW);
    delayMicroseconds(STEP_DELAY);
  }
  moveHorizontal(true, 100); // Back off slightly
}