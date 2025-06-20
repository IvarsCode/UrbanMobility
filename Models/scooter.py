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


def search_scooter():
    print("=== Search for Scooter ===")
    print("1. search on Brand")
    print("2. search on Model")
    print("3. search on Serial Number")
    print("4. search on ID")
    search_choice = input("Select search option: ").strip()

    if search_choice == "1":
        brand = input("Enter scooter brand: ").strip()
        filter_scooters("brand", brand)
    elif search_choice == "2":
        model = input("Enter scooter model: ").strip()
        filter_scooters("model", model)
    elif search_choice == "3":
        serial_number = input("Enter scooter serial number: ").strip()
        while not re.fullmatch(r"[A-Za-z0-9]{10,17}", serial_number):
            serial_number = input(
                "Please enter a correct serialnumber (10-17 alphanumeric characters): "
            ).strip()
        _search_scooter("serial_number", serial_number)
    elif search_choice == "4":
        scooter_id = input("Enter scooter ID: ").strip()
        _search_scooter("id", scooter_id)
    else:
        print("Invalid search option.")


def filter_scooters(column, value):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM scooters WHERE {column}=?", (value,))
        scooter = cursor.fetchall()

        if scooter:
            return scooter
        else:
            return None


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
        print("\nList of scooters with brand and model:")
        for s in scooters:
            print(f"{i}. : {s[1]} {s[2]}")
            i += 1

        print("\n \n \n1. Choose Scooter")
        print("2. Go back")
        choice = input("Select an option: ").strip()

        if choice == "1":
            scooter_id = input("Enter scooter ID: ").strip()
            foundScooter = _search_scooter("id", scooter_id)
            if foundScooter is None:
                print("[ERROR] Scooter not found")
                break
            printScooter(foundScooter)
            while True:
                print("\n=== What would you like to update ===")
                print("1. Brand")
                print("2. Model")
                print("3. Serial Number")
                print("4. Top Speed")
                print("5. Batery Capacity")
                print("6. State of Charge")
                print("7. Target Range SoC")
                print("8. Location (lat,long)")
                print("9. Out of Service")
                print("10. Mileage")
                print("11. Last Maintenance Date")
                print("12. Service Date")
                print("13. Done")

                choice2 = input("Select an option: ").strip()
                newBrand = foundScooter[1]
                newModel = foundScooter[2]
                newSerialNumber = foundScooter[3]
                newTS = foundScooter[4]
                newBC = foundScooter[5]
                newSoC = foundScooter[6]
                newLowPer = foundScooter[7]
                newHighPer = foundScooter[8]
                newLat = foundScooter[9]
                newLong = foundScooter[10]
                newOS = foundScooter[11]
                newM = foundScooter[12]
                newMD = foundScooter[13]
                newISD = foundScooter[14]

                match choice2:
                    case "1":
                        print("Update brand")
                        newBrand = input("Enter new brand: ").strip()
                    case "2":
                        print("Update model")
                        newModel = input("Enter new model: ").strip()
                    case "3":
                        print("Update serialnumber")
                        newSerialNumber = input("Enter new serialnumber: ").strip()
                    case "4":
                        print("Update top speed")
                        newTS = input("Enter new top speed: ").strip()
                    case "5":
                        print("Update battery capacity")
                        newBC = input("Enter new battery capacity: ").strip()
                    case "6":
                        print("Update state of charge")
                        newSoC = input("Enter new state of charge: ").strip()
                    case "7":
                        print("Update target range SoC")
                        newLowPer = input("Enter new target range SoC (low)%: ").strip()
                        newHighPer = input(
                            "Enter new target range SoC (high)%: "
                        ).strip()
                    case "8":
                        print("Update location")
                        newLong = input("Enter new location (long): ").strip()
                        newLat = input("Enter new location (lat): ").strip()
                    case "9":
                        print("Update out-of-service status")
                        newOS = input("Enter new out-of-service status: ").strip()
                    case "10":
                        print("Update mileage")
                        newM = input("Enter new mileage: ").strip()
                    case "11":
                        print("Update last maintenance date")
                        newMD = input("Enter new last maintenance date: ").strip()
                    case "12":
                        print("Update In service date")
                        newISD = input("Enter new in service date: ").strip()
                    case "13":
                        print("Finished updating.")
                        break
                    case _:
                        print("[ERROR] Invalid choice.")
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE scooters
                        SET brand=?, model=?, serial_number=?, top_speed=?, battery_capacity=?,
                            soc=?, target_range_min=?, target_range_max=?, latitude=?, longitude=?,
                            out_of_service=?, mileage=?, last_maintenance=?, in_service_date=?
                        WHERE id=?
                    """,
                        (
                            newBrand,
                            newModel,
                            newSerialNumber,
                            newTS,
                            newBC,
                            newSoC,
                            newLowPer,
                            newHighPer,
                            newLat,
                            newLong,
                            newOS,
                            newM,
                            newMD,
                            newISD,
                            foundScooter[0],
                        ),
                    )
                    conn.commit()

        elif choice == "2":
            print("Going back to dashboard")
            break
        else:
            print("[ERROR] Invalid choice.")
