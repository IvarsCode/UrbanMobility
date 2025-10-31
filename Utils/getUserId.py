from db.database import get_connection
from Utils.logger import Logger
from Utils.encryption import Encryptor

encryptor = Encryptor()
logger = Logger()


def get_user_id_by_username(input_username: str):
    """
    Retrieve a user's ID by comparing decrypted usernames.
    Returns the user ID if found, or None otherwise.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username FROM users")
            rows = cursor.fetchall() # List of tuples (id, encrypted_username)

        for user_id, encrypted_username in rows:
            try:
                decrypted_username = encryptor.decrypt_text(encrypted_username.encode()) # uses Encryptor instance
            except Exception as e: # invalid token or other decryption error
                continue

            if decrypted_username.lower() == input_username.lower():
                return user_id

        return None

    except Exception as e: # database error
        print(f"[ERROR] Failed to get user id: {e}") # To avoid circular import, using print instead of logger
        return None
 