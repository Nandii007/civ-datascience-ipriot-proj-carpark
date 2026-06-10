"""
config_parser.py - Reads and parses the carpark JSON configuration file.

Part of the SmartPark IoT Carpark Application.
"""

import json


def parse_config(config_file: str) -> dict:
    """Parse a JSON configuration file and return the first carpark's settings.

    The expected format is::

        {
            "CarParks": [
                {
                    "name": "...",
                    "total-spaces": 130,
                    "total-cars": 0,
                    "location": "...",
                    ...
                }
            ]
        }

    Parameters
    ----------
    config_file : str
        Path to the JSON configuration file.

    Returns
    -------
    dict
        A dictionary containing the configuration for the first carpark entry.

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist at the given path.
    KeyError
        If the JSON structure does not contain a "CarParks" key.
    """
    with open(config_file, "r", encoding="utf-8") as input_file:
        data = json.load(input_file)
    return data["CarParks"][0]


if __name__ == "__main__":
    cfg = parse_config("config.json")
    print(cfg)
