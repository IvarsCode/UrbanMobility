from datetime import datetime
import re
from db.database import get_connection
from Utils.encryption import Encryptor

encryptor = Encryptor()


class Scooter:
    def __init__(
        self,
        brand: str,
        model: str,
        serialNumber: str,  # 10 to 17 alphanumeric characters
        topSpeed: int,  # km/h
        batteryCapacity: int,  # Wh
        SoC: float,  # percentage
        targetRangeSoC: list[float],  # [min, max] percentage
        location: list[float],  # [latitude, longitude]
        outOfService: bool,
        mileage: float,  # in kilometers
        lastMaintenanceDate: str,  # YYYY-MM-DD
        inServiceDate: str,  # YYYY-MM-DD
    ):
        # === VALIDATION ===
        if not brand or len(brand) < 2:
            raise ValueError("Brand must be at least 2 characters.")

        if not model or len(model) < 1:
            raise ValueError("Model must be provided.")

        if not re.fullmatch(r"[A-Z0-9]{10,17}", serialNumber):
            raise ValueError(
                "Serial number must be 10 to 17 alphanumeric characters (uppercase A–Z, 0–9)."
            )

        if not (0 <= SoC <= 100):
            raise ValueError("SoC must be between 0 and 100.")

        if (
            not isinstance(targetRangeSoC, list)
            or len(targetRangeSoC) != 2
            or not all(isinstance(val, (int, float)) for val in targetRangeSoC)
            or not (0 <= targetRangeSoC[0] <= 100)
            or not (0 <= targetRangeSoC[1] <= 100)
            or targetRangeSoC[0] > targetRangeSoC[1]
        ):
            raise ValueError(
                "targetRangeSoC must be a list of two percentages [min, max] between 0 and 100."
            )

        if (
            not isinstance(location, list)
            or len(location) != 2
            or not (-90 <= location[0] <= 90)
            or not (-180 <= location[1] <= 180)
        ):
            raise ValueError(
                "Location must be a list [latitude, longitude] with valid GPS ranges."
            )

        if mileage < 0:
            raise ValueError("Mileage must be non-negative.")

        try:
            datetime.strptime(lastMaintenanceDate, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Last maintenance date must be in YYYY-MM-DD format.")

        try:
            datetime.strptime(inServiceDate, "%Y-%m-%d")
        except ValueError:
            raise ValueError("In service date date must be in YYYY-MM-DD format.")

        self.brand = brand
        self.model = model
        self.serialNumber = serialNumber
        self.topSpeed = topSpeed
        self.batteryCapacity = batteryCapacity
        self.SoC = SoC
        self.targetRangeSoC = targetRangeSoC
        self.location = location
        self.outOfService = outOfService
        self.mileage = mileage
        self.lastMaintenanceDate = lastMaintenanceDate
        self.inServiceDate = inServiceDate

    def add_to_db(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
            INSERT INTO scooters (
                brand, model, serial_number, top_speed, battery_capacity,
                soc, target_range_min, target_range_max,
                latitude, longitude, out_of_service,
                mileage, last_maintenance, in_service_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    encryptor.encrypt_text(self.brand).decode(),
                    encryptor.encrypt_text(self.model).decode(),
                    encryptor.encrypt_text(self.serialNumber).decode(),
                    self.topSpeed,
                    self.batteryCapacity,
                    self.SoC,
                    self.targetRangeSoC[0],
                    self.targetRangeSoC[1],
                    self.location[0],
                    self.location[1],
                    int(self.outOfService),  # Store boolean as 0/1
                    self.mileage,
                    encryptor.encrypt_text(self.lastMaintenanceDate).decode(),
                    encryptor.encrypt_text(self.inServiceDate).decode(),
                ),
            )
        conn.commit()
        print("[SUCCESS] Scooter added to database.")

    def get_all_scooters():
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM scooters")
            scooters = cursor.fetchall()
            return scooters

    @staticmethod
    def add_scooter():
        print("=== Add New Scooter ===")
        print("(Enter 'q' at any prompt to quit)")
        try:
            brand = get_valid_input(
                "Brand: ", r".{2,}", "Brand must be at least 2 characters."
            )
            if brand is None:
                return

            model = get_valid_input("Model: ", r".{1,}", "Model must be provided.")
            if model is None:
                return

            serial_number = get_valid_input(
                "Serial number (10–17 chars, uppercase A–Z, 0–9): ",
                r"[A-Z0-9]{10,17}",
                "Serial number must be 10–17 uppercase alphanumeric characters.",
            )
            if serial_number is None:
                return

            top_speed = get_valid_input(
                "Top speed (km/h): ", r"\d+", "Top speed must be a positive integer."
            )
            if top_speed is None:
                return

            battery_capacity = get_valid_input(
                "Battery capacity (Wh): ",
                r"\d+",
                "Battery capacity must be a positive integer.",
            )
            if battery_capacity is None:
                return

            soc = get_valid_input(
                "Current State of Charge (%): ",
                r"\d+(\.\d+)?",
                "SoC must be a number between 0 and 100.",
                validator=lambda v: (
                    float(v)
                    if 0 <= float(v) <= 100
                    else (_ for _ in ()).throw(
                        ValueError("SoC must be between 0 and 100.")
                    )
                ),
            )
            if soc is None:
                return

            target_range_min = get_valid_input(
                "Target range minimum SoC (%): ",
                r"\d+(\.\d+)?",
                "Must be a number between 0 and 100.",
                validator=lambda v: (
                    float(v)
                    if 0 <= float(v) <= 100
                    else (_ for _ in ()).throw(
                        ValueError("Min SoC must be between 0 and 100.")
                    )
                ),
            )
            if target_range_min is None:
                return

            target_range_max = get_valid_input(
                "Target range maximum SoC (%): ",
                r"\d+(\.\d+)?",
                "Must be a number between 0 and 100.",
                validator=lambda v: (
                    float(v)
                    if 0 <= float(v) <= 100
                    else (_ for _ in ()).throw(
                        ValueError("Max SoC must be between 0 and 100.")
                    )
                ),
            )
            if target_range_max is None:
                return

            if float(target_range_min) > float(target_range_max):
                raise ValueError("Minimum SoC cannot be greater than maximum SoC.")

            latitude = get_valid_input(
                "Latitude: ",
                r"-?\d+(\.\d+)?",
                "Invalid latitude.",
                validator=lambda v: (
                    float(v)
                    if -90 <= float(v) <= 90
                    else (_ for _ in ()).throw(
                        ValueError("Latitude must be between -90 and 90.")
                    )
                ),
            )
            if latitude is None:
                return

            longitude = get_valid_input(
                "Longitude: ",
                r"-?\d+(\.\d+)?",
                "Invalid longitude.",
                validator=lambda v: (
                    float(v)
                    if -180 <= float(v) <= 180
                    else (_ for _ in ()).throw(
                        ValueError("Longitude must be between -180 and 180.")
                    )
                ),
            )
            if longitude is None:
                return
            out_of_service = (
                get_valid_input(
                    "Is scooter out of service? (yes/no): ",
                    r"(yes|no)",
                    "Enter 'yes' or 'no'.",
                ).lower()
                == "yes"
            )
            if out_of_service is None:
                return

            mileage = get_valid_input(
                "Mileage (km): ",
                r"\d+(\.\d+)?",
                "Mileage must be a non-negative number.",
                validator=lambda v: (
                    float(v)
                    if float(v) >= 0
                    else (_ for _ in ()).throw(
                        ValueError("Mileage must be non-negative.")
                    )
                ),
            )
            if mileage is None:
                return

            last_maintenance = get_valid_input(
                "Last maintenance date (YYYY-MM-DD): ",
                validator=lambda v: (
                    v
                    if datetime.strptime(v, "%Y-%m-%d")
                    else (_ for _ in ()).throw(ValueError("Invalid date format."))
                ),
            )
            if last_maintenance is None:
                return

            in_service_date = get_valid_input(
                "In service date (YYYY-MM-DD): ",
                validator=lambda v: (
                    v
                    if datetime.strptime(v, "%Y-%m-%d")
                    else (_ for _ in ()).throw(ValueError("Invalid date format."))
                ),
            )
            if in_service_date is None:
                return

            scooter = Scooter(
                brand=brand,
                model=model,
                serialNumber=serial_number,
                topSpeed=int(top_speed),
                batteryCapacity=int(battery_capacity),
                SoC=float(soc),
                targetRangeSoC=[float(target_range_min), float(target_range_max)],
                location=[float(latitude), float(longitude)],
                outOfService=out_of_service,
                mileage=float(mileage),
                lastMaintenanceDate=last_maintenance,
                inServiceDate=in_service_date,
            )
            scooter.add_to_db()

        except Exception as e:
            print(f"[ERROR] {e}")

    @staticmethod
    def delete_scooter():
        print("=== Delete Scooter ===")
        scooter_id = input("Enter scooter ID to delete: ").strip()

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scooters WHERE id = ?", (scooter_id,))
            conn.commit()
            print("[SUCCESS] Scooter deleted.")

    @staticmethod
    def update_scooter():
        print("=== Update Scooter ===")
        scooter_id = input("Enter scooter ID to update: ").strip()

        fields = {
            "brand": {
                "pattern": r".{2,}",
                "error": "Brand must be at least 2 characters.",
                "encrypted": True,
            },
            "model": {
                "pattern": r".{1,}",
                "error": "Model must be at least 1 character.",
                "encrypted": True,
            },
            "serial_number": {
                "pattern": r"[A-Z0-9]{10,17}",
                "error": "Serial number must be 10–17 uppercase alphanumeric characters.",
                "encrypted": True,
            },
            "top_speed": {
                "validator": lambda x: (
                    int(x) if int(x) > 0 else ValueError("Must be positive.")
                )
            },
            "battery_capacity": {
                "validator": lambda x: (
                    int(x) if int(x) > 0 else ValueError("Must be positive.")
                )
            },
            "soc": {
                "validator": lambda x: (
                    float(x)
                    if 0 <= float(x) <= 100
                    else ValueError("SoC must be 0–100.")
                )
            },
            "target_range_min": {
                "validator": lambda x: (
                    float(x) if 0 <= float(x) <= 100 else ValueError("Must be 0–100.")
                )
            },
            "target_range_max": {
                "validator": lambda x: (
                    float(x) if 0 <= float(x) <= 100 else ValueError("Must be 0–100.")
                )
            },
            "latitude": {
                "validator": lambda x: (
                    float(x)
                    if -90 <= float(x) <= 90
                    else ValueError("Invalid latitude.")
                )
            },
            "longitude": {
                "validator": lambda x: (
                    float(x)
                    if -180 <= float(x) <= 180
                    else ValueError("Invalid longitude.")
                )
            },
            "out_of_service": {"validator": lambda x: x.lower() in ["true", "false"]},
            "mileage": {
                "validator": lambda x: (
                    float(x)
                    if float(x) >= 0
                    else ValueError("Mileage must be non-negative.")
                )
            },
            "last_maintenance": {
                "validator": lambda x: datetime.strptime(x, "%Y-%m-%d"),
                "encrypted": True,
            },
            "in_service_date": {
                "validator": lambda x: datetime.strptime(x, "%Y-%m-%d"),
                "encrypted": True,
            },
        }

        print("Available fields to update:")
        for field in fields.keys():
            print(f"- {field}")

        field_choice = input("Enter field name to update: ").strip()
        if field_choice not in fields:
            print("[ERROR] Invalid field.")
            return

        field = fields[field_choice]
        validator = field.get("validator")
        pattern = field.get("pattern")
        error_msg = field.get("error", "Invalid input.")

        new_value = get_valid_input(
            f"Enter new value for {field_choice}: ",
            pattern=pattern,
            error_msg=error_msg,
            validator=validator,
        )
        if new_value is None:
            return

        if field_choice == "out_of_service":
            new_value = 1 if new_value.lower() == "true" else 0

        if field.get("encrypted"):
            new_value = encryptor.encrypt_text(str(new_value)).decode()

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE scooters SET {field_choice} = ? WHERE id = ?",
                (new_value, scooter_id),
            )
            conn.commit()
            print(f"[SUCCESS] Scooter's {field_choice} updated.")

    @staticmethod
    def print_info(scooter_data: tuple):
        encrypted_indices = [
            1,
            2,
            3,
            13,
            14,
        ]  # brand, model, serial_number, last_maintenance, in_service_date
        decrypted_data = list(scooter_data)

        for i in encrypted_indices:
            value = scooter_data[i]
            if value is not None:
                try:
                    decrypted_data[i] = encryptor.decrypt_text(value.encode())
                except Exception:
                    decrypted_data[i] = value

        print(
            f"\nScooter ID: {decrypted_data[0]}"
            f"\nBrand: {decrypted_data[1]}"
            f"\nModel: {decrypted_data[2]}"
            f"\nSerial Number: {decrypted_data[3]}"
            f"\nTop Speed (km/h): {decrypted_data[4]}"
            f"\nBattery Capacity (Wh): {decrypted_data[5]}"
            f"\nState of Charge (%): {decrypted_data[6]}"
            f"\nTarget Range SoC (%): {decrypted_data[7]} - {decrypted_data[8]}"
            f"\nLocation (lat, long): {decrypted_data[9]}, {decrypted_data[10]}"
            f"\nOut of Service: {'Yes' if decrypted_data[11] else 'No'}"
            f"\nMileage (km): {decrypted_data[12]}"
            f"\nLast Maintenance Date: {decrypted_data[13]}"
            f"\nIn Service Date: {decrypted_data[14]}"
        )

    @staticmethod
    def search_scooter():
        print("=== Search Scooter ===")
        print("1. By ID")
        print("2. By Brand or Model")
        choice = input("Choose option: ").strip()

        with get_connection() as conn:
            cursor = conn.cursor()

            if choice == "1":
                scooter_id = input("Enter scooter ID: ").strip()
                if not scooter_id.isdigit():
                    print("[ERROR] Scooter ID must be a number.")
                    return
                cursor.execute("SELECT * FROM scooters WHERE id = ?", (scooter_id,))
                results = cursor.fetchall()

            elif choice == "2":
                term = input("Enter brand or model name: ").strip().lower()

                # Fetch all scooters and decrypt in Python
                cursor.execute("SELECT * FROM scooters")
                all_scooters = cursor.fetchall()
                results = []

                for scooter in all_scooters:
                    try:
                        brand = encryptor.decrypt_text(scooter[1].encode()).lower()
                        model = encryptor.decrypt_text(scooter[2].encode()).lower()
                    except Exception:
                        # fallback for unencrypted data
                        brand = scooter[1].lower() if scooter[1] else ""
                        model = scooter[2].lower() if scooter[2] else ""

                    if term in brand or term in model:
                        results.append(scooter)

            else:
                print("[ERROR] Invalid option.")
                return

            if results:
                for scooter in results:
                    Scooter.print_info(scooter)
            else:
                print("[INFO] No scooters found.")


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


def manage_scooter():
    while True:
        print("\n=== Manage Scooters ===")
        print("1. Add Scooter")
        print("2. Update Scooter")
        print("3. Delete Scooter")
        print("4. Search Scooter")
        print("5. List All Scooters")
        print("6. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            Scooter.add_scooter()

        elif choice == "2":
            Scooter.update_scooter()

        elif choice == "3":
            Scooter.delete_scooter()

        elif choice == "4":
            Scooter.search_scooter()

        elif choice == "5":
            scooters = Scooter.get_all_scooters()
            if scooters:
                for s in scooters:
                    Scooter.print_info(s)
            else:
                print("[INFO] No scooters found.")

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("[ERROR] Invalid choice. Please try again.")
