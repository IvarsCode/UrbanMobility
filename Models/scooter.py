from datetime import datetime
import re
from db.database import get_connection


class Scooter:
    def __init__(
        self,
        brand: str,
        model: str,
        serialNumber: str,  # 10 to 17 alphanumeric characters
        topSpeed: int,  # in km/h
        batteryCapacity: int,  # in watt-hours (Wh)
        SoC: float,  # State of Charge in percentage
        targetRangeSoC: list[float],  # [min, max] SoC in percentage
        location: list[float],  # [latitude, longitude]
        outOfService: bool,  # True/False
        mileage: float,  # in kilometers
        lastMaintenanceDate: str,  # ISO 8601 format: YYYY-MM-DD
    ):
        # Validate serial number format
        if not re.fullmatch(r"[A-Za-z0-9]{10,17}", serialNumber):
            raise ValueError("Serial number must be 10 to 17 alphanumeric characters.")

        # Validate location (Rotterdam GPS coordinates range)
        lat, lon = location
        if not (51.85 <= lat <= 51.98 and 4.35 <= lon <= 4.55):
            raise ValueError("Location must be within the Rotterdam region.")

        # Validate location decimal precision
        if round(lat, 5) != lat or round(lon, 5) != lon:
            raise ValueError(
                "Latitude and longitude must be specified to 5 decimal places."
            )

        # Validate SoC and target SoC range
        if not (0 <= SoC <= 100):
            raise ValueError("State of Charge (SoC) must be between 0 and 100.")
        if not (0 <= targetRangeSoC[0] <= targetRangeSoC[1] <= 100):
            raise ValueError(
                "Target range SoC must be within 0 to 100 and in increasing order."
            )

        # Validate last maintenance date
        try:
            datetime.strptime(lastMaintenanceDate, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                "Last maintenance date must be in ISO 8601 format: YYYY-MM-DD"
            )

        # Set attributes
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

        # Automatically set in-service date to current time (ISO 8601 format)
        self.inServiceDate = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def __repr__(self):
        return f"<Scooter {self.serialNumber} - {self.brand} {self.model}>"

    def search_scooter(self):
        print("=== Search for Scooter ===")
        print("1. search on Brand")
        print("2. search on Model")
        print("3. search on Serial Number")
        print("4. search on ID")
        search_choice = input("Select search option: ").strip()

        if search_choice == "1":
            brand = input("Enter scooter brand: ").strip()
            self._search_scooter("brand", brand)
        elif search_choice == "2":
            model = input("Enter scooter model: ").strip()
            self._search_scooter("model", model)
        elif search_choice == "3":
            serial_number = input("Enter scooter serial number: ").strip()
            self._search_scooter("serial_number", serial_number)
        elif search_choice == "4":
            scooter_id = input("Enter scooter ID: ").strip()
            self._search_scooter("id", scooter_id)
        else:
            print("Invalid search option.")


def _search_scooter(column, value) -> Scooter | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM scooters WHERE {column}=?", (value,))
        scooter = cursor.fetchone()

        if scooter:
            return scooter
        else:
            return None


def printScooter(scooter: Scooter):
    print(
        f"Scooter found:"
        f"\nID = {scooter[0]}"
        f"\nBrand = {scooter[1]}"
        f"\nModel = {scooter[2]}"
        f"\nSerial Number = {scooter[3]}"
        f"\nTop Speed = {scooter[4]} km/h"
        f"\nBattery Capacity = {scooter[5]} Wh"
        f"\nState of Charge = {scooter[6]}%"
        f"\nTarget Range SoC = [{scooter[7]}%, {scooter[8]}%]"
        f"\nLocation (lat,long)= ({scooter[9]}, {scooter[10]})"
        f"\nOut of Service = {scooter[11]}"
        f"\nMileage = {scooter[12]} km"
        f"\nLast Maintenance Date = {scooter[13]}"
        f"\nIn Service Date = {scooter[14]}"
    )


def get_all_scooters():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM scooters")
        scooters = cursor.fetchall()
        return scooters


def updateScooter():
    while True:
        print("\n=== Update Scooter ===")
        i = 0
        scooters: list[Scooter] = get_all_scooters()
        print("\nList of scooters and serialnumbers:")
        for s in scooters:
            i += 1
            print(f"{i}. : {s[3]}")

        print("\n \n \n1. Choose Scooter")
        print("2. Go back")
        choice = input("Select an option: ").strip()

        if choice == "1":
            scooterSerial = input("Enter the serialnumber of the scooter: ").strip()
            while not re.fullmatch(r"[A-Za-z0-9]{10,17}", scooterSerial):
                scooterSerial = input(
                    "Please enter a correct serialnumber (10-17 alphanumeric characters): "
                ).strip()

            foundScooter = _search_scooter("serial_number", scooterSerial)
            if foundScooter is None:
                print("[ERROR] Scooter not found")
                break
            printScooter(foundScooter)
            while True:
                print

        elif choice == "2":
            print("Going back to dashboard")
            break
        else:
            print("[ERROR] Invalid choice.")
