# auth/login.py

from db.database import get_connection
from auth.password import verify_password
from auth.passwordHash import hash_password
from Models.user import User
from Utils.logger import Logger
from ui.terminal import clear_terminal
from Utils.encryption import Encryptor
from Utils.getUserId import get_user_id_by_username
from auth.password import input_password_login

encryptor = Encryptor()
logger = Logger()


def login():
    clear_terminal()
    print("=== Urban Mobility Backend Login ===")
    username = input("Username: ").strip()
    password = input_password_login("Password: ").strip()
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

    if user:
        id, stored_username, stored_hash, role = user

        try:
            stored_username = encryptor.decrypt_text(stored_username.encode())
            role = encryptor.decrypt_text(role.encode())
        except Exception:
            pass

        if verify_password(hashed_pw, stored_hash):
            print(f"[SUCCESS] Welcome, {stored_username} ({role})")
            logger.log(username, f"Logged in as {role}", "")
            return User(id, stored_username, stored_hash, role)
        else:
            print("[ERROR] Invalid Input.")
            logger.log(username, "Failed login attempt", "Wrong password", True)
            return None
    else:
        print("[ERROR] Invalid Input.")
        logger.log("unknown", "Failed login attempt", "username not found")
        return None


# def logOut(user):
#     clear_terminal()
#     print("=== Urban Mobility Logout ===")
#     conn = get_connection()
#     cur = conn.cursor()

#     cur.execute("UPDATE users SET isLoggedIn = 0 WHERE id = ?", (user.id,))

#     conn.commit()
#     print(f"\nUser '{user.userName}' logged out successfully.")
#     logger.log(user.userName, f"Logged out", "")
