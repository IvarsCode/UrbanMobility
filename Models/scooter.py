from datetime import datetime
import re
from db.database import get_connection


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

    def add_to_db(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
            INSERT INTO scooters (
                brand, model, serial_number, top_speed, battery_capacity,
                soc, target_range_min, target_range_max,
                latitude, longitude, out_of_service,
                mileage, last_maintenance
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.brand,
                    self.model,
                    self.serialNumber,
                    self.topSpeed,
                    self.batteryCapacity,
                    self.SoC,
                    self.targetRangeSoC[0],
                    self.targetRangeSoC[1],
                    self.location[0],
                    self.location[1],
                    int(self.outOfService),  # Store boolean as 0/1
                    self.mileage,
                    self.lastMaintenanceDate,
                ),
            )
        conn.commit()
        print("[SUCCESS] Scooter added to database.")

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
            },
            "model": {
                "pattern": r".{1,}",
                "error": "Model must be at least 1 character.",
            },
            "serial_number": {
                "pattern": r"[A-Z0-9]{10,17}",
                "error": "Serial number must be 10–17 uppercase alphanumeric characters.",
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
                "validator": lambda x: datetime.strptime(x, "%Y-%m-%d")
            },
            "in_service_date": {
                "validator": lambda x: datetime.strptime(x, "%Y-%m-%d")
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

        # Convert boolean string to integer 0/1
        if field_choice == "out_of_service":
            new_value = 1 if new_value.lower() == "true" else 0

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
        print(
            f"\nScooter ID: {scooter_data[0]}"
            f"\nBrand: {scooter_data[1]}"
            f"\nModel: {scooter_data[2]}"
            f"\nSerial Number: {scooter_data[3]}"
            f"\nTop Speed (km/h): {scooter_data[4]}"
            f"\nBattery Capacity (Wh): {scooter_data[5]}"
            f"\nState of Charge (%): {scooter_data[6]}"
            f"\nTarget Range SoC (%): {scooter_data[7]} - {scooter_data[8]}"
            f"\nLocation (lat, long): {scooter_data[9]}, {scooter_data[10]}"
            f"\nOut of Service: {'Yes' if scooter_data[11] else 'No'}"
            f"\nMileage (km): {scooter_data[12]}"
            f"\nLast Maintenance Date: {scooter_data[13]}"
            f"\nIn Service Date: {scooter_data[14]}"
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
            elif choice == "2":
                term = input("Enter brand or model name: ").strip()
                cursor.execute(
                    "SELECT * FROM scooters WHERE brand LIKE ? OR model LIKE ?",
                    (f"%{term}%", f"%{term}%"),
                )
            else:
                print("[ERROR] Invalid option.")
                return

            results = cursor.fetchall()
            if results:
                for scooter in results:
                    Scooter.print_info(scooter)
            else:
                print("[INFO] No scooters found.")


def get_valid_input(prompt, pattern=None, error_msg=None, validator=None):
    while True:
        value = input(prompt).strip()
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
            # You can call Scooter.add_scooter() or handle input here
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
