from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import sqlalchemy
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseConnection:
    def connect_with_connector() -> sqlalchemy.engine.base.Engine:
        """
        Initializes a connection pool for a Cloud SQL instance of MySQL.

        Uses the Cloud SQL Python Connector package.
        """

        instance_connection_name = os.environ[
            "INSTANCE_CONNECTION_NAME"
        ]
        db_user = os.environ["DB_USER"]
        db_pass = os.environ["DB_PASSWORD"]
        db_name = os.environ["DB_NAME"]

        ip_type = IPTypes.PRIVATE if os.environ.get("USE_PRIVATE_IP") else IPTypes.PUBLIC

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
