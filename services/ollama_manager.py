import logging
import threading
import time
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
                cls._instance._start_keep_alive()
                logging.info("Created persistent Ollama client connection")
            return cls._instance
    
    def _start_keep_alive(self):
        """Start a background thread to keep the model warm"""
        if self.keep_alive_thread is None or not self.keep_alive_thread.is_alive():
            self.keep_alive_thread = threading.Thread(target=self._keep_model_warm, daemon=True)
            self.keep_alive_thread.start()
            logging.info("Started Ollama keep-alive thread")
    
    def _keep_model_warm(self):
        """Periodically send a small request to keep the model loaded in memory"""
        while True:
            try:
                # Send a minimal request to keep the model loaded
                self.client.chat(
                    model="llama3.1",
                    messages=[{"role": "user", "content": "ping"}],
                    options={"num_predict": 1}  # Minimal generation
                )
                logging.info("Ollama keep-alive ping sent")
            except Exception as e:
                logging.error(f"Error in Ollama keep-alive thread: {e}")
            
            # Sleep for 5 minutes before the next ping
            time.sleep(300)
    
    def get_client(self):
        """Get the ollama client instance"""
        return self.client