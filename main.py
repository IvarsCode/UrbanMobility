from Models.db import init_db

from Controllers.userController import UserController


def main():
    print("Welcome to Urban Mobility Backend System")
    init_db()
    
    controller = UserController()  
    controller.display_users()
    controller.add_user()

    user = None
    while not user:
        user = controller.login()

    # Proceed to the menu based on role
    if user["role"] == "ServiceEngineer":
        print("Loading Service Engineer Menu...")
        # service_engineer_menu(user)
    elif user["role"] == "SystemAdministrator":
        print("Loading System Administrator Menu...")
        # system_admin_menu(user)
    elif user["role"] == "SuperAdministrator":
        print("Loading Super Administrator Menu...")
        # super_admin_menu(user)


if __name__ == "__main__":
    main()
