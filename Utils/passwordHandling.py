import sys 
import hashlib

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

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()