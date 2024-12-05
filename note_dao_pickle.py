from clinic.dao.note_dao import NoteDAO
from clinic.note import Note
from pickle import load, dump
import pickle
import os

#will store notes in records under phn.dat

class NoteDAOPickle(NoteDAO):

    def __init__(self, phn, autosave = None, autocounter = None):

        self.phn = phn
        self.autosave = autosave
        self.counter = autocounter
        self.filepath = os.path.join('clinic', 'records', f"{self.phn}.dat")
        
        self.notes = self.load_notes()
        self.counter = autocounter

    def load_notes(self):
        """Load notes from the patient's record file."""
        try:
            with open(self.filepath, 'rb') as file:
                self.notes = pickle.load(file)
                return self.notes
        except FileNotFoundError:
            return []  # Return an empty list if the file does not exist yet

        
    def save_notes(self):
        try:
        # Open the file in binary write mode
            with open(self.filepath , 'wb') as file:
            # Serialize the list of notes and write it to the file
                pickle.dump(self.notes, file)

        except Exception as e:
            print(f"Error saving notes: {e}")

    def search_note(self, key):
        """Search for a note by its code."""
    
        index = key - 1  # Adjust for zero-based index
        if index < 0 or index >= len(self.notes):
            return None  # Return None if the index is out of range
        return self.notes[index]  # Return the note if index is valid

    def create_note(self, text, autosave):
        """Creating new note"""
        self.counter = max((note.code for note in self.notes if note), default=0) + 1
        
        new_note = Note(self.counter,text)
        self.notes.append(new_note)
        self.counter += 1

        if self.autosave == False: 
            print("autosave disabled")
        else:
            self.save_notes()
        return new_note
        
    def retrieve_notes(self, search_string):
        """retrieve list of objects matching the search string"""
        retrieved = []
         #look through current patient notes
        for notes in self.notes:
            if search_string in notes.text:
                retrieved.append(notes)
        return retrieved

    
    def update_note(self, key, text):
        """Update note based on Note code"""
        if len(self.notes) == 0:
            return False #cannot update note if there are no notes in record

        updated_note = Note(key, text)
        self.notes[key-1] = updated_note #search by key with a 0 based stored indexing
        
        if self.autosave == False: 
            print("autosave disabled")
        else:
            self.save_notes()
       
        return True
    
    def delete_note(self, key):
        """Delete Note using the Note code"""
        if (len(self.notes) == 0): #cannot delete if there are no notes
            return False
        
        
        if (len(self.notes) >= 1): #there are notes to delete
            index = key - 1
            if index < 0 or index >= len(self.notes):
                return False  # Return False if the index is out of range

            self.notes[index] = None #set note to none to 
            
            if self.autosave == False: 
                print("autosave disabled")
            else:
                self.save_notes()
            
            return True
    
    def list_notes(self):
        """Listing all Non None notes"""
        not_none = []
        for note in self.notes:
            if note is not None:
                not_none.insert(0,note) #insert the new note at the front of the array
        return not_none
