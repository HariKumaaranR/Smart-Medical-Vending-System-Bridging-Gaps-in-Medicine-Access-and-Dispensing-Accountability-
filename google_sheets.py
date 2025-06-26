import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import SPREADSHEET_ID, CREDENTIALS_FILE

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
            print(f"Google Sheets connection failed: {e}")
            return False
    
    def get_patient_data(self, patient_id):
        """Fetch patient records from sheet"""
        try:
            sheet = self.client.open_by_key(SPREADSHEET_ID)
            worksheet = sheet.worksheet("Patients")
            records = worksheet.get_all_records()
            return next((p for p in records if p['ID'] == patient_id), None)
        except Exception as e:
            print(f"Error fetching patient data: {e}")
            return None
    
    def update_balance(self, patient_id, new_balance):
        """Update patient balance in sheet"""
        # Implementation from your original code
        pass