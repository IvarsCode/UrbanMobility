import sys
from db.database import initialize_db
from ui.main_menu import start_app
from Utils.DummyDataScooter import insert_dummy_scooters


def main():
    try:
        # initialize_db()
        # insert_dummy_scooters(100)
        start_app()
    except Exception as e:
        print("[FATAL ERROR]", str(e))


if __name__ == "__main__":
    main()
