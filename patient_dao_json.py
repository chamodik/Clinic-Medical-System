# dao/patient_dao_json.py
#patients will be stored in patient.json, except for notes as they will be in records folder
import json
import os
from clinic.dao.patient_encoder import PatientEncoder
from clinic.dao.patient_decoder import PatientDecoder
from clinic.patient import Patient

class PatientDAOJSON:
    def __init__(self, autosave = False):
        self.patients = []  # Collection to store patient data
        self.autosave = autosave
        self.filepath = os.path.join("clinic", "patients.json")
        if self.autosave:
            self.load_patients() # Load from file if autosave is enabled

    def load_patients(self):
        """
        Load patients from a JSON file using PatientDecoder
        """
        try:
            with open(self.filepath, 'r') as file:
                data = json.load(file)
                self.patients = [PatientDecoder().decode(json.dumps(patient_data)) for patient_data in data]
        except(FileNotFoundError, json.JSONDecodeError):
            self.patients = []

    def save_patients(self):
        """
        Save patients to a JSON file using PatientEncoder
        """
        if self.autosave:
            with open(self.filepath, "w") as file:
                json.dump(self.patients, file, cls = PatientEncoder)
        """
    def clear_persistence(self):
        """
      #  Clear the JSON file to reset patient data
        """
        if self.autosave:
            with open(self.filepath, 'w') as file:
                file.write("[]")
            self.patients = []
        """

    def create_patient(self, patient):
        """Add a new patient to the collection."""
        self.patients.append(patient)
        if self.autosave == True:
            self.save_patients() # Save after creating a patient if autosave is enabled

    def retrieve_patient(self, phn):
        """Retrieve a patient by PHN."""
        for patient in self.patients:
            if patient.phn  == phn:
                return patient
        return None

    def update_patient(self, phn, updated_patient):
        """Update an existing patient's information."""
        for idx, patient in enumerate(self.patients):
            if patient.phn == phn:
                self.patients[idx] = updated_patient
                self.save_patients()
                return True
        return False
        

    def delete_patient(self, phn):
        """Remove a patient by PHN."""
        initial_count = len(self.patients)
        self.patients = [p for p in self.patients if p.phn != phn]
        self.save_patients()
        return len(self.patients) < initial_count # Returns true if a patient was removed 
        

    def list_patients(self):
        """Return all patients."""
        return self.patients
