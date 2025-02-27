import os
from openai import OpenAI
from dotenv import load_dotenv
from flask import current_app
import requests
import json
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
        self.temperature = 0.7
        self.max_tokens = 100
    
    def get_response(self, message):
        """
        Gets a response from the Llama 3.1 model for a given message
        """
        try:
            system_prompt = (
                "Eres un asistente de inteligencia artificial que trabaja como empleado de un banco. "
                "Tu tarea es guiar a los usuarios en el proceso de solicitud de un préstamo. "
                "Para continuar con el proceso, necesitan subir dos documentos: una foto de su INE y un PDF de su estado de cuenta. "
                "Si preguntan cuánto dinero le van a prestar, explícales que el banco debe revisar sus documentos primero. "
                "Si piden hablar con un humano, convéncelos de que tu ayuda es la manera más rápida y eficiente "
                "de obtener información."
                "Solamente existe un solo tipo de credito."
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
            
            if response.status_code != 200:
                current_app.logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                raise Exception(f"Ollama API returned status code {response.status_code}")
            
            result = response.json()
            return result.get("response", "")
            
        except requests.RequestException as e:
            current_app.logger.error(f"Request error: {str(e)}")
            raise Exception(f"Error connecting to Ollama: {str(e)}")
        except json.JSONDecodeError as e:
            current_app.logger.error(f"JSON decode error: {str(e)}")
            raise Exception("Invalid response from Ollama API")
        except Exception as e:
            current_app.logger.error(f"Unexpected error: {str(e)}")
            raise
    
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