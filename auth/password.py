import re
import sys
from db.database import get_connection
from auth.passwordHash import hash_password


def verify_password(password: str, stored: str) -> bool:
    return password == stored


def input_password(prompt="Password: "):
    """Securely input and validate a password according to the defined rules."""

    def is_valid_password(pw: str) -> tuple[bool, str]:
        if len(pw) < 12:
            return False, " === Password must be at least 12 characters long. ==="
        if len(pw) > 30:
            return False, " === Password must be no longer than 30 characters. ==="
        if not re.search(r"[a-z]", pw):
            return (
                False,
                " === Password must contain at least one lowercase letter. ===",
            )
        if not re.search(r"[A-Z]", pw):
            return (
                False,
                " === Password must contain at least one uppercase letter. ===",
            )
        if not re.search(r"\d", pw):
            return False, " === Password must contain at least one digit. ==="
        if not re.search(r"[~!@#$%&_\-\+=`|()\[\]{}:;\"'<>,.?/]", pw):
            return (
                False,
                " === Password must contain at least one special character. ===",
            )
        if not re.fullmatch(
            r"[A-Za-z0-9~!@#$%&_\-\+=`|()\[\]{}:;\"'<>,.?/]{12,30}", pw
        ):
            return False, " === Password contains invalid characters. ==="
        return True, ""

    while True:
        print(prompt, end="", flush=True)
        password = ""

        # Cross-platform hidden input
        if sys.platform.startswith("win"):
            import msvcrt

            while True:
                ch = msvcrt.getch()
                if ch in {b"\r", b"\n"}:
                    print()
                    break
                elif ch == b"\x08":  # Backspace
                    if len(password) > 0:
                        password = password[:-1]
                        print("\b \b", end="", flush=True)
                elif ch == b"\x03":  # Ctrl+C
                    raise KeyboardInterrupt
                else:
                    password += ch.decode("utf-8", errors="ignore")
                    print("*", end="", flush=True)
        else:
            import tty
            import termios

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                while True:
                    ch = sys.stdin.read(1)
                    if ch in {"\r", "\n"}:
                        print()
                        break
                    elif ch == "\x7f":  # Backspace
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

        valid, msg = is_valid_password(password)
        if valid:
            return password
        else:
            print(msg)
            print(" === Please try again. ===\n")


def input_username(prompt="Username: "):
    """Input and validate a username according to the defined rules."""
    while True:
        username = input(prompt).strip()

        if len(username) < 8:
            print(" === Username must be at least 8 characters long. ===")
        elif len(username) > 10:
            print(" === Username must be no longer than 10 characters. ===")
        elif not re.match(r"^[A-Za-z_]", username):
            print(" === Username must start with a letter or underscore (_). ===")
        elif not re.fullmatch(r"[A-Za-z0-9_'.]{8,10}", username):
            print(
                " === Username can only contain letters, numbers, underscores (_), apostrophes ('), and periods (.). ==="
            )
        else:
            return username.lower()

        print(" === Please try again. ===\n")


# def input_password(prompt="Password: "):
#     print(prompt, end="", flush=True)
#     password = ""

#     if sys.platform.startswith("win"):
#         import msvcrt

#         while True:
#             ch = msvcrt.getch()
#             if ch in {b"\r", b"\n"}:
#                 print()
#                 break
#             elif ch == b"\x08":  # backspace
#                 if len(password) > 0:
#                     password = password[:-1]
#                     print("\b \b", end="", flush=True)
#             elif ch == b"\x03":  # Ctrl+C
#                 raise KeyboardInterrupt
#             else:
#                 password += ch.decode("utf-8")
#                 print("*", end="", flush=True)
#     else:
#         import tty
#         import termios

#         fd = sys.stdin.fileno()
#         old_settings = termios.tcgetattr(fd)

#         try:
#             tty.setraw(sys.stdin.fileno())
#             while True:
#                 ch = sys.stdin.read(1)
#                 if ch in {"\r", "\n"}:
#                     print()
#                     break
#                 elif ch == "\x7f":  # backspace
#                     if len(password) > 0:
#                         password = password[:-1]
#                         print("\b \b", end="", flush=True)
#                 elif ch == "\x03":  # Ctrl+C
#                     raise KeyboardInterrupt
#                 else:
#                     password += ch
#                     print("*", end="", flush=True)
#         finally:
#             termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

#     return password


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
