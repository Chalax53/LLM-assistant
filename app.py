from flask import Flask
from flask_restful import Api
import os
from routes.id_routes import GetAllRecords, ParseIDPhoto, ParseEdoCtaPDF
from routes.ai_routes import ChatWithLlama, InitialGreeting, UploadFile, InitialGreetingV2
from config.database import DatabaseConnection
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)  # Allow all domains
    api = Api(app)
    
    # Initialize DB connection
    db = DatabaseConnection()
    
    @app.teardown_appcontext
    def cleanup(exception=None):
        db.close()

    api.add_resource(ChatWithLlama, "/chat")
    api.add_resource(InitialGreeting, "/ai-greet")
    api.add_resource(InitialGreetingV2, "/initial-greeting")
    api.add_resource(UploadFile, "/upload-file")

    return app

app = create_app()