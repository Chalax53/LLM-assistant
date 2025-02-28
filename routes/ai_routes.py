from flask import request, current_app
from flask_restful import Resource
from services.ai_service import AIAgent
from services.ai_service import LlamaAgent
from services.localOCRService import OCRTextProcessor
from services.file_tracker import FileTracker

class GreetUser(Resource):
    def post(self):
        """
        Endpoint to greet a user using AI Agent
        """

        try:    
            ai_service = AIAgent()
            greeting = ai_service.initial_greeting()
            
            return {
                'message': 'Greeting generated successfully',
                'data': {
                    'greeting': greeting
                }
            }, 201
            
        except Exception as e:
            current_app.logger.error(f"Error generating greeting: {str(e)}")
            return {'error': 'Failed to generate greeting'}, 500


class ChatWithLlama(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data or 'message' not in data:
                return {'error': 'Message is required'}, 400
                
            message = data.get('message')
            
            llama_agent = LlamaAgent()

            # Check if file status might be relevant to this message
            # status_relevant = any(keyword in message.lower() for keyword in 
            #                     ['status', 'document', 'archivo', 'documento', 
            #                      'subir', 'upload', 'ine', 'pdf', 'jpg', 
            #                      'estado'])
            
            response = llama_agent.get_response(message)
            
            status_message = None
            # if status_relevant:
            #    status_message = llama_agent.generate_file_status_message()

            return {
                'message': 'Response generated successfully',
                'data': {
                    'response': response,
                    'status_update': status_message
                }
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
        

class InitialGreeting(Resource):
    def post(self):
        """
        Endpoint to get an initial greeting from the AI agent
        """
        try:
            llama_agent = LlamaAgent()
            greeting = llama_agent.initial_greeting()
            
            return {
                'message': 'Greeting generated successfully',
                'data': {
                    'greeting': greeting
                }
            }, 201
            
        except Exception as e:
            current_app.logger.error(f"Error generating greeting: {str(e)}")
            return {'error': 'Failed to generate greeting'}, 500
        
class UploadFile(Resource):
    def post(self):
        """
        Endpoint that handles uploaded files
        """
        try:
            if 'file' not in request.files:
                return {'error': 'No file uploaded'}, 400

            file = request.files['file']
            if file.filename == '':
                return {'error': 'No selected file'}, 400

            # Check file extension
            if not self.allowed_file(file.filename):
                return {'error': 'Invalid file type. Only PDF and JPG are allowed'}, 400
            

            if file.filename.lower().endswith('.pdf'):
                result = OCRTextProcessor.extract_name_from_EdoCta(file)
                print("First Names:", result)
                FileTracker.set_pdf()
                llama_agent = LlamaAgent()
                status_message = llama_agent.generate_file_status_message()
                
                return {
                    'message': 'PDF file uploaded successfully',
                    'data': {
                        'extracted_names': result,
                        'status': status_message
                    }
                }, 200

            elif file.filename.lower().endswith(('.jpg', '.jpeg')):
                result = OCRTextProcessor.extractIDData(file)
                print(result.get('first_names'))
                FileTracker.set_jpg()

                llama_agent = LlamaAgent()
                status_message = llama_agent.generate_file_status_message()
                
                return {
                    'message': 'PDF file uploaded successfully',
                    'data': {
                        'extracted_names': result,
                        'status': status_message
                    }
                }, 200

            return {'message': 'File uploaded successfully'}, 200
            
        except Exception as e:
            current_app.logger.error(f"Error generating response: {str(e)}")
            return {'error': 'Failed to generate response'}, 500
        
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg'}
    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS