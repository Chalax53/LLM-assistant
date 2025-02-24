from flask import request
from flask_restful import Resource
from werkzeug.utils import secure_filename
import os
from models.id_record import IDRecord
from models.cuenta_record import CuentaRecord
from services.ocr_service import OCRService
from services.localOCRService import OCRTextProcessor
from flask import current_app
from functools import wraps

# CONTROLLER

#
# Ensures correct file is received
#
def require_file(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'file' not in request.files:
            return {'error': 'No file provided'}, 400
        file = request.files['file']
        if file.filename == '':
            return {'error': 'No file selected'}, 400
        return f(*args, **kwargs)
    return decorated


#
# Parses text from ID photo and returns JSON with full_name and address
# Stores data in DB
#
class ParseIDPhoto(Resource):
    ALLOWED_EXTENSIONS = {'jpeg', 'jpg'}

    @require_file
    def post(self):
        file = request.files['file']
        if not self._allowed_file(file.filename):
            return {'error': 'Invalid file type'}, 400
            
        try:
            info = OCRTextProcessor.extractIDData(file)
        except Exception as e:
            current_app.logger.error(f"Error processing file: {str(e)}")
            return {'error': 'Failed to process image after Service'}, 500
            
        return {
            'message': 'ID Photo processed successfully',
            'data': info
        }, 201

    def _allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS


#
# Parses and stores estado de cuenta Name and Date in DB.
# Returns name and date
#
class ParseEdoCtaPDF(Resource):
    ALLOWED_EXTENSIONS = {'pdf'}

    @require_file
    def post(self):
        file = request.files['file']
        if not self._allowed_file(file.filename):
            return {'error': 'Invalid file type'}, 400
            
        try:
            info = OCRTextProcessor.extractEdoCtaData(file)
        except Exception as e:
            current_app.logger.error(f"Error processing file: {str(e)}")
            return {'error': 'Failed to process image after Service'}, 500
            
        return {
            'message': 'Estado de Cuenta processed successfully',
            'data': info
        }, 201
    
    def _allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS


#GETS ALL
class GetAllRecords(Resource):
    def get(self):
        try:
            # Get all records from the database
            records = IDRecord.get_all()  # You may need to implement `get_all` in your IDRecord model

            if not records:
                return {"message": "No records found"}, 404

            # Return the records as a list of dictionaries
            return {"records": records}, 200

        except Exception as e:
            return {"error": str(e)}, 500
        

