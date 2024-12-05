# dao/patient_decoder.py
import json
from clinic.patient import Patient

class PatientDecoder(json.JSONDecoder):
    def __init__(self):
        super().__init__(object_hook=self.object_hook)

    def object_hook(self, obj):
        if "phn" in obj:
            return Patient(
                phn=obj["phn"],
                name=obj["name"],
                birth_date=obj["birth_date"],
                phone=obj["phone"],
                email=obj["email"],
                address=obj["address"]
            )
        return obj
