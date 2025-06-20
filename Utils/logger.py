
import os
import time
import base64

# Ensure the data directory exists
os.makedirs('data', exist_ok=True)

# Path to the key file and log file
KEY_FILE = 'data/key.txt'
LOG_FILE = 'data/logs.txt'

# Function to generate or retrieve the encryption key
def get_key():
    if not os.path.exists(KEY_FILE):
        key = os.urandom(16)
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
    else:
        with open(KEY_FILE, 'rb') as f:
            key = f.read()
    return key

# XOR-based encryption/decryption function with base64 encoding
def xor_encrypt_decrypt(data, key):
    encrypted_data = bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])
    return base64.b64encode(encrypted_data).decode(), encrypted_data

# Function to write a log entry
def write_log(username, description, additional_info='', suspicious=False):
    key = get_key()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} {username} {description} {additional_info} {suspicious}\n"
    encrypted_log, _ = xor_encrypt_decrypt(log_entry.encode(), key)
    with open(LOG_FILE, 'a') as f:
        f.write(encrypted_log + '\n')

# Function to read and decrypt logs
def read_logs():
    key = get_key()
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, 'r') as f:
        encrypted_logs = f.readlines()
    decrypted_logs = []
    for encrypted_log in encrypted_logs:
        encrypted_log = encrypted_log.strip()
        encrypted_log_bytes = base64.b64decode(encrypted_log)
        _, decrypted_log = xor_encrypt_decrypt(encrypted_log_bytes, key)
        decrypted_logs.append(decrypted_log.decode())
    return decrypted_logs

# Function to flag suspicious activity
def flag_suspicious_activity(username, description, additional_info=''):
    write_log(username, description, additional_info, suspicious=True)
