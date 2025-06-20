from Models.db import init_db
from Utils import *
from Controllers.userController import UserController
#insert_dummy_scooters(50)  #run to run

def main():
    print("Welcome to Urban Mobility Backend System")
    init_db()
     
    
    controller = UserController()  
    
    #controller.display_users()
    #controller.add_user()

    user = None
    while not user:
        user = controller.login()
        controller.show_menu(user)

    


if __name__ == "__main__":
    main()
