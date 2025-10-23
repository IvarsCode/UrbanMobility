import base64
from cryptography.fernet import Fernet

RAW_KEY = (
    "UrbanMobilitySecret"  # ⚠️ Should be kept private and not hardcoded in production
)
FERNET_KEY = base64.urlsafe_b64encode(RAW_KEY.encode().ljust(32, b"_")[:32])


class EncryptionHandler:
    def __init__(self, key: bytes = FERNET_KEY):
        self.fernet = Fernet(key)

    def encrypt(self, text: str) -> bytes:
        """Encrypt text using Fernet AES encryption."""
        return self.fernet.encrypt(text.encode("utf-8"))

    def decrypt(self, data: bytes) -> str:
        """Decrypt Fernet-encrypted bytes to string."""
        return self.fernet.decrypt(data).decode("utf-8")
