import pymysql
import os
from dotenv import load_dotenv
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
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


## To Be Removed/Editted
    def encrypt(self, data):
        data = str(data).encode()
        cipher = AES.new(self.key, AES.MODE_GCM)  # AES-GCM Mode
        ciphertext, tag = cipher.encrypt_and_digest(data)  # Encrypt and get tag
        encrypted_data = base64.b64encode(cipher.nonce + tag + ciphertext).decode()
        return encrypted_data

    def decrypt(self, encrypted_data):
        encrypted_data = base64.b64decode(encrypted_data)
        nonce = encrypted_data[:16]  # First 16 bytes = Nonce
        tag = encrypted_data[16:32]  # Next 16 bytes = Tag
        ciphertext = encrypted_data[32:]  # Rest is Ciphertext

        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted_data.decode()
