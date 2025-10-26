# auth/login.py

from db.database import get_connection
from auth.password import verify_password, input_password
from auth.passwordHash import hash_password
from Models.user import User
from Utils.logger import Logger
from ui.terminal import clear_terminal
from Utils.encryption import Encryptor

encryptor = Encryptor()
logger = Logger()


def login():
    clear_terminal()
    print("=== Urban Mobility Backend Login ===")
    username = input("Username: ").strip()
    password = input_password("Password: ").strip()
    hashed_pw = hash_password(password)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, password_hash, role FROM users WHERE id = ?",
        (get_user_id_by_username(username),),
    )
    try:
        user = cur.fetchone()
        conn.close()
    except:
        print("[ERROR] No user found.")

    if not user:
        print("[ERROR] Invalid Input.")
        logger.log("unknown", "Failed login attempt", "username not found")
        return None

    id, stored_username, stored_hash, role = user

    try:
        stored_username = encryptor.decrypt_text(stored_username.encode())
        role = encryptor.decrypt_text(role.encode())
    except Exception:
        # In case you’re migrating old unencrypted users
        pass

    if verify_password(hashed_pw, stored_hash):
        print(f"[SUCCESS] Welcome, {stored_username} ({role})")
        logger.log(username, f"Logged in as {role}", "")
        return User(id, stored_username, stored_hash, role)
    else:
        print("[ERROR] Invalid Input.")
        logger.log(username, "Failed login attempt", "Wrong password", True)
        return None


def logOut(user):
    clear_terminal()
    print("=== Urban Mobility Logout ===")
    username = input("Enter your username to logout: ").strip()

    with get_connection() as conn:
        cursor = conn.cursor()
        encrypted_username = encryptor.encrypt_text(username).decode()
        cursor.execute(
            "UPDATE users SET isLoggedIn = 0 WHERE username = ?", (encrypted_username,)
        )
        conn.commit()
        print(f"\nUser '{username}' logged out successfully.")
        logger.log(username, f"Logged out", "")


def get_user_id_by_username(input_username: str):
    """
    Retrieve a user's ID by comparing decrypted usernames.
    Returns the user ID if found, or None otherwise.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username FROM users")
            rows = cursor.fetchall()

        for user_id, encrypted_username in rows:
            try:
                decrypted_username = encryptor.decrypt_text(encrypted_username.encode())
            except Exception as e:
                continue

            if decrypted_username.lower() == input_username.lower():
                return user_id

        return None

    except Exception as e:
        print(f"[ERROR] Failed to get user id: {e}")
        return None
