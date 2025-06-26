# Smart Medical Vending System 💊

![System Overview](docs/system_overview.png)  
*Automated medicine dispensing with RFID authentication and Arduino control*

## 📌 Key Features
- **RFID Patient Authentication** (with manual login fallback)
- **Google Sheets Integration** for real-time data sync
- **Arduino-controlled Dispensing** with serial communication
- **Complete Billing System** with balance tracking
- **Responsive Tkinter GUI** with 10+ interactive screens

## 🛠️ Tech Stack
| Component       | Technology Used           |
|-----------------|---------------------------|
| **Backend**     | Python 3.8+               |
| **Frontend**    | Tkinter (Custom themed UI)|
| **Hardware**    | Arduino Uno + RFID-RC522  |
| **Cloud Sync**  | Google Sheets API         |
| **Dependencies**| `pyserial`, `gspread`     |

## 📂 Project Structure
```bash
smart-medical-vending/
├── main.py                 # Entry point
├── hardware/               # All Arduino communication
│   ├── arduino_manager.py  # (200+ lines) Serial control
│   └── dispenser.py        # (150+ lines) Motor logic
├── data/                   # Data handling
│   ├── google_sheets.py    # (150+ lines) API integration
│   └── patient_records.py  # (100+ lines) Data processing
├── ui/                     # User interface
│   ├── auth_screens.py     # (150+ lines) Login UI
│   ├── patient_dash.py     # (200+ lines) Main dashboard
│   └── billing_ui.py       # (150+ lines) Payment screens
└── config.py               # 50+ configuration constants