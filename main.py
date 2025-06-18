from login import login
from db import init_db

def main():
    print("Welcome to Urban Mobility Backend System")
    init_db()
    
    user = None
    while not user:
        user = login()

    # Proceed to the menu based on role
    if user["role"] == "service_engineer":
        print("Loading Service Engineer Menu...")
        # service_engineer_menu(user)
    elif user["role"] == "system_admin":
        print("Loading System Administrator Menu...")
        # system_admin_menu(user)
    elif user["role"] == "super_admin":
        print("Loading Super Administrator Menu...")
        # super_admin_menu(user)

if __name__ == "__main__":
    main()