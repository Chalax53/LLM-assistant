from config.database import DatabaseConnection
from mysql.connector import Error
import sqlalchemy

class IDRecord:
    def __init__(self, full_name=None, address=None):
        self.full_name = full_name
        self.address = address
        self.db = DatabaseConnection()

    def save(self):
        try:
            engine = DatabaseConnection.connect_with_connector()
            with engine.connect() as connection:
                result = connection.execute(
                    sqlalchemy.text(
                        "INSERT INTO id_records (full_name, address) VALUES (:full_name, :address)"
                    ),
                    {"full_name": self.full_name, "address": self.address}
                )
                connection.commit()
                return result.lastrowid
        except Exception as e:
            print(f"Error saving record in id_record: {e}")
            return None

    def get_last_entry(self):
        try:
            engine = DatabaseConnection.connect_with_connector()
            with engine.connect() as connection:
                result = connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT * FROM id_records
                        ORDER BY record_id DESC
                        LIMIT 1
                        """
                    )
                )
                # Fetch the first row as a dictionary
                row = result.fetchone()
                if row:
                    # Convert row object to dictionary
                    return {key: value for key, value in zip(result.keys(), row)}
                return None
        except Exception as e:
            print(f"Error retrieving last entry: {e}")
            return None