# auth/password.py

import os
import hashlib
import base64
import sys
from db.database import get_connection
from auth.passwordHash import hash_password


def verify_password(password: str, stored: str) -> bool:
    return password == stored


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


def update_password():
    print("=== Update Password ===")
    username = input("Enter your username: ").strip()
    old_password = input_password("Enter your old password: ").strip()
    new_password = input_password("Enter your new password: ").strip()
    confirm_new_password = input_password("Confirm your new password: ").strip()

    if new_password != confirm_new_password:
        print("New passwords do not match.")
        return

    hashed_old_password = hash_password(old_password)
    hashed_new_password = hash_password(new_password)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username, hashed_old_password),
        )
        user_id = cursor.fetchone()

        if user_id:
            cursor.execute(
                "UPDATE users SET password=? WHERE id=?",
                (hashed_new_password, user_id[0]),
            )
            conn.commit()
            print("Password updated successfully.")
        else:
            print("Invalid username or old password.")
