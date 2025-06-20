# ui/main_menu.py

from auth.login import login


def start_app():
    user = login()
    if not user:
        return

    if user["role"] == "super_administrator":
        superAdmin()
        return
    elif user["role"] == "system_administrator":
        systemAdmin()
        return
    elif user["role"] == "service_engineer":
        serviceEngineer()
        return


def serviceEngineer():
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


def systemAdmin():
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


def superAdmin():
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
            manage_system_admins()
        elif choice == "2":
            manage_service_engineers()
        elif choice == "3":
            manage_travellers()
        elif choice == "4":
            manage_scooters()
        elif choice == "5":
            view_logs()
        elif choice == "6":
            backup_and_restore()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("[ERROR] Invalid choice.")


# Placeholder functions for each menu option
def manage_system_admins():
    print("[TODO] Manage System Administrators - Feature coming soon.")


def manage_service_engineers():
    print("[TODO] Manage Service Engineers - Feature coming soon.")


def manage_travellers():
    print("[TODO] Manage Travellers - Feature coming soon.")


def manage_scooters():
    print("[TODO] Manage Scooters - Feature coming soon.")


def view_logs():
    print("[TODO] View Logs - Feature coming soon.")


def backup_and_restore():
    print("[TODO] Backup & Restore - Feature coming soon.")
