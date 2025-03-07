# main.py
from app import app
from services.ollama_manager import OllamaClient

if __name__ == "__main__":
    OllamaClient()
    app.run(debug=True)