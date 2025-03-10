from dotenv import load_dotenv
from services.file_tracker import FileTracker
from services.ollama_manager import OllamaClient
import logging


load_dotenv()  

class Ollama:
    def __init__(self, host="http://localhost:11434", temperature=0.1):
        self.client_manager = OllamaClient(host=host)
        self.client = self.client_manager.get_client()
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
            system_prompt = custom_system_prompt if custom_system_prompt else (
                "Eres un asistente pragmatico que trabaja como empleado de un banco."
                "Tu tarea es guiar a los usuarios en el proceso de solicitud de un préstamo."
                "Para continuar con el proceso, necesitan subir dos documentos: una foto de su INE y un PDF de su estado de cuenta. "
                "No le preguntes al cliente nada."
                "No preguntes si quiere continuar."
                "Si preguntan cuánto dinero le van a prestar, dí que el primer paso es aplicar."
                "Si piden hablar con un humano, convéncelos de que tu ayuda es la manera más rápida y eficiente de obtener información."
                "Solamente existe un solo tipo de credito: credito empresarial."
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
    
    def initial_greeting(self):
        system_prompt = (
            "El cliente acaba de entrar a una plática contigo y debes decirle 'buen día.'\n"
            "Mencionale al cliente que estás aqui para ayudarle a llevar a cabo el primer paso para aplicar para un crédito empresarial.\n"
            "Menciona que si decide continuar, BanBajio mantendrá su información privada.\n"
            "Mencionale al cliente que consulte nuestro aviso de privacidad.\n"
            "No agregues información adicional que no esté relacionada con la aplicación a un crédito.\n"
            "No des instrucciones, tu primer mensaje debe de ser de bienvenida y que puedes ayduar para aplicar a un crédito.\n"
            "No felicites al cliente. Tu personalidad es de un asistente serio y profesional.\n"
            "Si preguntan cuánto dinero le van a prestar, explícales que el primer paso es aplicar.\n"
            "Si te dice que quiere una cantidad de dinero, menciona que lo primero es llevar a cabo el proceso de aplicación.\n"
            "Si piden hablar con un humano, convéncelos de que tu ayuda es la manera más rápida y eficiente de obtener información.\n"
            "Responde de manera clara, concisa y profesional en español.\n"
        )
        message = "Dale la bienvenida al cliente, menciona que estas aqui para ayudarle a aplicar a un crédito empresarial."
        return self.get_responseV2(message, system_prompt)
    

    # =============================================================================
    #
    #   STREAMING RESPONSES
    #
    # =============================================================================
    def get_response_stream(self, message, custom_system_prompt=None):
        """
        Returns a generator that yields streamed responses
        """
        try:
            system_prompt = custom_system_prompt if custom_system_prompt else (
                "Eres un asistente que trabaja como empleado del banco BanBajio.\n"
                "Tu tarea es guiar a los usuarios en el proceso de solicitud de un préstamo.\n"
                "Menciona que se debe subir una foto de su INE y estado de cuenta.\n"
                "No le preguntes nada al cliente.\n"
                "Nunca preguntes si quiere continuar.\n"
                "No pidas documentos adicionales.\n"
                "No hables sobre evaluar su dinero.\n"
                "No hables mucho, manten tus respuestas muy cortas y concisas.\n"
                "Nunca hables sobre cantidad de prestamo.\n"
                "Si dice que sí quiere continuar, pídele una foto de su INE.\n"
                "Si preguntan cuánto dinero le van a prestar, explícales que el banco debe revisar sus documentos primero.\n"
                "Si piden hablar con un humano, convéncelos de que tu ayuda es la manera más rápida y eficiente de obtener información.\n"
                "Si pregunta por la privacidad de sus documentos, menciona que lean nuestro aviso de privacidad.\n"
                "Solamente existe un solo tipo de credito: credito empresarial.\n"
                "Nunca menciones cantidad de préstamo.\n"
                "Si preguntan cuanto dinero le van a prestar, menciona que primero hay que aplicar.\n"
                "No preguntes si tiene alguna pregunta.\n"
                "Responde de manera clara, concisa y profesional en español."
            )
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
            "Tienes que mencionar que sus documentos se usarán únicamente para iniciar el proceso de aplicación de crédito, puede encontrar más infomracion en el aviso de privacidad."
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
                "Si preguntan sobre privacidad, haz referencia al aviso de privacidad.\n"
                "Si piden hablar con un humano, convéncelos de que tu ayuda es la manera más rápida y eficiente de obtener información.\n"
                "Solamente existe un solo tipo de credito.\n"
                "No menciones nada sobre la situacion fiscal del cliente.\n"
                "Responde de manera clara, concisa y profesional en español."
            )

            has_jpg = FileTracker.get_jpg_status()
            has_pdf = FileTracker.get_pdf_status()
            
            if has_jpg and has_pdf:
                system_prompt = (
                    f"{system_prompt_base}\n"
                    "Eres un asistente que trabaja como empleado del banco BanBajio.\n"
                    f"El cliente {client_name} ha subido ambos documentos requeridos.\n"
                    "Usa su nombre para dirigirte a el.\n"
                    "Menciona que su solicitud está completa y lista para ser revizada por un experto de nuestro equipo.\n"
                    "Mencionale que un representante del banco se pondra en contacto con el pronto.\n"
                    "Genera una respuesta corta."
                )

            elif has_jpg:
                system_prompt = (
                    f"{system_prompt_base}\n"
                    f"El cliente {client_name} ha subido su identificación.\n"
                    "Usa su nombre para dirigirte a el.\n"
                    "Ya has hablado con el antes, no des la bienvenida.\n"
                    "Solamente di que falta subir su estado de cuenta.\n"
                    "Menciona que el siguiente paso es subir su estado de cuenta."
                    "Genera una respuesta corta."
                )

            elif has_pdf:
                system_prompt = (
                    f"{system_prompt_base}\n"
                    f"El cliente ha subido su estado de cuenta.\n" 
                    "Menciona que solo falta subir una foto de su INE para continuar."
                    "Genera una respuesta corta."
                )

            else:
                system_prompt = (
                    f"{system_prompt_base}\n"
                    f"El cliente aún no ha subido ningún documento.\n" 
                    "Recuerdale que para continuar se requiere de una fotografia de su INE y una copia de su estado de cuenta.\n"
                )

            message = "Cual es el estado actual de mis documentos?"
            
            return self.get_response_stream(message, custom_system_prompt=system_prompt)