from PIL import Image
import pytesseract
from pathlib import Path

class IDOCRProcessor:
    @staticmethod
    def load_names_from_file(filename):
        path = Path('./data', filename)
        with open(path, 'r') as f:
            return [line.strip().upper() for line in f if line.strip()]
        
    @staticmethod
    def extractInfoLocally(image_file):
        """ Locally extracts all words from photo, stores relevant info in local DB """
        try:
            firstNames = IDOCRProcessor.load_names_from_file('firsts.txt')
            lastNames = IDOCRProcessor.load_names_from_file('lasts.txt')

            image = Image.open(image_file).convert("L")  #L grayscale RGB colour
            text = pytesseract.image_to_string(image)
            lines = [line.strip() for line in text.split("\n") if line.strip()]

            # SPOT DOMICILIO
            domicilio_idx = next((i for i, line in enumerate(lines) if "DOMICILIO" in line), -1)
            
            if domicilio_idx != -1:
                # Everything before DOMICILIO could be names
                name_section = ' '.join(lines[:domicilio_idx])
                # Everything after is address
                address_section = ' '.join(lines[domicilio_idx+1:domicilio_idx+3])
                
                name_words = name_section.split()

                found_first_name = " ".join([word for word in name_words if word in firstNames])
                found_last_name = " ".join([word for word in name_words if word in lastNames])

                clean_text = "\n".join(lines)

                return {
                    "first_names": found_first_name,
                    "last_names": found_last_name,
                    "address": address_section,
                    "text": clean_text
                }

        except Exception as e:
            print(f"Error processing image: {e}")
            return {"error": str(e)}
     

