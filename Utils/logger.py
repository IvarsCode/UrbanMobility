# utils/logger.py
import os
from datetime import datetime

LOG_FILE = "data/logs.enc"
KEY = "UrbanMobilitySecret"  # Symmetric key (should be kept private)


class Logger:
    def __init__(self, key: str = KEY):
        self.key = key

    def xor_encrypt(self, text: str) -> bytes:
        return bytes(
            [ord(c) ^ ord(self.key[i % len(self.key)]) for i, c in enumerate(text)]
        )

    def xor_decrypt(self, data: bytes) -> str:
        return "".join(
            [chr(b ^ ord(self.key[i % len(self.key)])) for i, b in enumerate(data)]
        )

    def log(self, username, description, extra="", suspicious=False):
        now = datetime.now()
        entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')}|{username}|{description}|{extra}|{'Yes' if suspicious else 'No'}|Unread\n"
        encrypted = self.xor_encrypt(entry)

        with open(LOG_FILE, "ab") as f:
            f.write(encrypted + b"\n")

    def read_logs(self, only_suspicious=False):
        if not os.path.exists(LOG_FILE):
            return []

        logs = []
        with open(LOG_FILE, "rb") as f:
            for line in f:
                line = line.strip()
                try:
                    decrypted = self.xor_decrypt(line)
                    parts = decrypted.split("|")
                    if only_suspicious and parts[4] != "Yes":
                        continue
                    logs.append(parts)
                except Exception:
                    continue
        return logs

    def mark_suspicious_as_read(self):
        if not os.path.exists(LOG_FILE):
            return

        updated_lines = []
        with open(LOG_FILE, "rb") as f:
            for line in f:
                try:
                    decrypted = self.xor_decrypt(line.strip())
                    if "Yes|Unread" in decrypted:
                        decrypted = decrypted.replace("Yes|Unread", "Yes|Read")
                    encrypted = self.xor_encrypt(decrypted)
                    updated_lines.append(encrypted)
                except Exception:
                    updated_lines.append(line.strip())

        with open(LOG_FILE, "wb") as f:
            for line in updated_lines:
                f.write(line + b"\n")
