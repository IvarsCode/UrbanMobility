# ui/main_menu.py

from auth.login import login
from Models.user import User


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
            pass
        elif choice == "2":
            print("Goodbye!")
            break
        else:
            print("[ERROR] Invalid choice.")


def systemAdmin(user: User):
    while True:
        print("\n=== System Admin Dashboard ===")
        print("1. Manage Service Engineers")
        print("2. Manage Travellers")
        print("3. Manage Scooters")
        print("4. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            pass
        elif choice == "2":
            pass
        elif choice == "3":
            pass
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("[ERROR] Invalid choice.")


def superAdmin(user: User):
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
            pass
        elif choice == "2":
            user.add_user()
        elif choice == "3":
            pass
        elif choice == "4":
            pass
        elif choice == "5":
            pass
        elif choice == "6":
            pass
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("[ERROR] Invalid choice.")
