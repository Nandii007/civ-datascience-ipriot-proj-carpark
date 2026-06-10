"""
carpark_manager.py - Manages the state of a carpark.

Implements CarparkSensorListener (responds to car entry/exit/temperature events)
and CarparkDataProvider (exposes data for the display).

Part of the SmartPark IoT Carpark Application.
"""
import os
import time
import logging
from pathlib import Path



from interfaces import CarparkSensorListener, CarparkDataProvider
from car import Car
from config_parser import parse_config

# Configure module-level logger
logger = logging.getLogger(__name__)


class CarparkManager(CarparkSensorListener, CarparkDataProvider):
    """Manages carpark state and responds to sensor events.

    Inherits from CarparkSensorListener to handle incoming sensor events and
    from CarparkDataProvider to supply live data to the display.

    Attributes
    ----------
    location : str
        Human-readable location name of the carpark.
    total_spaces : int
        Total number of bays in the carpark.
    _available_spaces : int
        Current number of free bays (never below zero).
    _temperature : float
        Most recent temperature reading in degrees Celsius.
    _parked_cars : dict
        Mapping of license_plate -> Car for all currently parked cars.
    _log_file : Path
        Path to the activity log file.
    """

    DEFAULT_LOG_FILE = Path("carpark_log.txt")

    def __init__(self, config_file: str = None):
        """Initialise the CarparkManager from a configuration file.

        Parameters
        ----------
        config_file : str
            Path to the JSON configuration file.
        """
        if config_file is None:
            config_file = os.path.join(
                os.path.dirname(__file__), "..", "config.json"
            )

        config = parse_config(config_file)

        self.location = config.get("location", "Unknown")
        self.total_spaces = int(config.get("total-spaces", 0))
        self._available_spaces = self.total_spaces
        self._temperature = 0.0
        self._parked_cars = {}

        self._log_file = self.DEFAULT_LOG_FILE
        self._setup_logging()

        self._log_event(
            f"CarparkManager initialised - location: {self.location}, "
            f"total spaces: {self.total_spaces}"
        )
    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _setup_logging(self) -> None:
        """Configure file-based logging for the manager."""
        file_handler = logging.FileHandler(self._log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s  %(levelname)-8s  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)

    def _log_event(self, message: str) -> None:
        """Write an event message to the activity log.

        Parameters
        ----------
        message : str
            The message to record.
        """
        logger.info(message)

    def _recalculate_spaces(self) -> None:
        """Recalculate available spaces based on the number of parked cars."""
        occupied = len(self._parked_cars)
        self._available_spaces = max(0, self.total_spaces - occupied)

    # ------------------------------------------------------------------
    # CarparkDataProvider properties
    # ------------------------------------------------------------------

    @property
    def available_spaces(self) -> int:
        """Return the number of currently available parking bays."""
        return self._available_spaces

    @property
    def temperature(self) -> float:
        """Return the most recent temperature reading."""
        return self._temperature

    @property
    def current_time(self) -> time.struct_time:
        """Return the current local time as a struct_time."""
        return time.localtime()

    # ------------------------------------------------------------------
    # CarparkSensorListener methods
    # ------------------------------------------------------------------

    def incoming_car(self, license_plate: str) -> None:
        """Handle a car entering the carpark.

        Ignores duplicate plates and refuses entry when the carpark is full.

        Parameters
        ----------
        license_plate : str
            The license plate of the entering car.
        """
        if license_plate in self._parked_cars:
            self._log_event(
                f"IGNORED duplicate entry for plate {license_plate!r}"
            )
            return

        if self._available_spaces <= 0:
            self._log_event(
                f"FULL — refused entry for plate {license_plate!r}"
            )
            return

        car = Car(license_plate)
        self._parked_cars[license_plate] = car
        self._recalculate_spaces()
        self._log_event(
            f"CAR IN  plate={license_plate!r}  "
            f"available={self._available_spaces}/{self.total_spaces}"
        )

    def outgoing_car(self, license_plate: str) -> None:
        """Handle a car leaving the carpark.

        Unrecognised plates do not free a parking space.

        Parameters
        ----------
        license_plate : str
            The license plate of the departing car.
        """
        if license_plate not in self._parked_cars:
            self._log_event(
                f"IGNORED unknown plate {license_plate!r} on exit"
            )
            return

        car = self._parked_cars.pop(license_plate)
        car.record_exit()
        self._recalculate_spaces()
        self._log_event(
            f"CAR OUT plate={license_plate!r}  "
            f"available={self._available_spaces}/{self.total_spaces}"
        )

    def temperature_reading(self, reading: float) -> None:
        """Handle a new temperature reading from the sensor.

        Parameters
        ----------
        reading : float
            Temperature in degrees Celsius.
        """
        self._temperature = reading
        self._log_event(f"TEMP    {reading}°C")
