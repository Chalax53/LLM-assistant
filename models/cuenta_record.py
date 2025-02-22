from config.database import DatabaseConnection
from mysql.connector import Error

class CuentaRecord:
    def __init__(self, full_name=None, address=None, fecha_corte=None):
        self.full_name = full_name
        self.address = address
        self.fecha_corte = fecha_corte
        self.db = DatabaseConnection()

    def save(self):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            
            query = """
                INSERT INTO estado_cuenta (full_name, address, fecha_corte)
                VALUES (%s, %s, %s)
            """
            values = (self.full_name, self.address, self.fecha_corte)
            
            cursor.execute(query, values)
            connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error saving record: {e}")
            return None

    @staticmethod
    def get_by_id(record_id):
        try:
            db = DatabaseConnection()
            cursor = db.get_connection().cursor(dictionary=True)
            
            query = "SELECT * FROM id_records WHERE record_id = %s"
            cursor.execute(query, (record_id,))
            
            return cursor.fetchone()
        except Error as e:
            print(f"Error retrieving record: {e}")
            return None

    @staticmethod
    def get_all():
        try:
            db = DatabaseConnection()
            cursor = db.get_connection().cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM id_records")
            return cursor.fetchall()
        except Error as e:
            print(f"Error retrieving records: {e}")
            return []