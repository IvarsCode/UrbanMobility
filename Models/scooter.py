from datetime import datetime
import re

class Scooter:
    def __init__(
        self,
        brand: str,
        model: str,
        serialNumber: str,              # 10 to 17 alphanumeric characters
        topSpeed: int,                  # in km/h
        batteryCapacity: int,           # in watt-hours (Wh)
        SoC: float,                     # State of Charge in percentage
        targetRangeSoC: list[float],    # [min, max] SoC in percentage
        location: list[float],          # [latitude, longitude]
        outOfService: bool,             # True/False
        mileage: float,                 # in kilometers
        lastMaintenanceDate: str        # ISO 8601 format: YYYY-MM-DD
    ):
        # Validate serial number format
        if not re.fullmatch(r'[A-Za-z0-9]{10,17}', serialNumber):
            raise ValueError("Serial number must be 10 to 17 alphanumeric characters.")

        # Validate location (Rotterdam GPS coordinates range)
        lat, lon = location
        if not (51.85 <= lat <= 51.98 and 4.35 <= lon <= 4.55):
            raise ValueError("Location must be within the Rotterdam region.")

        # Validate location decimal precision
        if round(lat, 5) != lat or round(lon, 5) != lon:
            raise ValueError("Latitude and longitude must be specified to 5 decimal places.")

        # Validate SoC and target SoC range
        if not (0 <= SoC <= 100):
            raise ValueError("State of Charge (SoC) must be between 0 and 100.")
        if not (0 <= targetRangeSoC[0] <= targetRangeSoC[1] <= 100):
            raise ValueError("Target range SoC must be within 0 to 100 and in increasing order.")

        # Validate last maintenance date
        try:
            datetime.strptime(lastMaintenanceDate, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Last maintenance date must be in ISO 8601 format: YYYY-MM-DD")

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