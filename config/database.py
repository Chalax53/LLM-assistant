from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import sqlalchemy
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseConnection:
    # _instance = None

    # def __new__(cls):
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #     return cls._instance

    # def __init__(self):
    #     self.connection = None
    #     self.connect()

    # def connect(self):
    #     try:
    #         self.connection = mysql.connector.connect(
    #             host=os.getenv('DB_HOST'),
    #             user=os.getenv('DB_USER'),
    #             password=os.getenv('DB_PASSWORD'),
    #             database=os.getenv('DB_NAME'),
    #             unix_socket_path = os.environ[
    #                 "/cloud-sql/eco-world-451921-h9:northamerica-south1:bajio-db"
    #             ]
    #         )
    #         print("Connected to MySQL")
    #     except Error as e:
    #         print(f"Error: {e}")

    # def get_connection(self):
    #     if not self.connection or not self.connection.is_connected():
    #         self.connect()
    #     return self.connection

    # def close(self):
    #     if self.connection and self.connection.is_connected():
    #         self.connection.close()


    def connect_with_connector() -> sqlalchemy.engine.base.Engine:
        """
        Initializes a connection pool for a Cloud SQL instance of MySQL.

        Uses the Cloud SQL Python Connector package.
        """
        # Note: Saving credentials in environment variables is convenient, but not
        # secure - consider a more secure solution such as
        # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
        # keep secrets safe.

        instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")
            
        db_user = os.getenv("DB_USER")  # e.g. 'my-db-user'
        db_pass = os.getenv("DB_PASSWORD")  # e.g. 'my-db-password'
        db_name = os.getenv("DB_NAME")  # e.g. 'my-database'

        ip_type = IPTypes.PRIVATE if os.getenv("USE_PRIVATE_IP") else IPTypes.PUBLIC

        # initialize Cloud SQL Python Connector object
        connector = Connector(ip_type=ip_type, refresh_strategy="LAZY")

        def getconn() -> pymysql.connections.Connection:
            conn: pymysql.connections.Connection = connector.connect(
                instance_connection_name,
                "pymysql",
                user=db_user,
                password=db_pass,
                db=db_name,
            )
            return conn

        pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800
        )
        return pool
