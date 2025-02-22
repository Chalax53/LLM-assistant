from flask import Flask
from flask_restful import Api
import os
from routes.id_routes import IDProcessing, GetAllRecords, EstadoDeCuentaProcessing, IDLocalProcessing, IDLocalProcessingV2
from config.database import DatabaseConnection

def create_app():
    app = Flask(__name__)
    api = Api(app)
    
    # Initialize DB connection
    db = DatabaseConnection()
    
    UPLOAD_FOLDER = 'uploads'
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    @app.teardown_appcontext
    def cleanup(exception=None):
        db.close()
        
    api.add_resource(
        IDProcessing, 
        '/api/process-id', 
        resource_class_kwargs={'upload_folder': UPLOAD_FOLDER}
    )
    
    api.add_resource(
        GetAllRecords, "/get-all-records"
    )

    api.add_resource(
        EstadoDeCuentaProcessing, 
        "/api/process-estado-cuenta",
        resource_class_kwargs={'upload_folder': UPLOAD_FOLDER}
    )

    api.add_resource(
        IDLocalProcessing, 
        "/api/process-locally"
    )

    api.add_resource(
        IDLocalProcessingV2,
        "/api/process-locally-v2"
    )

    return app

app = create_app()