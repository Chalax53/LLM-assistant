# main.py
from config.database import DatabaseConnection
from models.id_record import IDRecord
from app import app


if __name__ == "__main__":
    app.run(debug=True)