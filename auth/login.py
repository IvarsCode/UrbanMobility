# auth/login.py

from db.database import get_connection
from auth.password import verify_password, input_password
from auth.passwordHash import hash_password
from Models.user import User
from Utils.logger import Logger
from ui.terminal import clear_terminal

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
        "SELECT id, username, password_hash, role FROM users WHERE LOWER(username) = ?",
        (username,),
    )
    try:
        user = cur.fetchone()
        conn.close()
    except:
        print("[ERROR] No user found.")

    if not user:
        print("[ERROR] Invalid username.")
        logger.log("unknown", "Failed login attempt", "username not found")
        return None

    id, stored_username, stored_hash, role = user
    if verify_password(hashed_pw, stored_hash):
        print(f"[SUCCESS] Welcome, {stored_username} ({role})")
        logger.log(username, f"Logged in as {role}", "")
        return User(id, stored_username, stored_hash, role)
    else:
        print("[ERROR] Incorrect password.")
        logger.log(username, "Failed login attempt", "Wrong password", True)
        return None


def logOut(user):
    clear_terminal()
    print("=== Urban Mobility Logout ===")
    username = input("Enter your username to logout: ").strip()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET isLoggedIn = 0 WHERE username = ?", (user))
        conn.commit()
        print(f"\nUser '{username}' logged out successfully.")
        logger.log(username, f"Logged out", "")
