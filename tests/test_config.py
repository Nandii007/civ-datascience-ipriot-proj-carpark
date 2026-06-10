"""
test_config.py - Unit tests for config_parser module.
 
Part of the SmartPark IoT Carpark Application.
"""
 
import unittest
import sys
import os
from pathlib import Path
 
# Add smartpark folder to path so we can import from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "smartpark"))
 
from config_parser import parse_config
 
# Path to the real config.json inside smartpark/
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "smartpark", "config.json")
 
 
class TestConfigParsing(unittest.TestCase):
 
    def test_parse_config_returns_correct_location(self):
        """Config file should return the location field.
 
        Relates to Functional Requirement 3: system must read config from file.
        """
        result = parse_config(CONFIG_PATH)
        self.assertEqual(result['location'], "moondalup")
 
    def test_parse_config_returns_correct_total_spaces(self):
        """Config file should return 130 total spaces as set in config.json."""
        result = parse_config(CONFIG_PATH)
        self.assertEqual(int(result['total-spaces']), 130)
 
    def test_parse_config_has_sensors(self):
        """Config file should contain a Sensors list."""
        result = parse_config(CONFIG_PATH)
        self.assertIn('Sensors', result)
        self.assertIsInstance(result['Sensors'], list)
 
    def test_parse_config_file_not_found(self):
        """Passing a bad path should raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            parse_config("nonexistent.json")
 
 
if __name__ == "__main__":
    unittest.main(verbosity=2)