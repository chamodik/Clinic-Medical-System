from clinic.note import Note
from clinic.dao.note_dao_pickle import NoteDAOPickle
from pickle import load, dump

class PatientRecord:
    
    """ autocounter
    - all patients in the database
    - connected to patient noter
    """

    #initializing fields
    def __init__(self, phn, autosave = None):
        
        self.phn = phn 
        self.autosave = autosave
        # self.note_dao = NoteDAOPickle(self.autosave) #holds self.patient_notes = [] field now
        # self.patient_notes = []
        self.counter = 0
        self.note_dao = NoteDAOPickle(self.phn, self.autosave, self.counter) #holds self.patient_notes = [] field now


    def add_note(self, text, autosave):
        self.counter += 1
        return self.note_dao.create_note(text, autosave)

    #refacored Note_Dao method
    def retrieve_note_list(self, string_search):
        return self.note_dao.retrieve_notes(string_search)
    
    #refactored Note_Dao
    def search_for_note(self, code):
        """Search for a note by its code."""
        return self.note_dao.search_note(code)
    
    #refactored Note_dao
    def update(self, key , updated_txt):
        return self.note_dao.update_note(key, updated_txt)  
    
    #refactored Note_dao
    def remove_note(self, code):
        return self.note_dao.delete_note(code)

    #refactored Note_dao
    def list_record(self):
        return self.note_dao.list_notes()
