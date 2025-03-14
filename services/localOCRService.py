from PIL import Image
import pytesseract
from pathlib import Path
import pdfplumber
import re
from models.id_record import IDRecord

class OCRTextProcessor:
    @staticmethod
    def load_names_from_file(filename):
        path = Path('./data', filename)
        with open(path, 'r') as f:
            return [line.strip().upper() for line in f if line.strip()]
        
    @staticmethod
    def extractIDData(image_file):
        """ Locally extracts all words from ID photo, stores relevant info in local DB 
        Uses OCR to read data from ID Photo in jpeg or jpg format."""
        try:
            firstNames = OCRTextProcessor.load_names_from_file('firsts.txt')
            lastNames = OCRTextProcessor.load_names_from_file('lasts.txt')

            image = Image.open(image_file).convert("L")  #L grayscale RGB colour
            text = pytesseract.image_to_string(image)
            lines = [line.strip() for line in text.split("\n") if line.strip()]

            # SPOT DOMICILIO
            domicilio_idx = next((i for i, line in enumerate(lines) if "DOMICILIO" in line), -1)

            if domicilio_idx != -1:
                name_section = ' '.join(lines[:domicilio_idx])
                address_section = ' '.join(lines[domicilio_idx+1:domicilio_idx+3])
                
                name_words = name_section.split()

                found_first_name = " ".join([word for word in name_words if word in firstNames])
                found_last_names = " ".join([word for word in name_words if word in lastNames])

                clean_text = "\n".join(lines)

                full_name = f"{found_first_name} {found_last_names}".strip()
                
                idRecord = IDRecord(
                    full_name=full_name,
                    address=address_section
                )
                idRecord.save()

                return {
                    "first_names": found_first_name,
                    "last_names": found_last_names,
                }

        except Exception as e:
            print(f"Error processing image: {e}")
            return {"error": str(e)}
            


    def extract_name_from_EdoCta(file):
        """
        Uses pdfplumber to read data from Estado de Cuenta in PDF format.
        checks if the last entry on the names database is found in the PDF.
        Returns full name found in pdf
        """
        idRecord = IDRecord()
        last_entry = idRecord.get_last_entry()
        full_name = last_entry['full_name']

        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
                print(text)

        pattern = r'\b' + re.escape(full_name.upper()) + r'\b'
        
        match = re.search(pattern, text)

        if match:
            print(f"Found '{full_name}' in all caps in the PDF")
            return full_name
        else:
            words = full_name.upper().split()
            flexible_pattern = r'\s*'.join([r'\b' + re.escape(word) + r'\b' for word in words])
            flexible_match = re.search(flexible_pattern, text)
            
            if flexible_match:
                print(f"Found '{full_name}' with some formatting variations in the PDF")
                return full_name
            else:
                print(f"Could not find '{full_name}' in the PDF")
                return "estimado"    
    