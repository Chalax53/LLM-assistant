from flask import Flask
from flask_restful import Api
from routes.ai_routes import InitialGreetingV2, UploadFileStream, ChatWithLlamaStream
from config.database import DatabaseConnection
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    api = Api(app)
    
    # Initialize DB connection
    db = DatabaseConnection()

    api.add_resource(InitialGreetingV2, "/initial-greeting")
    api.add_resource(UploadFileStream, "/upload-file-stream")
    api.add_resource(ChatWithLlamaStream, "/chat-stream")

    return app

app = create_app()