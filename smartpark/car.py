"""
car.py - Represents a vehicle that enters or exits the carpark.

Part of the SmartPark IoT Carpark Application.
"""

import time


class Car:
    """Represents a car in the carpark system.

    Attributes
    ----------
    license_plate : str
        The car's license plate identifier.
    entry_time : float
        Unix timestamp when the car entered.
    exit_time : float or None
        Unix timestamp when the car exited, or None if still parked.
    """

    def __init__(self, license_plate: str):
        """Initialise a Car with its license plate and record entry time.

        Parameters
        ----------
        license_plate : str
            The license plate number of the car.
        """
        self.license_plate = license_plate
        self.entry_time: float = time.time()
        self.exit_time = None

    def record_exit(self) -> None:
        """Record the time the car exited the carpark."""
        self.exit_time = time.time()

    @property
    def is_parked(self) -> bool:
        """Return True if the car is still in the carpark."""
        return self.exit_time is None

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        status = "parked" if self.is_parked else "departed"
        return f"Car(plate={self.license_plate!r}, status={status})"
