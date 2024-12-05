from datetime import datetime

class Note:
    
    def __init__(self, code, text):
        self.code = code
        self.text = text
        self.timestamp = datetime.now()
        
    def __eq__(self, other):
        if isinstance(other, Note):
            return self.code == other.code and self.text == other.text
        return False
        
    def __str__(self):
        return f"Note({self.code}, {self.text})"
    
