from datetime import datetime
import re
from db.database import get_connection
from ui.terminal import clear_terminal
from Utils.encryption import Encryptor

encryptor = Encryptor()


class Traveller:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        birthday: str,
        gender: str,
        street_name: str,
        house_number: str,
        zip_code: str,
        city: str,
        email: str,
        mobile_phone: str,
        driving_license_number: str,
    ):
        # Validation
        if not re.fullmatch(r"\d{4}[A-Z]{2}", zip_code):
            raise ValueError("Zip code must be in the format 1234AB.")
        if not re.fullmatch(r"06\d{8}", mobile_phone):
            raise ValueError("Mobile phone must start with 06 and be 10 digits long.")
        if not re.fullmatch(r"[A-Z0-9]{8,12}", driving_license_number):
            raise ValueError(
                "Driving license number must be 8–12 alphanumeric characters."
            )
        if len(street_name) < 2:
            raise ValueError("Street name must be at least 2 characters.")
        if not re.fullmatch(r"\d+[A-Za-z]?", house_number):
            raise ValueError(
                "House number must be numeric, optionally with a letter (e.g., 12A)."
            )
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format.")
        try:
            datetime.strptime(birthday, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Birthday must be in format YYYY-MM-DD.")

        # Assign
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.gender = gender
        self.street_name = street_name
        self.house_number = house_number
        self.zip_code = zip_code
        self.city = city
        self.email = email
        self.mobile_phone = mobile_phone
        self.driving_license_number = driving_license_number

    def add_to_db(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO travellers (
                    first_name, last_name, birthday, gender, street_name,
                    house_number, zip_code, city, email, mobile_phone, driving_license_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    encryptor.encrypt_text(self.first_name).decode(),
                    encryptor.encrypt_text(self.last_name).decode(),
                    encryptor.encrypt_text(self.birthday).decode(),
                    encryptor.encrypt_text(self.gender).decode(),
                    encryptor.encrypt_text(self.street_name).decode(),
                    encryptor.encrypt_text(self.house_number).decode(),
                    encryptor.encrypt_text(self.zip_code).decode(),
                    encryptor.encrypt_text(self.city).decode(),
                    encryptor.encrypt_text(self.email).decode(),
                    encryptor.encrypt_text(self.mobile_phone).decode(),
                    encryptor.encrypt_text(self.driving_license_number).decode(),
                ),
            )
            conn.commit()
            print("[SUCCESS] Traveller added to database.")

    @staticmethod
    def update_traveller():
        print("=== Update Traveller ===")
        traveller_id = input("Enter traveller ID to update: ").strip()

        # Map of allowed columns and their validation rules
        fields = {
            "first_name": {
                "pattern": r"[A-Za-z\-]{2,}",
                "error": "At least 2 letters",
                "encrypted": True,
            },
            "last_name": {
                "pattern": r"[A-Za-z\-]{2,}",
                "error": "At least 2 letters",
                "encrypted": True,
            },
            "birthday": {
                "validator": validate_date,
                "encrypted": True,
            },
            "gender": {
                "pattern": r"[MFO]",
                "error": "Must be M, F, or O",
                "encrypted": True,
            },
            "street_name": {
                "pattern": r".{2,}",
                "error": "At least 2 chars",
                "encrypted": True,
            },
            "house_number": {
                "pattern": r"\d+[A-Za-z]?",
                "error": "Invalid format",
                "encrypted": True,
            },
            "zip_code": {
                "pattern": r"\d{4}[A-Z]{2}",
                "error": "Format 1234AB",
                "encrypted": True,
            },
            "city": {
                "pattern": r".{2,}",
                "error": "At least 2 chars",
                "encrypted": True,
            },
            "email": {
                "pattern": r"[^@]+@[^@]+\.[^@]+",
                "error": "Invalid email",
                "encrypted": True,
            },
            "mobile_phone": {
                "pattern": r"06\d{8}",
                "error": "Must start with 06",
                "encrypted": True,
            },
            "driving_license_number": {
                "pattern": r"[A-Z0-9]{8,12}",
                "error": "8–12 chars",
                "encrypted": True,
            },
        }

        print("Available fields to update:")
        for i, field in enumerate(fields.keys(), 1):
            print(f"{i}. {field}")

        field_choice = input("Enter the field name to update: ").strip() # the name, not the number
        if field_choice not in fields:
            print("[ERROR] Invalid field.")
            return

        field = fields[field_choice]
        pattern = field.get("pattern")
        error_msg = field.get("error", "Invalid input.")
        validator = field.get("validator")

        new_value = get_valid_input(
            f"Enter new value for {field_choice}: ", pattern, error_msg, validator
        )
        if new_value is None:
            return

        if field.get("encrypted"):
            new_value = encryptor.encrypt_text(new_value).decode()

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE travellers SET {field_choice} = ? WHERE id = ?",
                (new_value, traveller_id),
            )
            conn.commit()
            print(f"[SUCCESS] Traveller's {field_choice} updated.")

    @staticmethod
    def delete_traveller():
        print("=== Delete Traveller ===")
        traveller_id = input("Enter traveller ID to delete: ").strip()

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM travellers WHERE id = ?", (traveller_id,))
            conn.commit()
            print("[SUCCESS] Traveller deleted.")

    @staticmethod
    def search_traveller():
        print("=== Search Traveller ===")
        print("1. By ID")
        print("2. By First or Last Name")
        choice = input("Choose option: ").strip()

        with get_connection() as conn:
            cursor = conn.cursor()
            results = []

            if choice == "1":
                traveller_id = input("Enter ID: ").strip()
                cursor.execute("SELECT * FROM travellers WHERE id = ?", (traveller_id,))
                results = cursor.fetchall()

            elif choice == "2":
                term = input("Enter name to search: ").strip().lower()
                cursor.execute("SELECT * FROM travellers")
                all_travellers = cursor.fetchall()

                for t in all_travellers:
                    try:
                        first_name = encryptor.decrypt_text(t[1].encode()).lower()
                        last_name = encryptor.decrypt_text(t[2].encode()).lower()
                    except Exception:
                        first_name = t[1].lower() if t[1] else ""
                        last_name = t[2].lower() if t[2] else ""

                    if term in first_name or term in last_name:
                        results.append(t)
            else:
                print("[ERROR] Invalid option.")
                return

            if results:
                for t in results:
                    Traveller.print_info(t)
            else:
                print("[INFO] No traveller found.")

    @staticmethod
    def print_info(traveller_data: tuple):
        encrypted_indices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        decrypted_data = list(traveller_data)

        for i in encrypted_indices:
            value = traveller_data[i]
            if value is not None:
                try:
                    decrypted_data[i] = encryptor.decrypt_text(value.encode())
                except Exception:
                    decrypted_data[i] = value

        print(
            f"\nTraveller ID: {decrypted_data[0]}"
            f"\nFirst Name: {decrypted_data[1]}"
            f"\nLast Name: {decrypted_data[2]}"
            f"\nBirthday: {decrypted_data[3]}"
            f"\nGender: {decrypted_data[4]}"
            f"\nStreet Name: {decrypted_data[5]}"
            f"\nHouse Number: {decrypted_data[6]}"
            f"\nZip Code: {decrypted_data[7]}"
            f"\nCity: {decrypted_data[8]}"
            f"\nEmail: {decrypted_data[9]}"
            f"\nMobile Phone: {decrypted_data[10]}"
            f"\nDriving License #: {decrypted_data[11]}"
        )

    @staticmethod
    def get_all_travellers():
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM travellers")
            return cursor.fetchall()


