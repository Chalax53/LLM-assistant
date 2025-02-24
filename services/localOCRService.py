from PIL import Image
import pytesseract
from pathlib import Path
import pdfplumber
import re
from models.id_record import IDRecord

#
# Parses files and creates JSON with relevant data
#
class OCRTextProcessor:
    @staticmethod
    def load_names_from_file(filename):
        path = Path('./data', filename)
        with open(path, 'r') as f:
            return [line.strip().upper() for line in f if line.strip()]
        
    #
    # Uses OCR to read data from ID Photo in jpeg or jpg format.
    #
    @staticmethod
    def extractIDData(image_file):
        """ Locally extracts all words from ID photo, stores relevant info in local DB """
        try:
            firstNames = OCRTextProcessor.load_names_from_file('firsts.txt')
            lastNames = OCRTextProcessor.load_names_from_file('lasts.txt')

            image = Image.open(image_file).convert("L")  #L grayscale RGB colour
            text = pytesseract.image_to_string(image)
            lines = [line.strip() for line in text.split("\n") if line.strip()]

            # SPOT DOMICILIO
            domicilio_idx = next((i for i, line in enumerate(lines) if "DOMICILIO" in line), -1)

            #TODO: handle when DOMICILIO isn't found

            if domicilio_idx != -1:
                # Everything before DOMICILIO could be names
                name_section = ' '.join(lines[:domicilio_idx])
                # Everything after is address
                address_section = ' '.join(lines[domicilio_idx+1:domicilio_idx+3])
                
                name_words = name_section.split()

                found_first_name = " ".join([word for word in name_words if word in firstNames])
                found_last_names = " ".join([word for word in name_words if word in lastNames])

                clean_text = "\n".join(lines)
                print(clean_text) # <- FOR TESTING PURPOSES. Prints all that is parsed

                full_name = f"{found_first_name} {found_last_names}".strip()
                
                #create idRecord object, populate it and store it in db.
                #TODO: Create a repository to handle DB interactions.
                idRecord = IDRecord(
                    full_name=full_name,
                    address=address_section
                )
                idRecord.save()

                return {
                    "first_names": found_first_name,
                    "last_names": found_last_names,
                    "address": address_section, # <- FOR TESTING PURPOSES. DELETE FOR DEMO.
                    "text": clean_text # <- FOR TESTING PURPOSES. DELETE FOR DEMO.
                }

        except Exception as e:
            print(f"Error processing image: {e}")
            return {"error": str(e)}
            

    #
    # Uses pdfplumber to read data from Estado de Cuenta in PDF format.
    #
    def extractEdoCtaData(file):
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
                print(text)
                
            # With Regex, extract relevant data from all parsed text
            date_pattern = r'\d{1,2}/\d{1,2}/\d{2,4}'
            address_pattern = r'\d+\s+[A-Za-z\s,]+\s+[A-Z]{2}\s+\d{5}'
            
            dates = re.findall(date_pattern, text)
            addresses = re.findall(address_pattern, text)
            print("======RELEVANT DATA=======")
            print(dates)
            print(addresses)

            #TODO: Create a repository to handle DB interactions and store data in DB.

            return {
                'dates': dates,
                'addresses': addresses
            }

