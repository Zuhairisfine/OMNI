"""
Unit tests for GameObject abstract base class and polymorphic subclasses (Room, Hazard, Item).
"""

import unittest
from omni.core.base import GameObject
from omni.entities.item import Item, MedicalItem, ToolItem, KeycardItem, EnergyCellItem
from omni.entities.hazard import Hazard, RadiationHazard, RogueDroneHazard, FireHazard
from omni.entities.room import Room
from omni.core.player import Player


class TestGameObjects(unittest.TestCase):
    """Verifies abstraction, inheritance, and polymorphism across game entities."""

    def test_game_object_is_abstract(self):
        """Validates that GameObject cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            GameObject("obj_01", "Generic Object", "Description")

    def test_item_hierarchy_and_polymorphism(self):
        """Verifies Item subclasses inherit and implement polymorphic interact() method."""
        player = Player(name="Test Subject")
        medkit = MedicalItem("med_01", "Nanite Stim", "Restores HP", weight=0.5, heal_amount=25)
        tool = ToolItem("tool_01", "Arc Welder", "Industrial tool", weight=2.0, tool_type="WELDER")
        key = KeycardItem("key_01", "Bio-Pass", "Clearance card", clearance_level=2)

        # Ensure all are instances of GameObject and Item
        for entity in [medkit, tool, key]:
            self.assertIsInstance(entity, GameObject)
            self.assertIsInstance(entity, Item)
            # Polymorphic interact() call without type branching
            result = entity.interact(player)
            self.assertIsInstance(result, str)
            self.assertTrue(len(result) > 0)

        # Test medical use restores health
        player.health = 50
        medkit.use(player)
        self.assertEqual(player.health, 75)

    def test_hazard_hierarchy_and_polymorphism(self):
        """Verifies Hazard subclasses inherit and implement polymorphic interact() method."""
        player = Player(name="Test Subject")
        player.health = 100

        rad = RadiationHazard("haz_rad", "Gamma Cloud", "Deadly radiation", damage=20)
        drone = RogueDroneHazard("haz_drone", "Sentry Bot", "Combat droid", damage=30)
        fire = FireHazard("haz_fire", "Plasma Jet", "Extreme fire", damage=15, temperature=50.0)

        for entity in [rad, drone, fire]:
            self.assertIsInstance(entity, GameObject)
            self.assertIsInstance(entity, Hazard)

        # Polymorphic interact inflicts damage
        rad.interact(player)
        self.assertEqual(player.health, 80)

        drone.interact(player)
        self.assertEqual(player.health, 50)

    def test_room_hierarchy_and_polymorphism(self):
        """Verifies Room implements interact() and manages items and exits."""
        player = Player(name="Test Subject")
        room = Room("sec_01", "Air Filtration Hub", "Humming ventilation fans.")
        self.assertIsInstance(room, GameObject)

        # Add item and connect exit
        item = Item("filter_01", "Carbon Filter", "Air filter", weight=1.2)
        room.add_item(item)
        room.connect_exit("north", "sec_02")

        # Polymorphic interact returns descriptive string containing item and exit
        narrative = room.interact(player)
        self.assertIn("Carbon Filter", narrative)
        self.assertIn("north", narrative)
        self.assertTrue(room.visited)


if __name__ == "__main__":
    unittest.main()

