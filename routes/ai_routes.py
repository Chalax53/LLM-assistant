from flask import request, current_app
from flask_restful import Resource
from services.ai_service import AIAgent
from services.ai_service import LlamaAgent

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


class HealthCheck(Resource):
    def get(self):
        """Health check endpoint"""
        return {'status': 'ok'}, 200
    

class ChatWithLlama(Resource):
    def post(self):
        """
        Endpoint to chat with the Llama 3.1 model
        """
        try:
            data = request.get_json()
            
            if not data or 'message' not in data:
                return {'error': 'Message is required'}, 400
                
            message = data.get('message')
            
            llama_agent = LlamaAgent()
            response = llama_agent.get_response(message)
            
            return {
                'message': 'Response generated successfully',
                'data': {
                    'response': response
                }
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Error generating response: {str(e)}")
            return {'error': 'Failed to generate response'}, 500

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