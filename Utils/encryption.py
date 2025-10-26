from cryptography.fernet import Fernet
import os


class Encryptor:
    def __init__(self, key_file: str = "encryption.key"):
        self.key_file = key_file
        self.key = self._load_or_create_key()
        self.fernet = Fernet(self.key)

    def _load_or_create_key(self) -> bytes:
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
        return key

    def encrypt_text(self, text: str) -> bytes:
        return self.fernet.encrypt(text.encode())

    def decrypt_text(self, encrypted_text: bytes) -> str:
        return self.fernet.decrypt(encrypted_text).decode()

    def encrypt_file(self, input_path: str, output_path: str):
        with open(input_path, "rb") as f:
            data = f.read()
        encrypted_data = self.fernet.encrypt(data)
        with open(output_path, "wb") as f:
            f.write(encrypted_data)