def get_valid_input(
    prompt, pattern=None, error_msg=None, validator=None, allow_back=True
):
    while True:
        value = input(prompt).strip()
        if allow_back and value.lower() == "q":
            return None  # Signal to go back
        if pattern and not re.fullmatch(pattern, value):
            print(f"[ERROR] {error_msg}")
            continue
        if validator:
            try:
                return validator(value)
            except Exception as e:
                print(f"[ERROR] {e}")
                continue
        return value


def validate_date(date_str):
    datetime.strptime(date_str, "%Y-%m-%d")
    return date_str


def manage_traveller():
    while True:
        print("\n=== Manage Travellers ===")
        print("1. Add Traveller")
        print("2. Update Traveller")
        print("3. Delete Traveller")
        print("4. Search Traveller")
        print("5. Print All Travellers")
        print("6. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            clear_terminal()
            print("=== Add New Traveller ===")
            print("(Enter 'Q' at any prompt to quit)\n")

            try:
                first_name = get_valid_input(
                    "First name: ",
                    r"[A-Za-z\-]{2,}",
                    "First name must be at least 2 letters.",
                )
                if first_name is None:
                    return
                last_name = get_valid_input(
                    "Last name: ",
                    r"[A-Za-z\-]{2,}",
                    "Last name must be at least 2 letters.",
                )
                if last_name is None:
                    return
                gender = get_valid_input(
                    "Gender (M/F/O): ", r"[MFO]", "Gender must be M, F, or O."
                )
                if gender is None:
                    return
                birthday = get_valid_input(
                    "Birthday (YYYY-MM-DD): ", validator=validate_date
                )
                if birthday is None:
                    return
                zip_code = get_valid_input(
                    "Zip Code (e.g., 1234AB): ",
                    r"\d{4}[A-Z]{2}",
                    "Format must be 1234AB.",
                )
                if zip_code is None:
                    return
                city = get_valid_input(
                    "City: ", r".{2,}", "City name must be at least 2 characters."
                )
                if city is None:
                    return
                street_name = get_valid_input(
                    "Street Name: ",
                    r".{2,}",
                    "Street name must be at least 2 characters.",
                )
                if street_name is None:
                    return
                house_number = get_valid_input(
                    "House Number: ",
                    r"\d+[A-Za-z]?",
                    "Must be numeric, optionally with a letter.",
                )
                if house_number is None:
                    return
                mobile_phone = get_valid_input(
                    "Mobile Phone (06XXXXXXXX): ",
                    r"06\d{8}",
                    "Must start with 06 and be 10 digits.",
                )
                if mobile_phone is None:
                    return
                email = get_valid_input(
                    "Email: ", r"[^@]+@[^@]+\.[^@]+", "Invalid email address format."
                )
                if email is None:
                    return
                driving_license_number = get_valid_input(
                    "Driving License Number: ",
                    r"[A-Z0-9]{8,12}",
                    "Must be 8–12 alphanumeric characters.",
                )
                if driving_license_number is None:
                    return

                t = Traveller(
                    first_name,
                    last_name,
                    birthday,
                    gender,
                    street_name,
                    house_number,
                    zip_code,
                    city,
                    email,
                    mobile_phone,
                    driving_license_number,
                )
                t.add_to_db()

            except Exception as e:
                print(f"[ERROR] {e}")

        elif choice == "2":
            clear_terminal()
            Traveller.update_traveller()

        elif choice == "3":
            clear_terminal()
            Traveller.delete_traveller()

        elif choice == "4":
            clear_terminal()
            Traveller.search_traveller()

        elif choice == "5":
            travellers = Traveller.get_all_travellers()
            if travellers:
                print("=== All Travellers ===")
                for t in travellers:
                    Traveller.print_info(t)
            else:
                print("[INFO] No travellers found.")

        elif choice == "6":
            clear_terminal()
            print("Exiting...")
            break
        else:
            clear_terminal()
            print("[ERROR] Invalid choice. Please try again.")
