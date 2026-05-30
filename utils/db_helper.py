import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

class DatabaseHelper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseHelper, cls).__new__(cls)
            try:
                cls._instance._connection = mysql.connector.connect(
                    host=os.getenv("DB_HOST", "localhost"),
                    port=int(os.getenv("DB_PORT", 3306)),
                    user=os.getenv("DB_USER", "root"),
                    password=os.getenv("DB_PASSWORD", ""),
                    database=os.getenv("DB_NAME", "booking_hotel"),
                    charset="utf8mb4",
                    collation="utf8mb4_general_ci"
                )
            except Exception:
                cls._instance._connection = None
        return cls._instance

    def get_connection(self):
        return self._connection
