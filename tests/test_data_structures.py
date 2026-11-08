"""
Unit tests for Custom Data Structures: Stack, Queue, and Singly Linked List (PowerGrid).
Validates operations, edge conditions, underflows, and game mechanic integration.
"""

import unittest
from omni.structures.stack import Stack
from omni.structures.queue import Queue
from omni.structures.linked_list import SinglyLinkedList, PowerGrid, PowerRelay
from omni.core.exceptions import DataStructureUnderflowError
from omni.core.player import Player


class TestDataStructures(unittest.TestCase):
    """Verifies that all custom data structures operate with exact algorithmic correctness."""

    # --- STACK TESTS ---
    def test_stack_push_pop_lifo(self):
        stack = Stack()
        self.assertTrue(stack.is_empty())
        self.assertEqual(stack.size(), 0)

        stack.push("cryo_bay")
        stack.push("corridor")
        stack.push("engineering")

        self.assertEqual(stack.size(), 3)
        self.assertEqual(stack.peek(), "engineering")

        # LIFO check
        self.assertEqual(stack.pop(), "engineering")
        self.assertEqual(stack.pop(), "corridor")
        self.assertEqual(stack.pop(), "cryo_bay")
        self.assertTrue(stack.is_empty())

    def test_stack_underflow(self):
        stack = Stack()
        with self.assertRaises(DataStructureUnderflowError):
            stack.pop()

    def test_player_flee_using_movement_stack(self):
        player = Player("Tester", starting_room_id="cryo_bay")
        player.record_movement("cryo_bay")
        player.current_room_id = "corridor"

        player.record_movement("corridor")
        player.current_room_id = "quarantine"

        # Fleeing retreats to corridor (LIFO)
        retreated = player.flee()
        self.assertEqual(retreated, "corridor")
        self.assertEqual(player.current_room_id, "corridor")

        # Fleeing again retreats to cryo_bay
        retreated_again = player.flee()
        self.assertEqual(retreated_again, "cryo_bay")
        self.assertEqual(player.current_room_id, "cryo_bay")

        # Stack now empty
        self.assertIsNone(player.flee())

    # --- QUEUE TESTS ---
    def test_queue_enqueue_dequeue_fifo(self):
        queue = Queue()
        self.assertTrue(queue.is_empty())
        self.assertEqual(queue.size(), 0)

        queue.enqueue("Threat_A")
        queue.enqueue("Threat_B")
        queue.enqueue("Threat_C")

        self.assertEqual(queue.size(), 3)
        self.assertEqual(queue.peek(), "Threat_A")

        # FIFO check
        self.assertEqual(queue.dequeue(), "Threat_A")
        self.assertEqual(queue.dequeue(), "Threat_B")
        self.assertEqual(queue.dequeue(), "Threat_C")
        self.assertTrue(queue.is_empty())

    def test_queue_underflow(self):
        queue = Queue()
        with self.assertRaises(DataStructureUnderflowError):
            queue.dequeue()

    # --- LINKED LIST & POWER GRID TESTS ---
    def test_singly_linked_list_operations(self):
        sll = SinglyLinkedList()
        self.assertTrue(sll.is_empty())

        sll.append("Relay_1")
        sll.append("Relay_2")
        sll.prepend("Relay_0")

        # Expected: Relay_0 -> Relay_1 -> Relay_2
        self.assertEqual(sll.to_list(), ["Relay_0", "Relay_1", "Relay_2"])
        self.assertEqual(sll.size(), 3)

        # Insertion
        inserted = sll.insert_after("Relay_1", "Relay_1.5")
        self.assertTrue(inserted)
        self.assertEqual(sll.to_list(), ["Relay_0", "Relay_1", "Relay_1.5", "Relay_2"])

        # Deletion
        deleted = sll.delete("Relay_1.5")
        self.assertEqual(deleted, "Relay_1.5")
        self.assertEqual(sll.to_list(), ["Relay_0", "Relay_1", "Relay_2"])

        # Delete head
        deleted_head = sll.delete("Relay_0")
        self.assertEqual(deleted_head, "Relay_0")
        self.assertEqual(sll.to_list(), ["Relay_1", "Relay_2"])

    def test_power_grid_continuity_logic(self):
        grid = PowerGrid()
        r1 = PowerRelay("R1", "Generator", "Reactor", is_online=True, is_damaged=False)
        r2 = PowerRelay("R2", "Bus", "Engineering", is_online=True, is_damaged=True)  # Damaged!
        r3 = PowerRelay("R3", "Pod Switch", "Escape", is_online=True, is_damaged=False)

        grid.append(r1)
        grid.append(r2)
        grid.append(r3)

        # Circuit should NOT be complete because R2 is damaged
        self.assertFalse(grid.is_circuit_complete())
        self.assertEqual(grid.get_broken_relay().relay_id, "R2")

        # Repair R2
        r2.repair()
        self.assertFalse(r2.is_damaged)
        self.assertTrue(r2.is_online)

        # Circuit should now be complete!
        self.assertTrue(grid.is_circuit_complete())
        self.assertIsNone(grid.get_broken_relay())


if __name__ == "__main__":
    unittest.main()

