import sqlite3
import hashlib
from datetime import datetime
from db import get_connection


import sys

def input_password(prompt="Password: "):
    print(prompt, end="", flush=True)
    password = ""

    if sys.platform.startswith("win"):
        import msvcrt
        while True:
            ch = msvcrt.getch()
            if ch in {b"\r", b"\n"}:
                print()
                break
            elif ch == b"\x08":  # backspace
                if len(password) > 0:
                    password = password[:-1]
                    print("\b \b", end="", flush=True)
            elif ch == b"\x03":  # Ctrl+C
                raise KeyboardInterrupt
            else:
                password += ch.decode("utf-8")
                print("*", end="", flush=True)
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(sys.stdin.fileno())
            while True:
                ch = sys.stdin.read(1)
                if ch in {"\r", "\n"}:
                    print()
                    break
                elif ch == "\x7f":  # backspace
                    if len(password) > 0:
                        password = password[:-1]
                        print("\b \b", end="", flush=True)
                elif ch == "\x03":  # Ctrl+C
                    raise KeyboardInterrupt
                else:
                    password += ch
                    print("*", end="", flush=True)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return password


def login():
    print("=== Urban Mobility Login ===")
    username = input("Username: ")
    password = input_password("Password: ")

    hashedPassword = hash_password(password)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, hashedPassword))
        result = cursor.fetchone()

        if result:
            role = result[0]
            print(f"\n✅ Login successful! Logged in as {role} ({username})")
            return {"username": username, "role": role}
        else:
            print("\n❌ Login failed. Invalid username or password.")
            return None


DB_FILE = "urban_mobility.db"


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()



def add_user():
    try:
        username = input("Enter username: ").strip()
        password = input_password("Enter password: ").strip()
        confirm_password = input_password("Confirm password: ").strip()

        if password != confirm_password:
            print("❌ Passwords do not match.")
            return

        print("\nSelect role:")
        print("1. ServiceEngineer")
        print("2. SystemAdministrator")
        print("3. SuperAdministrator")
        role_choice = input("Enter number (1-3): ").strip()

        role_map = {
            "1": "ServiceEngineer",
            "2": "SystemAdministrator",
            "3": "SuperAdministrator"
        }
        role = role_map.get(role_choice)

        if not role:
            print("❌ Invalid role selected.")
            return

        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip()

        with get_connection() as conn:
            cursor = conn.cursor()

            # Check if username exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                print("❌ Username already exists.")
                return

            hashed_password = hash_password(password)

            # Insert into users table
            cursor.execute('''
                INSERT INTO users (username, password, role) VALUES (?, ?, ?)
            ''', (username, hashed_password, role))

            user_id = cursor.lastrowid
            reg_date = datetime.now().strftime("%Y-%m-%d")

            # Insert into profiles table
            cursor.execute('''
                INSERT INTO profiles (user_id, first_name, last_name, registration_date)
                VALUES (?, ?, ?, ?)
            ''', (user_id, first_name, last_name, reg_date))

            conn.commit()
            print(f"\n✅ User '{username}' added successfully with role '{role}'.\n")

    except sqlite3.Error as e:
        print("❌ Database error:", e)
    except KeyboardInterrupt:
        print("\n❗ Operation cancelled by user.")