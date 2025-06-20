import os
import hashlib
import base64


def hash_password(password: str) -> str:
    salt = bytes.fromhex("a7b3d91e4f8c6a12de35f90c56e4b789")
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return base64.b64encode(salt + key).decode()
