class MedicineDispenser:
    def __init__(self, arduino, sheets):
        self.arduino = arduino
        self.sheets = sheets
    
    def process_prescription(self, patient_id):
        """Full prescription logic from original code"""
        patient_data = self.sheets.get_patient_data(patient_id)
        medicines = self._extract_medicines(patient_data)
        
        for med in medicines:
            self.dispense_with_retry(med)
    
    def _extract_medicines(self, patient_data):
        """Medicine extraction logic from original code"""
        pass