# auth/password.py

import os
import hashlib
import base64


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return base64.b64encode(salt + key).decode()


def verify_password(password: str, stored: str) -> bool:
    decoded = base64.b64decode(stored.encode())
    salt = decoded[:16]
    key = decoded[16:]
    new_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return new_key == key
