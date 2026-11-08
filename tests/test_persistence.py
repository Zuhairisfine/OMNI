"""
Unit tests for Data Persistence ('Neural Upload' Checkpoint).
Performs a comprehensive save/load round-trip test ensuring exact state restoration.
"""

import os
import unittest
from omni.core.player import Player
from omni.entities.room import Room, MedicalQuarantineBay
from omni.entities.item import Item, ToolItem, MedicalItem
from omni.entities.hazard import Hazard, RogueDroneHazard
from omni.structures.linked_list import PowerGrid, PowerRelay
from omni.structures.queue import Queue
from omni.persistence.neural_upload import NeuralUpload


class TestPersistence(unittest.TestCase):
    """Verifies JSON serialization and deserialization of player and station state."""

    def setUp(self):
        self.test_save_file = "test_neural_checkpoint.json"

    def tearDown(self):
        if os.path.exists(self.test_save_file):
            os.remove(self.test_save_file)

    def test_save_load_round_trip(self):
        """
        Comprehensive round-trip test:
        1. Set up detailed player, rooms, power grid, and threat queue.
        2. Serialize to JSON file.
        3. Restore state from file.
        4. Assert exact equality across all fields and nested structures.
        """
        # 1. Prepare original player state
        player = Player(name="Dr. Vance", starting_room_id="quarantine", max_carry_weight=20.0)
        player.health = 82
        player.oxygen = 94
        player.temperature = 36.8
        player.record_movement("cryo_bay")
        player.record_movement("corridor")

        item1 = MedicalItem("med_01", "Med-Stim", "Healing injector", weight=0.6, value=25, heal_amount=35)
        item2 = ToolItem("tool_01", "Arc Torch", "Welder", weight=2.5, value=75, tool_type="TORCH", charges=4)
        player.add_to_inventory(item1)
        player.add_to_inventory(item2)

        # 2. Prepare rooms
        room1 = Room("corridor", "Central Corridor", "Hub sector", is_locked=False)
        room2 = MedicalQuarantineBay("quarantine", "Quarantine Bay", "Containment", temperature=24.5, contamination_level=18.0)
        room_dict = {
            "corridor": room1.to_dict(),
            "quarantine": room2.to_dict(),
        }

        # 3. Prepare power grid
        grid = PowerGrid()
        grid.append(PowerRelay("RELAY-01", "Core Feed", "Reactor", is_online=True, is_damaged=False))
        grid.append(PowerRelay("RELAY-02", "Bus", "Engineering", is_online=False, is_damaged=True))

        # 4. Prepare threat queue
        threat_queue = Queue()
        threat_queue.enqueue(RogueDroneHazard("drone_01", "Sentinel", "Security bot", damage=25))

        # 5. Save Checkpoint
        saved_path = NeuralUpload.save_checkpoint(
            player_dict=player.to_dict(),
            rooms_dict=room_dict,
            power_grid_list=[r.to_dict() for r in grid],
            threat_queue_list=[h.to_dict() for h in threat_queue],
            turn_count=7,
            filepath=self.test_save_file,
        )
        self.assertTrue(os.path.exists(saved_path))

        # 6. Load Checkpoint
        data = NeuralUpload.load_checkpoint(filepath=self.test_save_file)
        self.assertEqual(data["turn_count"], 7)

        # 7. Reconstruct & Verify Player
        restored_player = Player.from_dict(data["player"])
        self.assertEqual(restored_player.name, "Dr. Vance")
        self.assertEqual(restored_player.health, 82)
        self.assertEqual(restored_player.oxygen, 94)
        self.assertEqual(restored_player.temperature, 36.8)
        self.assertEqual(restored_player.current_room_id, "quarantine")
        self.assertEqual(len(restored_player.inventory), 2)
        self.assertEqual(restored_player.inventory[0].name, "Med-Stim")
        self.assertEqual(restored_player.inventory[1].name, "Arc Torch")
        self.assertEqual(restored_player.inventory[1].charges, 4)

        # Verify movement history stack restored in correct LIFO order
        self.assertEqual(restored_player.flee(), "corridor")
        self.assertEqual(restored_player.flee(), "cryo_bay")
        self.assertIsNone(restored_player.flee())

        # 8. Reconstruct & Verify Rooms
        restored_rooms = {r_id: Room.from_dict(r_d) for r_id, r_d in data["rooms"].items()}
        self.assertIn("corridor", restored_rooms)
        self.assertIn("quarantine", restored_rooms)
        quarantine_restored = restored_rooms["quarantine"]
        self.assertIsInstance(quarantine_restored, MedicalQuarantineBay)
        self.assertEqual(quarantine_restored.temperature, 24.5)
        self.assertEqual(quarantine_restored.contamination_level, 18.0)

        # 9. Reconstruct & Verify Power Grid
        restored_grid = PowerGrid()
        for r_data in data["power_grid"]:
            restored_grid.append(PowerRelay.from_dict(r_data))
        self.assertEqual(restored_grid.size(), 2)
        r1 = restored_grid.find_relay("RELAY-01")
        self.assertTrue(r1.is_online)
        self.assertFalse(r1.is_damaged)
        r2 = restored_grid.find_relay("RELAY-02")
        self.assertFalse(r2.is_online)
        self.assertTrue(r2.is_damaged)

        # 10. Reconstruct & Verify Threat Queue
        restored_queue = Queue()
        for h_data in data["threat_queue"]:
            restored_queue.enqueue(Hazard.from_dict(h_data))
        self.assertEqual(restored_queue.size(), 1)
        dequeued = restored_queue.dequeue()
        self.assertEqual(dequeued.name, "Sentinel")
        self.assertEqual(dequeued.damage, 25)


if __name__ == "__main__":
    unittest.main()

