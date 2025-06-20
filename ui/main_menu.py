# ui/main_menu.py

from auth.login import login


def start_app():
    user = login()
    if not user:
        return

    if user["role"] != "super_admin":
        print("[ERROR] Only Super Admin can access this version of the system.")
        return

    while True:
        print("\n=== Super Admin Dashboard ===")
        print("1. View System Info (Placeholder)")
        print("2. Exit")

        choice = input("Select an option: ").strip()
        if choice == "1":
            print("[INFO] System running. Feature coming soon.")
        elif choice == "2":
            print("Goodbye!")
            break
        else:
            print("[ERROR] Invalid choice.")
