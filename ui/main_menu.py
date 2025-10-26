# ui/main_menu.py

from auth.login import login
from Models.user import User
from Models.scooter import Scooter, manage_scooter
from Models.traveler import manage_traveller
from Utils.logger import Logger
from ui.terminal import clear_terminal
from Utils.BackupService import backup_menu, system_admin_backup_menu

logger = Logger()


def start_app():
    user = login()
    if not user:
        return

    if user.role == "super_administrator":
        superAdmin(user)
        return
    elif user.role == "system_administrator":
        systemAdmin(user)
        return
    elif user.role == "service_engineer":
        serviceEngineer(user)
        return


def serviceEngineer(user: User):
    while True:
        print("\n=== Service Engineer Dashboard ===")
        print("1. Update Scooter")
        print("2. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            clear_terminal()
            Scooter.update_scooter()
            return
        elif choice == "2":
            clear_terminal()
            print("Goodbye!")
            break
        else:
            print("[ERROR] Invalid choice.")


def systemAdmin(user: User):
    if logger.check_suspicious() > 0:
        print(
            "[ALERT] There are suspicious log entries. Please review the logs in the menu."
        )
    while True:
        print("\n=== System Admin Dashboard ===")
        print("1. View Users")
        print("2. Manage Service Engineers")
        print("3. Manage Travellers")
        print("4. Manage Scooters")
        print("5. Restore Backup")
        print("6. Read Logs")
        print("7. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            clear_terminal()
            user.display_users()

        elif choice == "2":
            clear_terminal()
            user.manageServiceEngineers()

        elif choice == "3":
            clear_terminal()
            manage_traveller()

        elif choice == "4":
            clear_terminal()
            manage_scooter()

        elif choice == "5":
            clear_terminal()
            system_admin_backup_menu(user.username)

        elif choice == "6":
            clear_terminal()
            logs = logger.read_logs()
            if not logs:
                print("No logs found.")
            else:
                for log in logs:
                    timestamp, username, description, extra, suspicious, status = log
                    print(
                        f"[{timestamp}] {username} | {description} | {extra} | Suspicious: {suspicious} | {status}"
                    )
            logger.mark_as_read()

        elif choice == "7":
            clear_terminal()
            print("Goodbye!")
            break

        else:
            clear_terminal()
            print("[ERROR] Invalid choice.")


def superAdmin(user: User):
    if logger.check_suspicious() > 0:
        print(
            "[ALERT] There are suspicious log entries. Please review the logs in the menu."
        )
    while True:
        print("\n=== Super Admin Dashboard ===")
        print("1. Manage System Administrators")
        print("2. Manage Service Engineers")
        print("3. Manage Travellers")
        print("4. Manage Scooters")
        print("5. View Logs")
        print("6. Backup & Restore")
        print("7. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            clear_terminal()
            user.ManageSystemAdministrators()
        elif choice == "2":
            clear_terminal()
            user.manageServiceEngineers()
        elif choice == "3":
            clear_terminal()
            manage_traveller()
        elif choice == "4":
            clear_terminal()
            manage_scooter()
        elif choice == "5":
            clear_terminal()
            logs = logger.read_logs()
            if not logs:
                print("No logs found.")
            else:
                for log in logs:
                    timestamp, username, description, extra, suspicious, status = log
                    print(
                        f"[{timestamp}] {username} | {description} | {extra} | Suspicious: {suspicious} | {status}"
                    )
            logger.mark_as_read()
        elif choice == "6":
            clear_terminal()
            backup_menu()
            pass
        elif choice == "7":
            clear_terminal()
            print("Goodbye!")
            break
        else:
            clear_terminal()
            print("[ERROR] Invalid choice.")
