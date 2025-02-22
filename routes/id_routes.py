from flask import request
from flask_restful import Resource
from werkzeug.utils import secure_filename
import os
from models.id_record import IDRecord
from models.cuenta_record import CuentaRecord
from services.ocr_service import OCRService
from services.localOCRService import IDOCRProcessor

# APIS
class IDProcessing(Resource):
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        
    def post(self):
        if 'file' not in request.files:
            return {'error': 'No file provided'}, 400
            
        file = request.files['file']
        if file.filename == '':
            return {'error': 'No file selected'}, 400
            
        if file and self._allowed_file(file.filename):
            # Process the file directly from the request
            info = OCRService.extract_info_from_image(file)
            if not info:
                return {'error': 'Failed to process image after info = OCRService.extract_info_from_image(file) in id_routes.py'}, 500
            
            record = IDRecord(
                full_name=info['full_name'],
                address=info['address'],
                #id_image_path=file.filename  # Save filename or URL if you need. No need for now i guess
            )
            record_id = record.save()
            
            return {
                'message': 'ID processed successfully',
                'record_id': record_id,
                'data': info
            }, 201
            
        return {'error': 'Invalid file type'}, 400
    
    def _allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg'}

#Process Estado de Cta
class EstadoDeCuentaProcessing(Resource):
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        
    def post(self):
        if 'file' not in request.files:
            return {'error': 'No file provided'}, 400
            
        file = request.files['file']
        if file.filename == '':
            return {'error': 'No file selected'}, 400
            
        if file and self._allowed_file(file.filename):
            # Process the file directly from the request
            info = OCRService.extract_info_from_estado_cuenta(file)
            if not info:
                return {'error': 'Failed to process image after info = OCRService.extract_info_from_image(file) in id_routes.py'}, 500
            
            estadoCuenta = CuentaRecord(
                full_name=info['full_name'],
                address=info['address'],
                fecha_corte=['fecha_corte']
            )
            estado_id = estadoCuenta.save()
            
            # This return is what we see on postman as a response.
            return {
                'message': 'Estado de Cuenta processed successfully',
                'estadoCuenta_id': estado_id,
                'data': info
            }, 201
        
        return {'error': 'Invalid file type'}, 400
    
    def _allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg'}


#Processes photo and returns relevant data
class IDLocalProcessing(Resource):  
    def post(self):
        if 'file' not in request.files:
            return {'error': 'No file provided'}, 400
            
        file = request.files['file']
        if file.filename == '':
            return {'error': 'No file selected'}, 400
            
        if file and self._allowed_file(file.filename):
            # Process the file directly from the request
            info = OCRService.extractInfoLocally(file)
            if not info:
                return {'error': 'Failed to process image after info = OCRService.extractInfoLocally(file) in id_routes.py'}, 500
            
            # estadoCuenta = CuentaRecord(
            #     full_name=info['full_name'],
            #     address=info['address'],
            #     fecha_corte=['fecha_corte']
            # )
            # estado_id = estadoCuenta.save()
            
            # This return is what we see on postman as a response.
            return {
                'message': 'Estado de Cuenta processed successfully',
                #'estadoCuenta_id': estado_id,
                'data': info
            }, 201
            
        return {'error': 'Invalid file type'}, 400
    
    def _allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg'}


class IDLocalProcessingV2(Resource):  
    def post(self):
        if 'file' not in request.files:
            return {'error': 'No file provided'}, 400
            
        file = request.files['file']
        if file.filename == '':
            return {'error': 'No file selected'}, 400
            
        if file and self._allowed_file(file.filename):
            # Process the file directly from the request
            info = IDOCRProcessor.extractInfoLocally(file)
            if not info:
                return {'error': 'Failed to process image after info = OCRService.extractInfoLocally(file) in id_routes.py'}, 500
            
            full_name = f"{info['first_names']} {info['last_names']}".strip()
            idRecord = IDRecord(
                full_name=full_name,
                address=info['address']
            )
            idRecord.save()
            
            # This return is what we see on postman as a response.
            return {
                'message': 'ID processed successfully',
                'data': info
            }, 201
            
        return {'error': 'Invalid file type'}, 400
    
    def _allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg'}


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
        

