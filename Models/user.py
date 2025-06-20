import sqlite3
from datetime import datetime
from db.database import get_connection
from auth.password import input_password, verify_password
from auth.passwordHash import hash_password

class User:
    def __init__(
        self, id: int, 
        userName: str, 
        passwordHash: str, 
        role: str
        ):
        self.id = id
        self.userName = userName
        self.passwordHash = passwordHash
        self.role = role

    def add_user(self):
        
        username = input("Enter username: ").strip()
        password = input_password("Enter password: ").strip()
        confirm_password = input_password("Confirm password: ").strip()

        if password != confirm_password:
            print("Passwords do not match.")
            return
        match self.role:
            case "super_administrator":
                print("=== Adding new user ===")
                print("\nRole of the new user:")
                print("1. service engineer")
                print("2. system administrator")
                role_choice = input("Enter number (1 or 2): ").strip()

                role_map = {
                    "1": "service_engineer",
                    "2": "system_administrator"
                }
                role = role_map.get(role_choice)

                if not role:
                    print("invalid role selected.")
                    return
            case "system_administrator":
                print("=== Adding new service engineer ===")
                role = "service_engineer"
            case "service_engineer":
                print("You are unauthorized to add a user")
                return
        
        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip()
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                # Check if username exists
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    print("Username already exists.")
                    return

                hashed_password = hash_password(password)

                # Insert into users table
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)
                ''', (username, hashed_password, role))

                # get userId
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                user_id_row = cursor.fetchone()
                if user_id_row is None:
                    print("User not found after insert — unexpected.")
                    return

                user_id = user_id_row[0]
                reg_date = datetime.now().strftime("%Y-%m-%d")

                # Insert into profiles table
                cursor.execute('''
                    INSERT INTO profiles (user_id, first_name, last_name, registration_date)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, first_name, last_name, reg_date))

                conn.commit()
                print(f"\nUser '{username}' added successfully with role '{role}'.\n")

        except sqlite3.Error as e:
            print("Database error:", e)
        

    def display_users(self):
        
        try:
            print("=== User display ===")
            start = input("Enter starting index (0 for beginning): ").strip()
            if not start.isdigit():
                print("Invalid input. Must be a non-negative number.")
                return

            offset = int(start)

            with get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT username, role FROM users LIMIT 100 OFFSET ?",
                    (offset,)
                )
                users = cursor.fetchall()

                if not users:
                    print("\nNo users found from this starting point.")
                    return

                print(f"\n=== Users List (From {offset} to {offset + len(users) - 1}) ===")
                for username, role in users:
                    print(f"Username: {username} | Role: {role}")

        except Exception as e:
            print("Error fetching users:", e)

    def manageServiceEngineers(self):
        
        while True:
            print("=== Manage Service Engineers ===")
            print("1. Add Service Engineer")
            print("2. Update Service Engineer")
            print("3. Delete Service Engineer")
            print("4 Change password of Service Engineer")
            print("5. Exit")

            choice = input("Select an option: ").strip()

            if choice == "1":
                self.addServiceEngineer()
            elif choice == "2":
                self.updateServiceEngineer()
            elif choice == "3":
                self.deleteServiceEngineer()
            elif choice == "4":
                self.changePasswordSE()
            elif choice == "5":
                print("Exiting...")
                break
            else:
                print("[ERROR] Invalid choice. Please try again.")
            

    def addServiceEngineer(self):
        username = input("Enter username: ").strip()
        password = input_password("Enter password: ").strip()

        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip()
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                # Check if username exists
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    print("Username already exists.")
                    return

                hashed_password = hash_password(password)

                # Insert into users table
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)
                ''', (username, hashed_password, "service_engineer"))
                
                # get userId
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                user_id_row = cursor.fetchone()
                if user_id_row is None:
                    print("User not found after insert — unexpected.")
                    return

                user_id = user_id_row[0]
                reg_date = datetime.now().strftime("%Y-%m-%d")

                # Insert into profiles table
                cursor.execute('''
                    INSERT INTO profiles (user_id, first_name, last_name, registration_date)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, first_name, last_name, reg_date))

                conn.commit()
                print(f"[SUCCES] user: {username} succesfully added")

        except sqlite3.Error as e:
            print("Database error:", e)


    def updateServiceEngineer(self):
        username = input("Enter username: ").strip()
        password = input_password("Enter password: ").strip()
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                # Check if username exists
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if not cursor.fetchone():
                    print("Username doesn't exist.")
                    return

                # test if passwords match
                hashed_password = hash_password(password)
                cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
                stored_password_row = cursor.fetchone()

                if not stored_password_row:
                    print("Could not retrieve password.")
                    return

                stored_hash = stored_password_row[0]

                if not verify_password(hashed_password, stored_hash):
                    print("Password or username incorrect.")
                    return

                # get userId
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                user_id_row = cursor.fetchone()
                if user_id_row is None:
                    print("User not found after insert — unexpected.")
                    return

                user_id = user_id_row[0]

                print("\n === Update Service Engineer ===")
                print("1. Update Username")
                print("2. Update First name")
                print("3. Update Last name")
                choice = input("Enter number (1-3): ").strip()

                # Update users table
                if choice == "1":
                    new_userName = input("Enter new username: ").strip()
                    cursor.execute(
                        "UPDATE users SET username = ? WHERE id = ?", (new_userName, user_id))
                    print(f"[SUCCES] User {new_userName} updated succesfully")

                # Update profiles table
                elif choice == "2":
                    new_firstName = input("Enter new first name: ").strip()
                    cursor.execute(
                        "UPDATE profiles SET first_name = ? WHERE user_id = ?", (new_firstName, user_id))
                    print(f"[SUCCES] User {username} updated succesfully")

                # Update profiles table
                elif choice == "3":
                    new_lastName = input("Enter new last name: ").strip()
                    cursor.execute(
                        "UPDATE profiles SET last_name = ? WHERE user_id = ?", (new_lastName, user_id))
                    print(f"[SUCCES] User {username} updated succesfully")

                else:
                    print("[ERROR] Invalid choice.")
                    return

                conn.commit()
                

        except sqlite3.Error as e:
            print("Database error:", e)

    def deleteServiceEngineer(self):
        username = input("Enter username: ").strip()
        password = input_password("Enter password: ").strip()
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                # Check if username exists
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if not cursor.fetchone():
                    print("Username doesn't exist.")
                    return

                hashed_password = hash_password(password)

                # test if passwords match
                hashed_password = hash_password(password)
                cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
                stored_password_row = cursor.fetchone()
                if not stored_password_row:
                    print("Could not retrieve password.")
                    return
                stored_hash = stored_password_row[0]
                if not verify_password(hashed_password, stored_hash):
                    print("Password or username incorrect.")
                    return

                # get userId
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                user_id_row = cursor.fetchone()
                if user_id_row is None:
                    print("User not found — unexpected.")
                    return

                user_id = user_id_row[0]

                # delete user from profiles
                cursor.execute("DELETE FROM profiles WHERE user_id = ?", (user_id,))
                if cursor.rowcount == 0:
                    print("User not found or already deleted.")

                # delete user from users
                cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                if cursor.rowcount == 0:
                    print("User not found or already deleted.")

                conn.commit()
                print(f"[SUCCES] User {username} deleted succesfully")
        except sqlite3.Error as e:
            print("Database error:", e)


    def changePasswordSE(self):
        print("=== Change Service Engineer Password ===")
        username = input("Enter username: ").strip()
        current_password = input_password("Enter current password: ").strip()

        try:
            with get_connection() as conn:
                cursor = conn.cursor()

                # Check if user exists
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                user_row = cursor.fetchone()
                if not user_row:
                    print("[ERROR] Username doesn't exist.")
                    return

                user_id = user_row[0]

                # Get stored hash and verify
                hashed_password = hash_password(current_password)
                cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
                stored_password_row = cursor.fetchone()
                if not stored_password_row:
                    print("Could not retrieve password.")
                    return
                stored_hash = stored_password_row[0]

                if not verify_password(hashed_password, stored_hash):
                    print("Password or username incorrect.")
                    return

                # Ask for new password and confirmation
                new_password = input_password("Enter new password: ").strip()
                confirm_password = input_password("Confirm new password: ").strip()

                if new_password != confirm_password:
                    print("[ERROR] Passwords do not match.")
                    return

                new_hash = hash_password(new_password)

                # Update password
                cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
                conn.commit()

                print(f"[SUCCES] Password of user {username} changed successfully.")

        except sqlite3.Error as e:
            print("Database error:", e)


        