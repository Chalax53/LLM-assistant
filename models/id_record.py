from config.database import DatabaseConnection
from mysql.connector import Error


class IDRecord:
    def __init__(self, full_name=None, address=None):
        self.full_name = full_name
        self.address = address
        self.db = DatabaseConnection()

    def save(self):
        try:
            connection = DatabaseConnection.connect_with_connector()
            cursor = connection.cursor()
            
            query = """
                INSERT INTO id_records (full_name, address)
                VALUES (%s, %s)
            """
            values = (self.full_name, self.address)
            
            cursor.execute(query, values)
            connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error saving record in id_record: {e}")
            return None

    def get_last_entry(self):
        try:
            connection = DatabaseConnection.connect_with_connector()
            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT * FROM id_records
                ORDER BY record_id DESC
                LIMIT 1
            """
            
            cursor.execute(query)
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error retrieving last entry: {e}")
            return None


    # @staticmethod
    # def get_by_id(record_id):
    #     try:
    #         db = DatabaseConnection()
    #         cursor = db.connect_with_connector().cursor(dictionary=True)
            
    #         query = "SELECT * FROM id_records WHERE record_id = %s"
    #         cursor.execute(query, (record_id,))
            
    #         return cursor.fetchone()
    #     except Error as e:
    #         print(f"Error retrieving record: {e}")
    #         return None

    # @staticmethod
    # def get_all():
    #     try:
    #         db = DatabaseConnection()
    #         cursor = db.get_connection().cursor(dictionary=True)
            
    #         cursor.execute("SELECT * FROM id_records")
    #         return cursor.fetchall()
    #     except Error as e:
    #         print(f"Error retrieving records: {e}")
    #         return []