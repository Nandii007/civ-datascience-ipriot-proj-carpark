"""
test_carpark_manager.py - Unit tests for CarparkManager.

Tests cover the main behaviours described in the requirements:
  - Available spaces decrement on entry
  - Available spaces increment on exit
  - Available spaces never go below zero
  - Unrecognised plates do not free a space
  - Duplicate entry does not consume an extra space
  - Temperature is recorded correctly

Run with:
    python -m unittest discover tests -v

Part of the SmartPark IoT Carpark Application.
"""

import sys
import os
import unittest

# Make the smartpark package importable from the tests folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from smartpark.carpark_manager import CarparkManager

# Path to config used by all tests
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "smartpark", "config.json")


class TestCarparkManagerInitialState(unittest.TestCase):
    """Tests that verify the initial state after reading config."""

    def setUp(self):
        """Create a fresh CarparkManager before each test."""
        self.manager = CarparkManager(config_file=CONFIG_PATH)

    def test_initial_available_spaces_equals_total_spaces(self):
        """Available spaces should equal total spaces when no cars are present.

        Relates to User Story 1: drivers need an accurate count of free bays.
        """
        self.assertEqual(
            self.manager.available_spaces, self.manager.total_spaces
        )

    def test_initial_temperature_is_zero(self):
        """Temperature should default to 0.0 before any reading is received."""
        self.assertEqual(self.manager.temperature, 0.0)


class TestCarparkManagerIncomingCar(unittest.TestCase):
    """Tests for the incoming_car method."""

    def setUp(self):
        self.manager = CarparkManager(config_file=CONFIG_PATH)

    def test_incoming_car_decrements_available_spaces(self):
        """Each unique entering car should reduce available spaces by one.

        Relates to Backlog Item 1: accurately count cars entering the lot.
        """
        initial = self.manager.available_spaces
        self.manager.incoming_car("1ABC123")
        self.assertEqual(self.manager.available_spaces, initial - 1)

    def test_duplicate_plate_does_not_consume_extra_space(self):
        """A plate already parked should not claim a second bay.

        Relates to Backlog Item 4: proper data handling and error prevention.
        """
        self.manager.incoming_car("1ABC123")
        spaces_after_first = self.manager.available_spaces
        self.manager.incoming_car("1ABC123")
        self.assertEqual(self.manager.available_spaces, spaces_after_first)

    def test_full_carpark_refuses_entry(self):
        """Available spaces must not go below zero.

        Relates to Non-Functional Requirement 5: handle edge case of a full lot.
        """
        for i in range(self.manager.total_spaces):
            self.manager.incoming_car(f"PLATE{i:04d}")
        self.assertEqual(self.manager.available_spaces, 0)
        self.manager.incoming_car("OVERFLOW")
        self.assertEqual(self.manager.available_spaces, 0)


class TestCarparkManagerOutgoingCar(unittest.TestCase):
    """Tests for the outgoing_car method."""

    def setUp(self):
        self.manager = CarparkManager(config_file=CONFIG_PATH)

    def test_outgoing_car_increments_available_spaces(self):
        """A recognised car leaving should free exactly one bay.

        Relates to Backlog Item 1: accurately count cars leaving the lot.
        """
        self.manager.incoming_car("2XYZ456")
        spaces_after_entry = self.manager.available_spaces
        self.manager.outgoing_car("2XYZ456")
        self.assertEqual(self.manager.available_spaces, spaces_after_entry + 1)

    def test_unknown_plate_on_exit_does_not_change_spaces(self):
        """An unrecognised plate on exit must not free a space.

        Relates to Backlog Item 4: unrecognised cars should not free a space.
        """
        spaces_before = self.manager.available_spaces
        self.manager.outgoing_car("UNKNOWN_PLATE")
        self.assertEqual(self.manager.available_spaces, spaces_before)

    def test_available_spaces_never_exceed_total(self):
        """Spaces must never exceed total after excess exits.

        Relates to Non-Functional Requirement 5: handle edge cases.
        """
        self.manager.incoming_car("3DEF789")
        self.manager.outgoing_car("3DEF789")
        self.manager.outgoing_car("3DEF789")  # second exit — ignored
        self.assertLessEqual(
            self.manager.available_spaces, self.manager.total_spaces
        )


class TestCarparkManagerTemperature(unittest.TestCase):
    """Tests for the temperature_reading method."""

    def setUp(self):
        self.manager = CarparkManager(config_file=CONFIG_PATH)

    def test_temperature_reading_updates_value(self):
        """A temperature reading must update the stored temperature.

        Relates to User Story 2: display current temperature.
        """
        self.manager.temperature_reading(25.5)
        self.assertEqual(self.manager.temperature, 25.5)

    def test_temperature_reading_negative_value(self):
        """Negative temperatures should be stored correctly."""
        self.manager.temperature_reading(-3.0)
        self.assertEqual(self.manager.temperature, -3.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
