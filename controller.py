import os
from clinic.patient import Patient 
from clinic.patient_record import PatientRecord
from clinic.note import Note
from clinic.exception.invalid_login_exception import InvalidLoginException
from clinic.exception.duplicate_login_exception import DuplicateLoginException
from clinic.exception.invalid_logout_exception import InvalidLogoutException
from clinic.exception.illegal_access_exception import IllegalAccessException
from clinic.exception.illegal_operation_exception import IllegalOperationException
from clinic.exception.no_current_patient_exception import NoCurrentPatientException
import hashlib
from clinic.dao.patient_dao_json import PatientDAOJSON

class Controller:
    
    def __init__(self, autosave = None):
        
        self.users = self.load_users()
        self.autosave = autosave
        self.is_logged_in = None #login status to help with double login
        self.patient_record = {} #list to hold Patient instances
        self.current_patient = None #current patient isnt chosen by default
        self.patient_dao = PatientDAOJSON()  # Using PatientDAOJSON for patient management
        self.patient_dao = PatientDAOJSON(autosave = self.autosave) # Pass autosave to DAO
        self.patient_dao.load_patients() # Initial load of patients
        """
        # Clear persistence at the start of each test run if autosave is enabled
        if self. autosave:
            self.patient_dao.clear_persistence()
        """

    def load_users(self):
        """ load users that is stores in users.txt into saved users to access login"""
        users = {}
        
        with open( 'clinic/users.txt', 'r') as file: #open users.txt file
            for line in file:
                line = line.strip() #clean up whitespaces in the lines
                if line:  # Only process non-empty lines
                    username, password_hash = line.split(",") #assign username and password according to the split
                    users[username] = password_hash  # Add to saved users database
        return users #assing to self.users
    
    def get_password_hash(self, password):
        """ turn the plaintext password user enters into a hashcode to compare"""
        encoded_password = password.encode('utf-8')     # Convert the password to bytes
        hash_object = hashlib.sha256(encoded_password)      # Choose a hashing algorithm (e.g., SHA-256)
        hex_dig = hash_object.hexdigest()       # Get the hexadecimal digest of the hashed password
        return hex_dig


    def login(self, username, password):
        """user enters username and plaintext password, the password is converted 
            into has and information is compared to the users database to login"""

        if self.is_logged_in is not None: 
            raise DuplicateLoginException #cannot login again if already logged in 
            return False
    
        if username in self.users:
            entered_password_hash = self.get_password_hash(password)
            if self.users[username] == entered_password_hash:
                self.is_logged_in = username # Store the logged-in username
                return True
            else:
                raise InvalidLoginException("Invalid username or password.")
        else:
            raise InvalidLoginException("Invalid username or password.")
            


    def logout(self):
        """
        Logs out if currently logged in
        """
        # Check if there is an active login
        if self.is_logged_in is None:
            raise InvalidLogoutException("Cannot log out if not logged in.")

        self.is_logged_in = None # Clear the login state
        return True


    def create_patient(self, phn, name, birth_date, phone, email, address):
        """Create a new patient if they don't exist and add them to the patient records.

        """
        # Check if the user is logged in
        if not self.is_logged_in:
            raise IllegalAccessException("User must be logged in to cireate a patient.")

        # Check if the patient already exists
        if self.patient_dao.retrieve_patient(phn):
            raise IllegalOperationException(f"Patient with PHN {phn} already exists.")

        new_patient = Patient(phn, name, birth_date, phone, email, address)
        self.patient_dao.create_patient(new_patient)
        
        return new_patient
    
    def search_patient(self, phn):
        """Search for a patient by their PHN

        """
        if not self.is_logged_in:
            raise IllegalAccessException

        return self.patient_dao.retrieve_patient(phn) # Search via DAO


    def retrieve_patients(self, query):
        """
        Retrieve all patients in the patient record
        """
        if not self.is_logged_in:
            raise IllegalAccessException("User must be logged in to retrieve patients.")

        if not query.strip():
            return self.patient_dao.list_patients()

        # Retrieve the list of patients from patient_dao
        retrieved = []
        for patient in self.patient_dao.list_patients():
            if query.lower() in patient.name.lower():
                retrieved.append(patient)

        return retrieved


    def update_patient(self, key , phn, name, birth_date, phone, email, address):
        """
        Update details of an existing patient
        """
        if not self.is_logged_in:
            raise IllegalAccessException("Patient not found.")

        if self.current_patient and self.current_patient.phn == key:
            raise IllegalOperationException("Cannot update the current patient.")

        # Retrieve the patient to update
        patient = self.patient_dao.retrieve_patient(key)
        if not patient:
            raise IllegalOperationException("Patient not found.")

        # Check for duplicate PHN
        existing_patient = self.patient_dao.retrieve_patient(phn)
        if existing_patient and existing_patient.phn != key:
            raise IllegalOperationException("Cannot update patient and assign a registered PHN.")

        # Update patient details
        patient.phn = phn
        patient.name = name
        patient.birth_date = birth_date
        patient.phone = phone
        patient.email = email
        patient.address = address

        # Update patient in DAO, changing the key if PHN is updated
        if phn != key:
            self.patient_dao.delete_patient(key)
            self.patient_dao.create_patient(patient)  # Add updated patient with new PHN
        else:
            self.patient_dao.update_patient(key, patient)

        return True

    def delete_patient(self, phn):
        """
        Delete a patient from the record based on their PHN
        """
        if not self.is_logged_in:
            raise IllegalAccessException("User must be logged in to delete a patient.")

        if self.current_patient and self.current_patient.phn == phn:
            raise IllegalOperationException("Cannot delete the current patient.")

        patient = self.patient_dao.retrieve_patient(phn)
        if not patient:
            raise IllegalOperationException("Patient not found.")

        success = self.patient_dao.delete_patient(phn)
        if not success:
            raise IllegalOperationException("Failed to delete patient.")
        return success

    def list_patients(self):
        """
        List all patients currently in the record
        """
        if not self.is_logged_in:
            raise IllegalAccessException("User must be logged in to list patients.")

        return self.patient_dao.list_patients()  # Get all patients from DAO
        


    def get_current_patient(self):
        """
        Retrieve the current patient by PHN
        """
        if not self.is_logged_in:
            raise IllegalAccessException

        return self.current_patient


    def set_current_patient(self, phn):
        """
        Set the current patient by PHN if they exist in the DAO
        """
        if not self.is_logged_in:
            raise IllegalAccessException("User must be logged in to set a current patient.")

        patient = self.patient_dao.retrieve_patient(phn)
        
        if patient:
            self.current_patient = patient
            return f"Patient with PHN {phn} set successfully."
        else:
            raise IllegalOperationException("Patient with PHN not found.")

    def unset_current_patient(self):
        """
        Unset the current patient by PHN.
        If the current patient matches the provided PHN, it will be unset.
        """
        if not self.is_logged_in:
            raise IllegalAccessException

        self.current_patient = None


    def create_note(self, text):
        if not self.is_logged_in:
            raise IllegalAccessException
        
        
        # Check if there is a current patient
        if self.current_patient is None:
            raise NoCurrentPatientException
            
        
        # If both conditions are met, proceed with note creation


        return self.current_patient.record.add_note(text, autosave=self.autosave)


    def retrieve_notes(self, text):
        if not self.is_logged_in:
            raise IllegalAccessException #cannot access method without loggin in
        
        if self.current_patient is not None: # if current_patient is set
            return self.current_patient.record.retrieve_note_list(text) #method to access current_patient record field
        else:
            raise NoCurrentPatientException #no current patient set to retrieve their notes


    def update_note(self, code, updated_txt):
        if not self.is_logged_in:
            raise IllegalAccessException
            

        if self.current_patient is None: #current Patient not set
            raise NoCurrentPatientException
            
        return self.current_patient.record.update(code, updated_txt)


    def search_note(self, code):
        if not self.is_logged_in:
            raise IllegalAccessException
            
        
        if self.current_patient is None:
            raise NoCurrentPatientException
            
        return self.current_patient.record.search_for_note(code)


    def delete_note(self, code):
        if  not self.is_logged_in:
            raise IllegalAccessException
            
        
        if self.current_patient is not None:
            success = self.current_patient.record.remove_note(code)
            return success
            
        else:
            raise NoCurrentPatientException
        


    def list_notes(self):
        if not self.is_logged_in: #will not proceed if user is not logged in
            raise IllegalAccessException
            
        
        if self.current_patient is not None: # current patient is set
            return self.current_patient.record.list_record()
        else:
            raise NoCurrentPatientException #current patient not set so cannot display notes

