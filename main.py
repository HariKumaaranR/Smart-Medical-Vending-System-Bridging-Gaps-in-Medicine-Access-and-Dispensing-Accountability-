import tkinter as tk
from gui_components import AuthWindow
from arduino_interface import ArduinoController
from google_sheets import SheetsManager

class MedicalVendingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Medical Vending")
        self.root.geometry("1024x768")
        
        self.arduino = ArduinoController()
        self.sheets = SheetsManager()
        
        self.show_auth_screen()
    
    def show_auth_screen(self):
        AuthWindow(self.root, self.on_auth_success)
    
    def on_auth_success(self, patient_id):
        from gui_components import PatientDashboard
        PatientDashboard(self.root, patient_id)

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalVendingApp(root)
    root.mainloop()