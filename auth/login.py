# auth/login.py

from db.database import get_connection
from auth.password import verify_password


def login():
    print("=== Urban Mobility Backend Login ===")
    username = input("Username: ").strip().lower()
    password = input("Password: ").strip()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT username, password_hash, role FROM users WHERE LOWER(username) = ?",
        (username,),
    )
    user = cur.fetchone()
    conn.close()

    if not user:
        print("[ERROR] Invalid username.")
        return None

    stored_username, hashed_pw, role = user
    if verify_password(password, hashed_pw):
        print(f"[SUCCESS] Welcome, {stored_username} ({role})")
        return {"username": stored_username, "role": role}
    else:
        print("[ERROR] Incorrect password.")
        return None
