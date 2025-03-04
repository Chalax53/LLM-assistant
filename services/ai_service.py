import os
from openai import OpenAI
from dotenv import load_dotenv
from flask import current_app
import requests
import json
from services.file_tracker import FileTracker
from ollama import chat
from ollama import Client
import logging


# Load environment variables
load_dotenv()
        

class LlamaAgent:
    """
    Service class to interact with locally running Llama 3.1 model via Ollama
    """
    
    def __init__(self):
        """Initialize the LlamaAgent with the Ollama API URL"""
        self.ollama_api_url = "http://localhost:11434/api/generate"
        self.temperature = 0.1
        self.max_tokens = 50
    
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
                "max_length": 50,
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



    def generate_file_status_message(self, client_name=None):
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
            context = f"""El {client_name} cliente ha subido su identificación y su estado de cuenta.
                Su solicitud está completa y lista para ser revizada por un experto de nuestro equipo.
                Hazle saber que un representante del banco se pondra en contacto con el pronto."""
        elif has_jpg:
            context = f"""El {client_name} cliente ha subido su identificación, menciona que solo falta subir 
                su estado de cuenta para completar su solicitud."""
        elif has_pdf:
            context = f"""El cliente {client_name} ha subido su estado de cuenta, pero aún falta su 
                INE para completar su solicitud."""
        else:
            context = f"""El cliente aún no ha subido ningún documento. Se requiere fotografia de su
                identificación y suarchivo de su estado de cuenta."""
        
        system_prompt = (
            "Eres un asistente que trabaja como empleado del banco BanBajio. "
            "Tu trabajo es informarle al cliente sobre el estado de los documentos que ha subido para su solicitud. "
            "Sé cordial, claro y específico sobre qué documentos se han recibido y cuáles faltan por subir."
            "No agregues información adicional que no esté relacionada con el estado de los documentos."
            "No des instrucciones de cómo subir los documentos."
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
            "Eres un asistente que trabaja como empleado del banco BanBajio. "
            "El cliente acaba de entrar a una plática contigo y debes decirle 'buen día.'"
            "Mencionale al cliente que estás aqui para ayudarle a llevar a cabo el primer paso para aplicar para un crédito empresarial."
            "No agregues información adicional que no esté relacionada con la aplicación a un crédito."
            "No des instrucciones, tu primer mensaje debe de ser de bienvenida y que puedes ayduar para aplicar para un crédito."
            "No felicites al cliente. Tu personalidad es de un agente serio y profesional."
            "Si preguntan cuánto dinero le van a prestar, explícales que el banco debe revisar sus documentos primero."
            "Si te dice que quiere una cantidad de dinero, menciona que lo primero es llevar a cabo el proceso de aplicación."
            "Si piden hablar con un humano, convéncelos de que tu ayuda es la manera más rápida y eficiente de obtener información."
            "Solamente existe un solo tipo de credito."
            "Responde de manera clara, concisa y profesional en español."
            "Manten tus mensajes en menos de 100 caracteres."
        )
        message = "Dale la bienvenida al cliente, menciona que estas aqui para ayudarle a aplicar a un crédito empresarial."
        
        return self.get_response(message, system_prompt)
    


