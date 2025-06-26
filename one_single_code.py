"""
SMART MEDICAL VENDING SYSTEM
A complete RFID-authenticated medicine dispenser with Google Sheets integration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import serial
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import random
from threading import Thread

# ========== CONFIGURATION ==========
ARDUINO_PORT = "COM4"
BAUD_RATE = 9600
RFID_TIMEOUT = 5
SPREADSHEET_ID = "your-spreadsheet-id"
CREDENTIALS_FILE = "credentials.json"
PATIENT_SHEET = "Patients"
MEDICINE_SHEET = "Medicines"

# ========== HARDWARE CONTROL ==========
class ArduinoHandler:
    def __init__(self):
        self.serial_conn = None
        self.connect()
    
    def connect(self):
        """Initialize serial connection to Arduino"""
        try:
            self.serial_conn = serial.Serial(
                port=ARDUINO_PORT,
                baudrate=BAUD_RATE,
                timeout=RFID_TIMEOUT
            )
            time.sleep(2)  # Wait for Arduino initialization
            return True
        except serial.SerialException as e:
            messagebox.showerror("Hardware Error", f"Arduino connection failed:\n{str(e)}")
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
                self.serial_conn.reset_input_buffer()
                self.serial_conn.write(command.encode())
                response = self.serial_conn.readline().decode().strip()
                if response != "DONE":
                    return False
                time.sleep(0.5)
            except Exception as e:
                messagebox.showerror("Dispensing Error", f"Hardware communication failed:\n{str(e)}")
                return False
        return True

# ========== DATA MANAGEMENT ==========
class SheetsManager:
    def __init__(self):
        self.client = None
        self.connect()
    
    def connect(self):
        """Authenticate with Google Sheets API"""
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                CREDENTIALS_FILE, scope)
            self.client = gspread.authorize(creds)
            return True
        except Exception as e:
            messagebox.showerror("Cloud Error", f"Google Sheets connection failed:\n{str(e)}")
            return False
    
    def get_patient_data(self, patient_id):
        """Fetch patient records from sheet"""
        try:
            sheet = self.client.open_by_key(SPREADSHEET_ID)
            worksheet = sheet.worksheet(PATIENT_SHEET)
            records = worksheet.get_all_records()
            return next((p for p in records if p['ID'] == patient_id), None)
        except Exception as e:
            messagebox.showerror("Data Error", f"Failed to fetch patient data:\n{str(e)}")
            return None
    
    def update_balance(self, patient_id, amount):
        """Update patient balance in sheet"""
        try:
            sheet = self.client.open_by_key(SPREADSHEET_ID)
            worksheet = sheet.worksheet(PATIENT_SHEET)
            
            # Find patient row
            cell = worksheet.find(patient_id)
            balance_col = worksheet.find("Balance").col
            
            # Update value
            worksheet.update_cell(cell.row, balance_col, amount)
            return True
        except Exception as e:
            messagebox.showerror("Update Error", f"Failed to update balance:\n{str(e)}")
            return False

# ========== USER INTERFACE ==========
class AuthWindow(tk.Frame):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.pack(expand=True, fill=tk.BOTH)
        
        self.arduino = ArduinoHandler()
        self.on_success = on_success
        
        # UI Components
        ttk.Label(self, text="MEDICAL VENDING SYSTEM", font=("Arial", 18, "bold")).pack(pady=20)
        
        ttk.Button(
            self, 
            text="SCAN RFID CARD", 
            command=self.scan_rfid,
            style="Accent.TButton"
        ).pack(pady=15, ipadx=20, ipady=10)
        
        ttk.Separator(self, orient="horizontal").pack(fill=tk.X, pady=20)
        
        # Manual Login Frame
        manual_frame = ttk.Frame(self)
        manual_frame.pack()
        
        ttk.Label(manual_frame, text="Manual Login", font=("Arial", 12)).pack(pady=5)
        
        self.user_entry = ttk.Entry(manual_frame, width=20)
        self.user_entry.pack(pady=5)
        
        self.pass_entry = ttk.Entry(manual_frame, width=20, show="*")
        self.pass_entry.pack(pady=5)
        
        ttk.Button(
            manual_frame,
            text="LOGIN",
            command=self.manual_login
        ).pack(pady=10)
        
        # Configure Styles
        self.style = ttk.Style()
        self.style.configure("Accent.TButton", foreground="white", background="#4CAF50", font=("Arial", 12, "bold"))
    
    def scan_rfid(self):
        """Handle RFID scanning process"""
        if not self.arduino.connect():
            messagebox.showwarning("Hardware", "Arduino not connected")
            return
            
        patient_id = self.arduino.read_rfid()
        if patient_id:
            self.on_success(patient_id)
        else:
            messagebox.showerror("Scan Failed", "Could not read RFID card")
    
    def manual_login(self):
        """Handle manual credentials login"""
        username = self.user_entry.get()
        password = self.pass_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        # In a real system, validate against database
        self.on_success("DEMO123")  # Bypass for testing

class PatientDashboard(tk.Frame):
    def __init__(self, parent, patient_id):
        super().__init__(parent)
        self.pack(expand=True, fill=tk.BOTH)
        
        self.sheets = SheetsManager()
        self.arduino = ArduinoHandler()
        self.patient_id = patient_id
        
        self.load_data()
        self.create_ui()
    
    def load_data(self):
        """Fetch patient and medicine data"""
        self.patient_data = self.sheets.get_patient_data(self.patient_id)
        if not self.patient_data:
            messagebox.showerror("Error", "Patient record not found")
            self.master.destroy()
            return
            
        # Load medicine data
        sheet = self.sheets.client.open_by_key(SPREADSHEET_ID)
        self.medicines = sheet.worksheet(MEDICINE_SHEET).get_all_records()
    
    def create_ui(self):
        """Build the patient dashboard"""
        # Header Frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(
            header_frame,
            text=f"PATIENT: {self.patient_data['Name']}",
            font=("Arial", 14, "bold")
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            header_frame,
            text=f"BALANCE: ${self.patient_data.get('Balance', 0)}",
            font=("Arial", 12)
        ).pack(side=tk.RIGHT)
        
        # Medicine Table
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scroll_y = ttk.Scrollbar(table_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=("Medicine", "Dosage", "Frequency", "Stock"),
            show="headings",
            yscrollcommand=scroll_y.set,
            height=8
        )
        
        # Configure columns
        self.tree.heading("Medicine", text="Medicine")
        self.tree.heading("Dosage", text="Dosage")
        self.tree.heading("Frequency", text="Frequency")
        self.tree.heading("Stock", text="In Stock")
        
        self.tree.column("Medicine", width=200)
        self.tree.column("Dosage", width=100, anchor=tk.CENTER)
        self.tree.column("Frequency", width=150, anchor=tk.CENTER)
        self.tree.column("Stock", width=80, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        scroll_y.config(command=self.tree.yview)
        
        # Populate table
        for med in self.patient_data.get("Prescriptions", []):
            self.tree.insert("", tk.END, values=(
                med["Name"],
                med["Dosage"],
                med["Frequency"],
                med["Stock"]
            ))
        
        # Control Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(
            button_frame,
            text="DISPENSE SELECTED",
            command=self.dispense_selected,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="VIEW BILLING",
            command=self.show_billing
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="LOGOUT",
            command=self.logout
        ).pack(side=tk.RIGHT)
    
    def dispense_selected(self):
        """Handle medicine dispensing"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "No medicines selected")
            return
            
        for item in selected:
            med_data = self.tree.item(item)['values']
            med_name = med_data[0]
            quantity = med_data[1].split()[0]  # Extract numeric dosage
            
            # Find medicine in inventory
            medicine = next((m for m in self.medicines if m['Name'] == med_name), None)
            if not medicine:
                messagebox.showerror("Error", f"{med_name} not found in inventory")
                continue
                
            # Dispense via Arduino
            if not self.arduino.dispense_medicine(medicine['Slot'], int(quantity)):
                messagebox.showerror("Error", f"Failed to dispense {med_name}")
                return
                
            # Update stock
            self.update_stock(medicine, quantity)
            
        messagebox.showinfo("Success", "Medicines dispensed successfully")
    
    def update_stock(self, medicine, quantity):
        """Update medicine stock in Sheets"""
        # Implementation would connect to Sheets API
        print(f"Updating stock for {medicine['Name']} (-{quantity})")
    
    def show_billing(self):
        """Show billing information"""
        # Implementation would show billing window
        messagebox.showinfo("Billing", "Billing feature coming soon")
    
    def logout(self):
        """Return to login screen"""
        self.master.destroy()
        root = tk.Tk()
        app = MedicalVendingApp(root)
        root.mainloop()

# ========== MAIN APPLICATION ==========
class MedicalVendingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Medical Vending System")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure("Accent.TButton", 
                           foreground="white",
                           background="#4CAF50",
                           font=("Arial", 12, "bold"))
        
        self.show_auth_screen()
    
    def show_auth_screen(self):
        """Display authentication window"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        AuthWindow(self.root, self.on_auth_success)
    
    def on_auth_success(self, patient_id):
        """Handle successful authentication"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        PatientDashboard(self.root, patient_id)

# ========== RUN APPLICATION ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalVendingApp(root)
    root.mainloop()