# main.py
from config.database import DatabaseConnection
from models.id_record import IDRecord
from app import app

# TESTING DATABASE
# def test_connection():
#     db = DatabaseConnection()
#     connection = db.get_connection()
    
#     if connection and connection.is_connected():
#         print("Database connection test successful")
#         # Example query
#         cursor = connection.cursor()
#         cursor.execute("SELECT 1")
#         version = cursor.fetchone()
#         print(f"MySQL version: {version[0]}")
    
#     #db.close()

# if __name__ == "__main__":
#     test_connection()


# # Create record
# record = IDRecord(
#     full_name="John Doe",
#     address="123 Main St",
#     id_image_path="/path/to/image.jpg"
# )
# record_id = record.save()

# # Retrieve record
# stored_record = IDRecord.get_by_id(record_id)



if __name__ == "__main__":
    app.run(debug=True)