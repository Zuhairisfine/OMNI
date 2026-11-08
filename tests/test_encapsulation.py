"""
Unit tests for Encapsulation in Player and MedicalQuarantineBay.
Validates private attributes, @property getters/setters, boundaries, and validation exceptions.
"""

import unittest
from omni.core.player import Player
from omni.entities.room import MedicalQuarantineBay
from omni.entities.item import Item
from omni.core.exceptions import (
    TemperatureCriticalError,
    InventoryCapacityExceededError,
)


class TestEncapsulation(unittest.TestCase):
    """Verifies that private attributes cannot be arbitrarily corrupted and setters enforce validation."""

    def test_player_health_encapsulation(self):
        player = Player("Test")
        # Default health is 100
        self.assertEqual(player.health, 100)

        # Modifying within valid range
        player.health = 75
        self.assertEqual(player.health, 75)

        # Clamping above 100
        player.health = 150
        self.assertEqual(player.health, 100)

        # Clamping below 0
        player.health = -50
        self.assertEqual(player.health, 0)
        self.assertFalse(player.is_alive)

        # Non-numeric type raises TypeError
        with self.assertRaises(TypeError):
            player.health = "full_health"

    def test_player_temperature_encapsulation_and_critical_error(self):
        player = Player("Test")
        self.assertEqual(player.temperature, 37.0)

        # Safe fluctuation
        player.temperature = 38.2
        self.assertEqual(player.temperature, 38.2)

        # Hyperthermia critical threshold (> 42.0°C) raises TemperatureCriticalError
        with self.assertRaises(TemperatureCriticalError) as ctx:
            player.temperature = 43.5
        self.assertEqual(ctx.exception.current_temp, 43.5)
        self.assertEqual(ctx.exception.threshold, 42.0)

        # Hypothermia critical threshold (< 32.0°C) raises TemperatureCriticalError
        with self.assertRaises(TemperatureCriticalError) as ctx:
            player.temperature = 30.0
        self.assertEqual(ctx.exception.current_temp, 30.0)
        self.assertEqual(ctx.exception.threshold, 32.0)

    def test_inventory_capacity_encapsulation(self):
        player = Player("Test", max_carry_weight=10.0)
        item1 = Item("i1", "Lead Plate", "Heavy shield", weight=6.0)
        item2 = Item("i2", "Iron Bar", "Metal bar", weight=3.0)
        item3 = Item("i3", "Concrete Block", "Too heavy", weight=2.0)

        player.add_to_inventory(item1)
        player.add_to_inventory(item2)
        self.assertEqual(player.current_carry_weight, 9.0)

        # Adding item3 would bring weight to 11.0 > 10.0, raising exception
        with self.assertRaises(InventoryCapacityExceededError) as ctx:
            player.add_to_inventory(item3)
        self.assertEqual(ctx.exception.current_weight, 9.0)
        self.assertEqual(ctx.exception.item_weight, 2.0)
        self.assertEqual(ctx.exception.max_weight, 10.0)

    def test_medical_quarantine_bay_encapsulation(self):
        bay = MedicalQuarantineBay(
            obj_id="quarantine_test",
            name="Testing Quarantine Bay",
            description="Testing containment chamber",
            temperature=21.0,
            contamination_level=50.0,
        )

        self.assertEqual(bay.temperature, 21.0)
        self.assertEqual(bay.contamination_level, 50.0)
        self.assertTrue(bay.quarantine_active)

        # Setting unsafe runaway temperature raises TemperatureCriticalError
        with self.assertRaises(TemperatureCriticalError) as ctx:
            bay.temperature = 75.0
        self.assertEqual(ctx.exception.current_temp, 75.0)

        # Setting out-of-bounds contamination percentage raises ValueError
        with self.assertRaises(ValueError):
            bay.contamination_level = 150.0

        # Sanitization cycle reduces contamination and disengages quarantine lock
        bay.sanitize_chamber(50.0)
        self.assertEqual(bay.contamination_level, 0.0)
        self.assertFalse(bay.quarantine_active)


if __name__ == "__main__":
    unittest.main()

