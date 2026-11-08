"""
Unit tests for custom domain-specific exceptions.
Ensures TemperatureCriticalError, DoorJammedException, PowerGridFailureError,
and InventoryCapacityExceededError carry expected payloads and are handled cleanly.
"""

import unittest
from omni.core.exceptions import (
    OMNIError,
    TemperatureCriticalError,
    DoorJammedException,
    PowerGridFailureError,
    InventoryCapacityExceededError,
)
from omni.entities.room import Room


class TestExceptions(unittest.TestCase):
    """Verifies custom exception behavior and contextual data."""

    def test_temperature_critical_error_attributes(self):
        err = TemperatureCriticalError("Reactor containment failure!", current_temp=98.5, threshold=70.0)
        self.assertIsInstance(err, OMNIError)
        self.assertEqual(err.current_temp, 98.5)
        self.assertEqual(err.threshold, 70.0)
        self.assertEqual(err.severity, "CRITICAL")
        self.assertIn("Reactor containment failure!", str(err))

    def test_door_jammed_exception_on_room_entry(self):
        room = Room("reactor_sec", "Reactor Deck", "High heat area.", is_door_jammed=True)
        # Checking entry on a jammed room should raise DoorJammedException
        with self.assertRaises(DoorJammedException) as ctx:
            room.check_entry_permitted(None)
        self.assertEqual(ctx.exception.door_id, "reactor_sec")
        self.assertIn("jammed", ctx.exception.message)

    def test_power_grid_failure_error(self):
        err = PowerGridFailureError("Launch Solenoid disconnected", relay_name="Pod Relay")
        self.assertIsInstance(err, OMNIError)
        self.assertEqual(err.relay_name, "Pod Relay")

    def test_inventory_capacity_exceeded_error_attributes(self):
        err = InventoryCapacityExceededError("Too heavy", current_weight=12.0, item_weight=4.0, max_weight=15.0)
        self.assertEqual(err.current_weight, 12.0)
        self.assertEqual(err.item_weight, 4.0)
        self.assertEqual(err.max_weight, 15.0)


if __name__ == "__main__":
    unittest.main()

