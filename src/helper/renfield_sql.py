import pymysql
import os
from dotenv import load_dotenv
import base64
import hashlib

# Load environment variables
load_dotenv()
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

config = {
    "host": "localhost",
    "user": DATABASE_USERNAME,
    "password": DATABASE_PASSWORD,
    "database": "renfield",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
}

class Renfield_SQL:
    def __init__(self):
        if not ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY is missing from environment variables")

        # Ensure the key is 32 bytes (AES-256 requires 256-bit key)
        self.key = hashlib.sha256(ENCRYPTION_KEY.encode()).digest()

    def connect(self):
        """Connect to database

        Raises:
            RuntimeError: Fails to connect to database

        Returns:
            _type_: _description_
        """
        try:
            self.connection = pymysql.connect(**config)
            self.cursor = self.connection.cursor()
            return self.cursor
        except pymysql.MySQLError as err:
            raise RuntimeError(f"MySQL Connection Failed: {err}")

    def disconnect(self):
        """Disconnect from database"""
        try:
            if hasattr(self, "cursor") and self.cursor:
                self.cursor.close()
            if hasattr(self, "connection") and self.connection:
                self.connection.close()
        except pymysql.MySQLError as err:
            print(f"Error closing MySQL connection: {err}")

    def commit(self):
        """Commit change to the database"""
        try:
            if hasattr(self, "connection") and self.connection:
                self.connection.commit()
        except pymysql.MySQLError as err:
            print(f"Error committing transaction: {err}")