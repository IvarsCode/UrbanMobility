from db import get_connection
#from input_password import input_password

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

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()

        if result:
            role = result[0]
            print(f"\n✅ Login successful! Logged in as {role} ({username})")
            return {"username": username, "role": role}
        else:
            print("\n❌ Login failed. Invalid username or password.")
            return None