class Ollama:
    def __init__(self, host="http://localhost:11434", temperature=0.1):
        self.client = Client(host=host)
        self.temperature = temperature
        
    # =============================================================================
    #
    #   NON-STREAMING RESPONSES
    #
    # =============================================================================
    def get_responseV2(self, message, custom_system_prompt=None):
        """
        Gets a response from the Llama 3.1 model using Ollama library
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
            
            response = self.client.chat(
                model="llama3.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                options= {
                    "temperature": self.temperature,
                    'num_predict': 100
                }
            )
            
            return response['message']['content']
        
        except Exception as e:
            logging.error(f"Error getting response from Ollama: {e}")
            return "No se pudo generar una respuesta."
    
    # prompt que se da para darle la bienvenida a usuario al inicio del chat
    def initial_greeting(self):
        system_prompt = (
            "Eres un asistente que trabaja como empleado del banco BanBajio. "
            "El cliente acaba de entrar a una plática contigo y debes decirle 'buen día.'"
            "Mencionale al cliente que estás aqui para ayudarle a llevar a cabo el primer paso para aplicar para un crédito empresarial."
            "No agregues información adicional que no esté relacionada con la aplicación a un crédito."
            "No des instrucciones, tu primer mensaje debe de ser de bienvenida y que puedes ayduar para aplicar para un crédito."
            "No felicites al cliente. Tu personalidad es de un agente serio y profesional."
            "Si preguntan cuánto dinero le van a prestar, explícales que el banco debe revisar sus documentos primero."
            "Si te dice que quiere una cantidad de dinero, menciona que lo primero es llevar a cabo el proceso de aplicación."
            "Si piden hablar con un humano, convéncelos de que tu ayuda es la manera más rápida y eficiente de obtener información."
            "Solamente existe un solo tipo de credito."
            "Responde de manera clara, concisa y profesional en español."
        )
        message = "Dale la bienvenida al cliente, menciona que estas aqui para ayudarle a aplicar a un crédito empresarial."
        return self.get_responseV2(message, system_prompt)
    

    # =============================================================================
    #
    #   STREAMING RESPONSES
    #
    # =============================================================================
    def get_response_stream(self, message, custom_system_prompt=None):
        print("=============================================================================")
        print("SYSTEM PROMPT")
        print(custom_system_prompt)
        print("=============================================================================")
        print("USER MESSAGE")
        print(message)
        print("=============================================================================")
        """
        Returns a generator that yields streamed responses
        """
        try:
            system_prompt = custom_system_prompt if custom_system_prompt else (
                "Eres un asistente que trabaja como empleado del banco BanBajio.\n"
                "Tu tarea es guiar a los usuarios en el proceso de solicitud de un préstamo.\n"
                "Menciona que se debe subir una foto de su INE y estado de cuenta.\n"
                "No pidas documentos adicionales.\n"
                "No hables sobre evaluar su dinero.\n"
                "Si preguntan cuánto dinero le van a prestar, explícales que el banco debe revisar sus documentos primero.\n"
                "Si piden hablar con un humano, convéncelos de que tu ayuda es la manera más rápida y eficiente de obtener información.\n"
                "Solamente existe un solo tipo de credito.\n"
                "Nunca asumas que el banco dara un credito.\n"
                "No preguntes si tiene alguna pregunta.\n"
                "Responde de manera clara, concisa y profesional en español."
            )
            print("============================ PROMPT =====================")
            print(system_prompt)
            print("============================ PROMPT =====================")
            response = self.client.chat(
                model="llama3.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                stream=True,
                options={
                    "temperature": self.temperature,
                    'num_predict': 150
                }
            )
            
            # Return a generator that yields each chunk
            for chunk in response:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
        
        except Exception as e:
            logging.error(f"Error streaming response from Ollama: {e}")
            yield "Error: No se pudo generar una respuesta."


    def initial_greeting_stream(self):
        system_prompt = (
            "El cliente acaba de entrar a una plática contigo y debes decirle 'buen día.'"
            "Mencionale al cliente que estás aqui para ayudarle a llevar a cabo el primer paso para aplicar para un crédito empresarial."
            "No agregues información adicional que no esté relacionada con la aplicación a un crédito."
            "No des instrucciones, tu primer mensaje debe de ser de bienvenida y que puedes ayduar para aplicar para un crédito."
            "No felicites al cliente. Tu personalidad es de un agente serio y profesional."
            "Si preguntan cuánto dinero le van a prestar, explícales que el banco debe revisar sus documentos primero."
            "Si te dice que quiere una cantidad de dinero, menciona que lo primero es llevar a cabo el proceso de aplicación."
            "Si piden hablar con un humano, convéncelos de que tu ayuda es la manera más rápida y eficiente de obtener información."
            "Solamente existe un solo tipo de credito."
            "Responde de manera clara, concisa y profesional en español."
        )
        message = "Dale la bienvenida al cliente, menciona que estas aqui para ayudarle a aplicar a un crédito empresarial."
        return self.get_response_stream(message, system_prompt)
    
    
    def generate_file_status_message_stream(self, client_name=None):
            """
            Generate a specific message about the current file upload status
            """
            
            system_prompt_base = (
                "Eres un asistente que trabaja como empleado del banco BanBajio.\n"
                "Tu trabajo es informarle al cliente sobre el estado de los documentos que ha subido para su solicitud.\n"
                "Los documentos se suben por medio de ti.\n"
                "No agregues información adicional que no esté relacionada con el estado de los documentos.\n"
                "No des instrucciones de cómo subir los documentos.\n"
                "No felicites al cliente. Tu personalidad es de un agente serio y profesional.\n"
                "Si preguntan cuánto dinero le van a prestar, explícales que el banco debe revisar sus documentos primero.\n"
                "Si piden hablar con un humano, convéncelos de que tu ayuda es la manera más rápida y eficiente de obtener información.\n"
                "Solamente existe un solo tipo de credito.\n"
                "No menciones nada sobre la situacion fiscal del cliente.\n"
                "Responde de manera clara, concisa y profesional en español."
            )

            # Get the current file status
            has_jpg = FileTracker.get_jpg_status()
            has_pdf = FileTracker.get_pdf_status()
            
            # Create a context prompt based on file status
            if has_jpg and has_pdf:
                system_prompt = (
                    f"{system_prompt_base}\n"
                    "Eres un asistente que trabaja como empleado del banco BanBajio.\n"
                    f"El cliente {client_name} ha subido ambos documentos requeridos.\n"
                    "Usa su nombre para dirigirte a el.\n"
                    "Menciona que su solicitud está completa y lista para ser revizada por un experto de nuestro equipo.\n"
                    "Mencionale que un representante del banco se pondra en contacto con el pronto.\n"
                )

            elif has_jpg:
                system_prompt = (
                    f"{system_prompt_base}\n"
                    f"El cliente {client_name} ha subido su identificación.\n"
                    "Usa su nombre para dirigirte a el.\n"
                    "Menciona que el siguiente paso es subir su estado de cuenta."
                )

            elif has_pdf:
                system_prompt = (
                    f"{system_prompt_base}\n"
                    f"El cliente ha subido su estado de cuenta.\n" 
                    "Menciona que solo falta subir una foto de su INE para continuar."
                )

            else:
                system_prompt = (
                    f"{system_prompt_base}\n"
                    f"El cliente aún no ha subido ningún documento.\n" 
                    "Recuerdale que para continuar se requiere de una fotografia de su INE y una copia de su estado de cuenta.\n"
                )

            message = "Cual es el estado actual de mis documentos?"
            
            return self.get_response_stream(message, custom_system_prompt=system_prompt)


    # Add your other methods here
