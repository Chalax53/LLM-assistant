import logging
import threading
from ollama import Client

# Singleton OllamaClient to maintain a persistent connection
class OllamaClient:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, host="http://localhost:11434"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(OllamaClient, cls).__new__(cls)
                cls._instance.client = Client(host=host)
                cls._instance.keep_alive_thread = None
                logging.info("Created persistent Ollama client connection")
            return cls._instance
    
    def get_client(self):
        """Get the ollama client instance"""
        return self.client