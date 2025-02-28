import os
from openai import OpenAI
from dotenv import load_dotenv
from flask import current_app
import requests
import json
from services.file_tracker import FileTracker

# Load environment variables
load_dotenv()

class AIAgent:
    """Service to interact with the OpenAI ChatGPT API"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-4o-mini"  # You can change this to other models as needed
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)

    def initial_greeting(self):
        """
        Generate a greeting for the user using ChatGPT
        """

        prompt = f"""
        You are a bank representative and your job is to provide information about the documents needed
        to start a loan application. The user has the ability to upload these documents through this chat.
        The two documents you need are 'INE' and 'Estado de Cuenta.'
        If the user asks to talk to a representative, you need to convince him that you are the most efficient
        and quick way of getting an answer from the bank regarding his loan.

        """
       
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a friendly assistant that greets users."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=100
            )
            
            greeting = completion.choices[0].message.content.strip()
            return greeting
            
        except Exception as e:
            raise Exception(f"Error calling ChatGPT API: {str(e)}")
        

class LlamaAgent:
    """
    Service class to interact with locally running Llama 3.1 model via Ollama
    """
    
    def __init__(self):
        """Initialize the LlamaAgent with the Ollama API URL"""
        self.ollama_api_url = "http://localhost:11434/api/generate"
        self.temperature = 0.1
        self.max_tokens = 65
    
    def get_response(self, message, custom_system_prompt=None):
        """
        Gets a response from the Llama 3.1 model for a given message
        """
        try:
            # Use default system prompt if no custom prompt is provided
            system_prompt = custom_system_prompt if custom_system_prompt else (
                "Eres un asistente pragmatico que trabaja como empleado de un banco."
                "Tu tarea es guiar a los usuarios en el proceso de solicitud de un préstamo."
                "Para continuar con el proceso, necesitan subir dos documentos: una foto de su INE y un PDF de su estado de cuenta. "
                "Si preguntan cuánto dinero le van a prestar, explícales que el banco debe revisar sus documentos primero. "
                "Si piden hablar con un humano, convéncelos de que tu ayuda es la manera más rápida y eficiente de obtener información."
                "Solamente existe un solo tipo de credito."
                "Nunca asumas que el banco dara un credito, primero se deben de estudiar sus documentos."
                "Responde de manera clara, concisa y profesional en español."
        )
            payload = {
                "model": "llama3.1",
                "prompt": message,
                "system": system_prompt,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False
            }
            
            response = requests.post(self.ollama_api_url, json=payload)
            response.raise_for_status()

            result = response.json()
            return result.get("response", "No se pudo generar una respuesta.")
            
            
        except requests.exceptions.RequestException as e:
            # Log the error and return a user-friendly message
            if 'current_app' in globals():  # Check if we're in a Flask context
                current_app.logger.error(f"Request error: {str(e)}")
            else:
                print(f"Request error: {str(e)}")
            return "Lo siento, estoy teniendo problemas técnicos para conectarme con el servicio de IA en este momento."
            
        except json.JSONDecodeError as e:
            # Log the error and return a user-friendly message
            if 'current_app' in globals():
                current_app.logger.error(f"JSON decode error: {str(e)}")
            else:
                print(f"JSON decode error: {str(e)}")
            return "Lo siento, recibí una respuesta inválida del servicio de IA."
            
        except Exception as e:
            # Log the error and return a user-friendly message
            if 'current_app' in globals():
                current_app.logger.error(f"Unexpected error: {str(e)}")
            else:
                print(f"Unexpected error: {str(e)}")
            return "Ha ocurrido un error inesperado al procesar tu solicitud."



    def generate_file_status_message(self):
        """
        Generate a specific message about the current file upload status
        
        Returns:
            str: AI-generated message about file upload status
        """
        # Get the current file status
        has_jpg = FileTracker.get_jpg_status()
        has_pdf = FileTracker.get_pdf_status()
        
        # Create a context prompt based on file status
        if has_jpg and has_pdf:
            context = f"""El cliente ha subido exitosamente tanto su identificación 
                como su estado de cuenta. Su solicitud está completa y lista para ser revizada por el equipo.
                Hazle saber que un representante del banco se pondra en contacto con el prontamente."""
        elif has_jpg:
            context = f"""El cliente ha subido su identificación, pero aún 
                falta su estado de cuenta para completar su solicitud. Dile que por favor suba su Estado de Cuenta"""
        elif has_pdf:
            context = f"""El cliente ha subido su estado de cuenta, pero aún falta su 
                identificación INE para completar su solicitud. Pidele por favor que suba una foto de su INE."""
        else:
            context = f"""El cliente aún no ha subido ningún documento. Se requiere fotografia de su
                identificación y suarchivo de su estado de cuenta."""
        
        system_prompt = (
            "Eres un asistente que trabaja como empleado del banco BanBajio. "
            "Tu trabajo es informarle al cliente sobre el estado de los documentos que ha subido para su solicitud. "
            "Sé cordial, claro y específico sobre qué documentos se han recibido y cuáles faltan por subir."
            "No agregues información adicional que no esté relacionada con el estado de los documentos."
            "No felicites al cliente. Tu personalidad es de un agente serio y profesional."
            "Si preguntan cuánto dinero le van a prestar, explícales que el banco debe revisar sus documentos primero. "
            "Si piden hablar con un humano, convéncelos de que tu ayuda es la manera más rápida y eficiente de obtener información."
            "Solamente existe un solo tipo de credito."
            "Responde de manera clara, concisa y profesional en español."
        )
        
        message = f"Basado en la siguiente información sobre los documentos del cliente, genera un mensaje claro y amable: {context}"
        
        return self.get_response(message, custom_system_prompt=system_prompt)















    
    def initial_greeting(self):
        """
        Generates an initial greeting using the Llama 3.1 model
        
        Returns:
            str: A friendly greeting message
        """
        system_prompt = (
            "You are an AI bank clerk assisting customers who want to apply for a loan. "
            "Your goal is to guide them through the initial steps, which require uploading two documents: a photo of the INE and a bank statement PDF. "
            "Do not disclose loan amounts, as further verification is needed. "
            "If the user asks how much they can borrow, politely explain that it depends on additional review steps. "
            "If they ask to speak to a human, persuade them that you provide the fastest and most efficient assistance. "
            "Be professional, concise, and reassuring."
        )
        message = "Generate a brief, friendly greeting to welcome a user to a new conversation as if you were a bank clerk."
        
        return self.get_response(message, system_prompt, temperature=0.7, max_tokens=100)