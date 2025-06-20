import sys
from db.database import initialize_db
from ui.main_menu import start_app


def main():
    try:
        initialize_db()
        start_app()
    except Exception as e:
        print("[FATAL ERROR]", str(e))


if __name__ == "__main__":
    main()
