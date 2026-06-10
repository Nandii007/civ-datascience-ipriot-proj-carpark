"""
no_pi.py - Tkinter UI for the SmartPark application.

Provides a simulated car detector window and a display window for students
who do not have a Raspberry Pi / SenseHAT.

Run this file directly to start the application::

    python no_pi.py

Part of the SmartPark IoT Carpark Application.
"""

import os
import threading
import time
import tkinter as tk
from typing import Iterable

from interfaces import CarparkSensorListener, CarparkDataProvider
from carpark_manager import CarparkManager


# ---------------------------------------------------------------------------
# WindowedDisplay — provided infrastructure, do not modify
# ---------------------------------------------------------------------------

class WindowedDisplay:
    """Displays values for a given set of fields as a simple GUI window.

    Use .show() to display the window and .update() to refresh values.
    """

    DISPLAY_INIT = '– – –'
    SEP = ':'

    def __init__(self, root, title: str, display_fields: Iterable[str]):
        """Initialise the windowed display.

        Parameters
        ----------
        root :
            The parent tkinter root window.
        title : str
            Window title (usually the carpark name from config).
        display_fields : Iterable[str]
            Labels for each row of the display.
        """
        self.window = tk.Toplevel(root)
        self.window.title(f'{title}: Parking')
        self.window.geometry('800x400')
        self.window.resizable(False, False)
        self.display_fields = display_fields

        self.gui_elements = {}
        for i, field in enumerate(self.display_fields):
            self.gui_elements[f'lbl_field_{i}'] = tk.Label(
                self.window, text=field + self.SEP, font=('Arial', 50))
            self.gui_elements[f'lbl_value_{i}'] = tk.Label(
                self.window, text=self.DISPLAY_INIT, font=('Arial', 50))

            self.gui_elements[f'lbl_field_{i}'].grid(
                row=i, column=0, sticky=tk.E, padx=5, pady=5)
            self.gui_elements[f'lbl_value_{i}'].grid(
                row=i, column=2, sticky=tk.W, padx=10)

    def show(self) -> None:
        """Display the GUI (non-blocking)."""

    def update(self, updated_values: dict) -> None:
        """Update the displayed values.

        Parameters
        ----------
        updated_values : dict
            Keys must match the field names passed to the constructor.
        """
        for field in self.gui_elements:
            if field.startswith('lbl_field'):
                field_value = field.replace('field', 'value')
                self.gui_elements[field_value].configure(
                    text=updated_values[
                        self.gui_elements[field].cget('text').rstrip(self.SEP)
                    ]
                )
        self.window.update()


# ---------------------------------------------------------------------------
# CarParkDisplay — student implementation
# ---------------------------------------------------------------------------

class CarParkDisplay:
    """Shows live carpark data (available bays, temperature, time) in a window.

    Reads from a CarparkDataProvider and refreshes the display every second
    via a background thread.
    """

    fields = ['Available bays', 'Temperature', 'At']

    def __init__(self, root, title: str = 'Moondalup'):
        """Initialise the display window and start the background updater.

        Parameters
        ----------
        root :
            Parent tkinter root window.
        title : str
            Title shown in the window bar.
        """
        self.window = WindowedDisplay(root, title, CarParkDisplay.fields)
        self._provider = None

        updater = threading.Thread(target=self._check_updates, daemon=True)
        updater.start()
        self.window.show()

    @property
    def data_provider(self):
        """The CarparkDataProvider supplying display data."""
        return self._provider

    @data_provider.setter
    def data_provider(self, provider):
        """Set the data provider if it implements CarparkDataProvider."""
        if isinstance(provider, CarparkDataProvider):
            self._provider = provider

    def _update_display(self) -> None:
        """Push the latest values from the provider into the window."""
        spaces = self._provider.available_spaces
        # Show FULL in red text when no spaces remain
        bay_label = f'{spaces:03d}' if spaces > 0 else 'FULL'
        field_values = dict(zip(CarParkDisplay.fields, [
            bay_label,
            f'{self._provider.temperature:.1f}\u2103',
            time.strftime("%H:%M:%S", self._provider.current_time),
        ]))
        self.window.update(field_values)

    def _check_updates(self) -> None:
        """Background thread: refresh the display once per second."""
        while True:
            time.sleep(1)
            if self._provider is not None:
                self._update_display()


# ---------------------------------------------------------------------------
# CarDetectorWindow — student implementation
# ---------------------------------------------------------------------------

class CarDetectorWindow:
    """Tkinter window that simulates car-entry and car-exit sensor events."""

    def __init__(self, root):
        """Initialise the detector window with buttons and input fields.

        Parameters
        ----------
        root :
            Parent tkinter root window.
        """
        self.root = root
        self.root.title("Car Detector ULTRA")
        self.listeners = []

        # Car entry button
        self.btn_incoming_car = tk.Button(
            self.root, text='\U0001f698 Incoming Car',
            font=('Arial', 50), cursor='right_side',
            command=self._incoming_car,
        )
        self.btn_incoming_car.grid(padx=10, pady=5, row=0, columnspan=2)

        # Car exit button
        self.btn_outgoing_car = tk.Button(
            self.root, text='Outgoing Car \U0001f698',
            font=('Arial', 50), cursor='bottom_left_corner',
            command=self._outgoing_car,
        )
        self.btn_outgoing_car.grid(padx=10, pady=5, row=1, columnspan=2)

        # Temperature input
        tk.Label(self.root, text="Temperature",
                 font=('Arial', 20)).grid(padx=10, pady=5, column=0, row=2)
        self.temp_var = tk.StringVar()
        self.temp_var.trace_add(
            "write", lambda x, y, v: self._temperature_changed())
        tk.Entry(self.root, font=('Arial', 20),
                 textvariable=self.temp_var).grid(
            padx=10, pady=5, column=1, row=2)

        # License plate input
        tk.Label(self.root, text="License Plate",
                 font=('Arial', 20)).grid(padx=10, pady=5, column=0, row=3)
        self.plate_var = tk.StringVar()
        tk.Entry(self.root, font=('Arial', 20),
                 textvariable=self.plate_var).grid(
            padx=10, pady=5, column=1, row=3)

    @property
    def current_license(self) -> str:
        """Return the license plate currently typed in the input field."""
        return self.plate_var.get()

    def add_listener(self, listener) -> None:
        """Register an object to receive sensor event callbacks.

        Parameters
        ----------
        listener : CarparkSensorListener
            Object with incoming_car, outgoing_car, temperature_reading methods.
        """
        if isinstance(listener, CarparkSensorListener):
            self.listeners.append(listener)

    def _incoming_car(self) -> None:
        """Fire the incoming_car event on all registered listeners."""
        for listener in self.listeners:
            listener.incoming_car(self.current_license)

    def _outgoing_car(self) -> None:
        """Fire the outgoing_car event on all registered listeners."""
        for listener in self.listeners:
            listener.outgoing_car(self.current_license)

    def _temperature_changed(self) -> None:
        """Fire the temperature_reading event when the input field changes."""
        try:
            temp = float(self.temp_var.get())
        except ValueError:
            return
        for listener in self.listeners:
            listener.temperature_reading(temp)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    root = tk.Tk()

    # Load real CarparkManager from config
    manager = CarparkManager(
        config_file=os.path.join(os.path.dirname(__file__), "config.json")
    )

    # Set up the display and wire it to the manager
    display = CarParkDisplay(root, title=manager.location.title())
    display.data_provider = manager

    # Set up the detector and wire it to the manager
    detector = CarDetectorWindow(root)
    detector.add_listener(manager)

    root.mainloop()
