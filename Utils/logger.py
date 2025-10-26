import os
from datetime import datetime
from Utils.encryption import Encryptor

LOG_FILE = "data/logs.enc"


class Logger:
    def __init__(self, encryptor: Encryptor = None):
        self.encryptor = encryptor or Encryptor()
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    def log(self, username, description, extra="", suspicious=False):
        now = datetime.now()
        entry = (
            f"{now.strftime('%Y-%m-%d %H:%M:%S')}|"
            f"{username}|{description}|{extra}|"
            f"{'Yes' if suspicious else 'No'}|Unread"
        )

        encrypted = self.encryptor.encrypt_text(entry)
        with open(LOG_FILE, "ab") as f:
            f.write(encrypted + b"\n")

    def read_logs(self, only_suspicious=False):
        if not os.path.exists(LOG_FILE):
            return []

        logs = []
        with open(LOG_FILE, "rb") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    decrypted = self.encryptor.decrypt_text(line)
                    parts = decrypted.split("|")
                    if len(parts) < 6:
                        continue
                    if only_suspicious and parts[4] != "Yes":
                        continue
                    logs.append(parts)
                except Exception:
                    continue
        return logs

    def mark_as_read(self):
        if not os.path.exists(LOG_FILE):
            return

        updated_lines = []
        with open(LOG_FILE, "rb") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    decrypted = self.encryptor.decrypt_text(line)
                    if "Unread" in decrypted:
                        decrypted = decrypted.replace("Unread", "Read")
                    encrypted = self.encryptor.encrypt_text(decrypted)
                    updated_lines.append(encrypted)
                except Exception:
                    updated_lines.append(line)

        with open(LOG_FILE, "wb") as f:
            for line in updated_lines:
                f.write(line + b"\n")

    def check_suspicious(self):
        if not os.path.exists(LOG_FILE):
            return

        sus_logs = 0
        with open(LOG_FILE, "rb") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    decrypted = self.encryptor.decrypt_text(line)
                    if "Yes|Unread" in decrypted:
                        sus_logs += 1
                except Exception:
                    sus_logs += 0

        return sus_logs
