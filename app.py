from flask import Flask
from flask_restful import Api
import os
from routes.id_routes import GetAllRecords, ParseIDPhoto, ParseEdoCtaPDF
from routes.ai_routes import ChatWithLlama, InitialGreeting, UploadFile
from config.database import DatabaseConnection

def create_app():
    app = Flask(__name__)
    api = Api(app)
    
    # Initialize DB connection
    db = DatabaseConnection()
    
    @app.teardown_appcontext
    def cleanup(exception=None):
        db.close()

    api.add_resource(ChatWithLlama, "/chat")
    api.add_resource( InitialGreeting, "/ai-greet")
    api.add_resource(UploadFile, "/upload-file")

    return app

app = create_app()