from flask import Flask
from flask_restful import Api
import os
from routes.id_routes import GetAllRecords, ParseIDPhoto, ParseEdoCtaPDF
from config.database import DatabaseConnection

def create_app():
    app = Flask(__name__)
    api = Api(app)
    
    # Initialize DB connection
    db = DatabaseConnection()
    
    @app.teardown_appcontext
    def cleanup(exception=None):
        db.close()
        
    
    api.add_resource(
        GetAllRecords, "/get-all-records"
    )

    api.add_resource(
        ParseIDPhoto,
        "/process-id"
    )

    api.add_resource(
        ParseEdoCtaPDF,
        "/process-edocta"
    )

    return app

app = create_app()