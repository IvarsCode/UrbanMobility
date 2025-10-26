import sqlite3
from datetime import datetime
from db.database import get_connection
from auth.password import input_password, verify_password
from auth.passwordHash import hash_password
from ui.terminal import clear_terminal
from Utils.encryption import Encryptor
from Utils.getUserId import get_user_id_by_username

encryptor = Encryptor()


class User:
    def __init__(self, id: int, userName: str, passwordHash: str, role: str):
        self.id = id
        self.userName = userName
        self.passwordHash = passwordHash
        self.role = role

    def ManageSystemAdministrators(self):

        while True:
            print("=== Manage System Administrators ===")
            print("1. Add System Administrator")
            print("2. Update System Administrator")
            print("3. Delete System Administrator")
            print("4 Change password of System Administrator")
            print("5. Exit")

            choice = input("Select an option: ").strip()

            if choice == "1":
                self.add_system_administrator()
            elif choice == "2":
                self.update_user()
            elif choice == "3":
                self.delete_system_administrator()
            elif choice == "4":
                self.change_password()
            elif choice == "5":
                print("Exiting...")
                break
            else:
                clear_terminal()
                print("[ERROR] Invalid choice. Please try again.")

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
                self.add_service_engineer()
            elif choice == "2":
                self.update_service_engineer()
            elif choice == "3":
                self.delete_service_engineer()
            elif choice == "4":
                self.change_password()
            elif choice == "5":
                print("Exiting...")
                break
            else:
                clear_terminal()
                print("[ERROR] Invalid choice. Please try again.")

    def add_system_administrator(self):

        if self.role != "super_administrator":
            print("You are unauthorized to add a user")
            return

        print("=== Adding new system administrator ===")
        username = input("Enter username: ").strip()
        password = input_password("Enter password: ").strip()
        confirm_password = input_password("Confirm password: ").strip()
        clear_terminal()
        if password != confirm_password:
            print("Passwords do not match.")
            return

        role = "system_administrator"
        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip()

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                # Check if username exists
                user_id = get_user_id_by_username(username)

                if user_id != None:
                    print("Username already exists.")
                    return

                hashed_password = hash_password(password)

                # Insert into users table
                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)
                """,
                    (
                        encryptor.encrypt_text(username).decode(),
                        encryptor.encrypt_text(hashed_password).decode(),
                        encryptor.encrypt_text(role).decode(),
                    ),
                )

                reg_date = datetime.now().strftime("%Y-%m-%d")

                # Insert into profiles table
                cursor.execute(
                    """
                    INSERT INTO profiles (user_id, first_name, last_name, registration_date)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        user_id,
                        encryptor.encrypt_text(first_name).decode(),
                        encryptor.encrypt_text(last_name).decode(),
                        encryptor.encrypt_text(reg_date).decode(),
                    ),
                )

                conn.commit()
                print(f"\nUser '{username}' added successfully with role '{role}'.\n")

        except sqlite3.Error as e:
            print("Database error:", e)

    def update_user(self):
        clear_terminal()
        username = input("Enter username: ").strip()
        password = input_password("Enter password: ").strip()

        try:
            with get_connection() as conn:
                cursor = conn.cursor()

                # Check if username exists
                user_id = get_user_id_by_username(username)

                if user_id == None:
                    print("Username doesn't exists.")
                    return

                # test if passwords match
                hashed_password = hash_password(password)
                cursor.execute(
                    "SELECT password_hash FROM users WHERE id = ?", (user_id)
                )
                stored_password_row = cursor.fetchone()

                if not stored_password_row:
                    print("Could not retrieve password.")
                    return

                stored_hash = stored_password_row[0]

                if not verify_password(hashed_password, stored_hash):
                    print("Password or username incorrect.")
                    return

                cursor.execute(
                    "SELECT role FROM users WHERE id = ?",
                    (get_user_id_by_username(username),),
                )

                encrypted_user_subject_role = cursor.fetchone()
                decrypted_user_subject_role = encryptor.decrypt_text(
                    encrypted_user_subject_role.encode()
                )
                print("[ERROR] No user found.")

                clear_terminal()

                if self.role == "service_engineer":
                    # Service engineers cannot update anyone
                    print("\n === Not authorized to perform updates ===")
                    return

                elif self.role == "system_administrator":
                    # System admin updating another system admin
                    if (
                        decrypted_user_subject_role == "system_administrator"
                        and self.id != user_id
                    ):
                        print(
                            "\n === Not authorized to update another system administrator ==="
                        )
                        return
                    # System admin trying to update a super admin
                    elif decrypted_user_subject_role == "super_administrator":
                        print(
                            "\n === Not authorized to update a super administrator ==="
                        )
                        return
                    # System admin updating self or a service engineer
                    else:
                        print("\n === Update Service Engineer/System Administrator ===")

                elif self.role == "super_administrator":
                    # Super admin cannot update themselves
                    if self.id == user_id:
                        print("\n === Unable to update super administrator (self) ===")
                        return
                    # Can update system administrators or service engineers
                    else:
                        print("\n === Update Service Engineer/System Administrator ===")

                else:
                    print("\n === No valid login ===")
                    return

                # If the update is allowed, show options
                print("1. Update Username")
                print("2. Update First name")
                print("3. Update Last name")
                choice = input("Enter number (1-3): ").strip()

                # Update users table
                if choice == "1":
                    new_userName = input("Enter new username: ").strip()
                    cursor.execute(
                        "UPDATE users SET username = ? WHERE id = ?",
                        (encryptor.encrypt_text(new_userName).decode(), user_id),
                    )
                    clear_terminal()
                    print(f"[SUCCES] User {new_userName} updated succesfully")

                # Update profiles table
                elif choice == "2":
                    new_firstName = input("Enter new first name: ").strip()
                    cursor.execute(
                        "UPDATE profiles SET first_name = ? WHERE user_id = ?",
                        (encryptor.encrypt_text(new_firstName).decode(), user_id),
                    )
                    clear_terminal()
                    print(f"[SUCCES] User {username} updated succesfully")

                # Update profiles table
                elif choice == "3":
                    new_lastName = input("Enter new last name: ").strip()
                    cursor.execute(
                        "UPDATE profiles SET last_name = ? WHERE user_id = ?",
                        (encryptor.encrypt_text(new_lastName).decode(), user_id),
                    )
                    clear_terminal()
                    print(f"[SUCCES] User {username} updated succesfully")

                else:
                    print("[ERROR] Invalid choice.")
                    return

                conn.commit()

        except sqlite3.Error as e:
            print("Database error:", e)

    def delete_system_administrator():
        username = input("Enter username: ").strip()
        password = input_password("Enter password: ").strip()

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                # Check if username exists
                user_id = get_user_id_by_username(username)

                if user_id == None:
                    print("Username doesn't exists.")
                    return

                hashed_password = hash_password(password)

                # test if passwords match
                hashed_password = hash_password(password)
                cursor.execute(
                    "SELECT password_hash FROM users WHERE id = ?", (user_id,)
                )
                stored_password_row = cursor.fetchone()
                if not stored_password_row:
                    print("Could not retrieve password.")
                    return
                stored_hash = stored_password_row[0]
                if not verify_password(hashed_password, stored_hash):
                    print("Password or username incorrect.")
                    return

                # delete user from profiles
                cursor.execute("DELETE FROM profiles WHERE user_id = ?", (user_id,))
                if cursor.rowcount == 0:
                    print("User not found or already deleted.")

                # delete user from users
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                if cursor.rowcount == 0:
                    print("User not found or already deleted.")

                conn.commit()
                clear_terminal()
                print(f"[SUCCES] User {username} deleted succesfully")
        except sqlite3.Error as e:
            print("Database error:", e)

    def add_service_engineer(self):
        clear_terminal()

        if self.role != "super_administrator" or self.role != "system_administrator":
            print("You are unauthorized to add a user")
            return

        username = input("Enter username: ").strip()
        password = input_password("Enter password: ").strip()

        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip()

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                # Check if username exists
                user_id = get_user_id_by_username(username)

                if user_id != None:
                    print("Username already exists.")
                    return

                hashed_password = hash_password(password)

                # Insert into users table
                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)
                """,
                    (username, hashed_password, "service_engineer"),
                )

                # get userId
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                user_id_row = cursor.fetchone()
                if user_id_row is None:
                    print("User not found after insert — unexpected.")
                    return

                user_id = user_id_row[0]
                reg_date = datetime.now().strftime("%Y-%m-%d")

                # Insert into profiles table
                cursor.execute(
                    """
                    INSERT INTO profiles (user_id, first_name, last_name, registration_date)
                    VALUES (?, ?, ?, ?)
                """,
                    (user_id, first_name, last_name, reg_date),
                )

                conn.commit()
                print(f"[SUCCES] user: {username} succesfully added")

        except sqlite3.Error as e:
            print("Database error:", e)

    # def update_service_engineer(self):
    #     clear_terminal()
    #     username = input("Enter username: ").strip()
    #     password = input_password("Enter password: ").strip()

    #     try:
    #         with get_connection() as conn:
    #             cursor = conn.cursor()

    #             # Check if username exists
    #             user_id = get_user_id_by_username(username)

    #             if user_id == None:
    #                 print("Username already exists.")
    #                 return

    #             # test if passwords match
    #             hashed_password = hash_password(password)
    #             cursor.execute(
    #                 "SELECT password_hash FROM users WHERE id = ?", (user_id)
    #             )
    #             stored_password_row = cursor.fetchone()

    #             if not stored_password_row:
    #                 print("Could not retrieve password.")
    #                 return

    #             stored_hash = stored_password_row[0]

    #             if not verify_password(hashed_password, stored_hash):
    #                 print("Password or username incorrect.")
    #                 return

    #             clear_terminal()
    #             print("\n === Update Service Engineer ===")
    #             print("1. Update Username")
    #             print("2. Update First name")
    #             print("3. Update Last name")
    #             choice = input("Enter number (1-3): ").strip()

    #             # Update users table
    #             if choice == "1":
    #                 new_userName = input("Enter new username: ").strip()
    #                 cursor.execute(
    #                     "UPDATE users SET username = ? WHERE id = ?",
    #                     (encryptor.encrypt_text(new_userName).decode(), user_id),
    #                 )
    #                 clear_terminal()
    #                 print(f"[SUCCES] User {new_userName} updated succesfully")

    #             # Update profiles table
    #             elif choice == "2":
    #                 new_firstName = input("Enter new first name: ").strip()
    #                 cursor.execute(
    #                     "UPDATE profiles SET first_name = ? WHERE user_id = ?",
    #                     (encryptor.encrypt_text(new_firstName).decode(), user_id),
    #                 )
    #                 clear_terminal()
    #                 print(f"[SUCCES] User {username} updated succesfully")

    #             # Update profiles table
    #             elif choice == "3":
    #                 new_lastName = input("Enter new last name: ").strip()
    #                 cursor.execute(
    #                     "UPDATE profiles SET last_name = ? WHERE user_id = ?",
    #                     (encryptor.encrypt_text(new_lastName).decode(), user_id),
    #                 )
    #                 clear_terminal()
    #                 print(f"[SUCCES] User {username} updated succesfully")

    #             else:
    #                 print("[ERROR] Invalid choice.")
    #                 return

    #             conn.commit()

    #     except sqlite3.Error as e:
    #         print("Database error:", e)

    def delete_service_engineer(self):
        username = input("Enter username: ").strip()
        password = input_password("Enter password: ").strip()

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                # Check if username exists
                user_id = get_user_id_by_username(username)

                if user_id == None:
                    print("Username doesn't exists.")
                    return

                hashed_password = hash_password(password)

                # test if passwords match
                hashed_password = hash_password(password)
                cursor.execute(
                    "SELECT password_hash FROM users WHERE id = ?", (user_id,)
                )
                stored_password_row = cursor.fetchone()
                if not stored_password_row:
                    print("Could not retrieve password.")
                    return
                stored_hash = stored_password_row[0]
                if not verify_password(hashed_password, stored_hash):
                    print("Password or username incorrect.")
                    return

                # delete user from profiles
                cursor.execute("DELETE FROM profiles WHERE user_id = ?", (user_id,))
                if cursor.rowcount == 0:
                    print("User not found or already deleted.")

                # delete user from users
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                if cursor.rowcount == 0:
                    print("User not found or already deleted.")

                conn.commit()
                clear_terminal()
                print(f"[SUCCES] User {username} deleted succesfully")
        except sqlite3.Error as e:
            print("Database error:", e)

    def display_users(self):

        try:
            clear_terminal()
            print("=== User display ===")
            start = input("Enter starting index (0 for beginning): ").strip()
            if not start.isdigit():
                print("Invalid input. Must be a non-negative number.")
                return

            offset = int(start)

            with get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT username, role FROM users LIMIT 100 OFFSET ?", (offset,)
                )
                users = cursor.fetchall()

                if not users:
                    print("\nNo users found from this starting point.")
                    return

                print(
                    f"\n=== Users List (From {offset} to {offset + len(users) - 1}) ==="
                )
                for username, role in users:
                    print(f"Username: {username} | Role: {role}")

        except Exception as e:
            print("Error fetching users:", e)

    def change_password(self, target_username=None):

        ROLE_LEVELS = {
            "service_engineer": 1,
            "system_administrator": 2,
            "super_administrator": 3,
        }

        print("=== Change Password ===")

        # Ask for target username if not provided
        if not target_username:
            target_username = input("Enter username to change password for: ").strip()

        try:
            with get_connection() as conn:
                cursor = conn.cursor()

                # Retrieve user info
                cursor.execute(
                    "SELECT id, role, password_hash FROM users WHERE id = ?",
                    (get_user_id_by_username(target_username),),
                )
                target_row = cursor.fetchone()
                if not target_row:
                    print("[ERROR] Target username not found.")
                    return

                target_id, target_role, stored_hash = target_row

                # --- Role validation ---
                if self.role not in ROLE_LEVELS or target_role not in ROLE_LEVELS:
                    print("[ERROR] Unknown role detected.")
                    return

                self_role_level = ROLE_LEVELS[self.role]
                target_role_level = ROLE_LEVELS[target_role]

                # Prevent changing password of same/higher role (unless it’s your own)
                if (
                    target_username != self.userName
                    and self_role_level <= target_role_level
                ):
                    print(
                        "[ERROR] You cannot change the password of a user with an equal or higher role."
                    )
                    return

                # --- If changing own password, verify current one ---
                if target_username == self.userName:
                    current_password = input_password("Enter your current password: ")
                    if not verify_password(current_password, stored_hash):
                        print("[ERROR] Incorrect current password.")
                        return

                # --- Get new password (with strength validation inside input_password) ---
                new_password = input_password(
                    "Enter new password: ", validate_strength=True
                )
                confirm_password = input_password("Confirm new password: ")

                if new_password != confirm_password:
                    print("[ERROR] Passwords do not match.")
                    return

                if verify_password(new_password, stored_hash):
                    print("[ERROR] New password cannot be the same as the old one.")
                    return

                # --- Hash and encrypt new password ---
                new_hash = hash_password(new_password)
                encrypted_new_hash = encryptor.encrypt_text(new_hash).decode()

                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (encrypted_new_hash, target_id),
                )
                conn.commit()

                print(
                    f"[SUCCESS] Password for user '{target_username}' changed successfully."
                )

        except sqlite3.Error as e:
            print("[DB ERROR]", e)

    # def changePasswordSE(self):
    #     print("=== Change Service Engineer Password ===")
    #     username = input("Enter username: ").strip()
    #     current_password = input_password("Enter current password: ").strip()

    #     try:
    #         with get_connection() as conn:
    #             cursor = conn.cursor()

    #             # Check if user exists
    #             cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    #             user_row = cursor.fetchone()
    #             if not user_row:
    #                 print("[ERROR] Username doesn't exist.")
    #                 return

    #             user_id = user_row[0]

    #             # Get stored hash and verify
    #             hashed_password = hash_password(current_password)
    #             cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
    #             stored_password_row = cursor.fetchone()
    #             if not stored_password_row:
    #                 print("Could not retrieve password.")
    #                 return
    #             stored_hash = stored_password_row[0]

    #             if not verify_password(hashed_password, stored_hash):
    #                 print("Password or username incorrect.")
    #                 return

    #             # Ask for new password and confirmation
    #             new_password = input_password("Enter new password: ").strip()
    #             confirm_password = input_password("Confirm new password: ").strip()

    #             if new_password != confirm_password:
    #                 print("[ERROR] Passwords do not match.")
    #                 return

    #             new_hash = hash_password(new_password)

    #             # Update password
    #             cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
    #             conn.commit()
    #             clear_terminal()
    #             print(f"[SUCCES] Password of user {username} changed successfully.")

    #     except sqlite3.Error as e:
    #         print("Database error:", e)
