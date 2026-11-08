"""
Unit tests for Searching (Linear, Binary) and Sorting (Bubble, Insertion, Selection) algorithms.
"""

import unittest
from omni.entities.item import Item
from omni.algorithms.search import linear_search, binary_search, find_item_in_inventory
from omni.algorithms.sort import bubble_sort, insertion_sort, selection_sort


class TestAlgorithms(unittest.TestCase):
    """Verifies that search and sort algorithms function properly on inventory collections."""

    def setUp(self):
        self.item_a = Item("i1", "Alpha Keycard", "Key", weight=0.2, value=10)
        self.item_b = Item("i2", "Heavy Battery", "Battery", weight=5.5, value=50)
        self.item_c = Item("i3", "Medkit", "Medical", weight=1.0, value=30)
        self.item_d = Item("i4", "Prybar", "Tool", weight=2.5, value=20)
        self.items = [self.item_a, self.item_b, self.item_c, self.item_d]

    # --- SEARCH TESTS ---
    def test_linear_search(self):
        # Successful search (case-insensitive)
        idx = linear_search(self.items, "medkit", key_fn=lambda x: x.name)
        self.assertEqual(idx, 2)
        self.assertEqual(self.items[idx].name, "Medkit")

        # Not found
        idx_none = linear_search(self.items, "Plasma Rifle", key_fn=lambda x: x.name)
        self.assertIsNone(idx_none)

    def test_binary_search(self):
        # Alphabetically sorted list by name
        sorted_by_name = sorted(self.items, key=lambda x: x.name.lower())
        # Names: "Alpha Keycard", "Heavy Battery", "Medkit", "Prybar"

        idx = binary_search(sorted_by_name, "Heavy Battery", key_fn=lambda x: x.name)
        self.assertEqual(idx, 1)

        idx_found = binary_search(sorted_by_name, "Prybar", key_fn=lambda x: x.name)
        self.assertEqual(idx_found, 3)

        idx_not_found = binary_search(sorted_by_name, "Nonexistent Item", key_fn=lambda x: x.name)
        self.assertIsNone(idx_not_found)

    # --- SORT TESTS ---
    def test_bubble_sort_by_weight(self):
        sorted_asc = bubble_sort(self.items, key="weight", reverse=False)
        weights_asc = [x.weight for x in sorted_asc]
        self.assertEqual(weights_asc, [0.2, 1.0, 2.5, 5.5])

        sorted_desc = bubble_sort(self.items, key="weight", reverse=True)
        weights_desc = [x.weight for x in sorted_desc]
        self.assertEqual(weights_desc, [5.5, 2.5, 1.0, 0.2])

    def test_insertion_sort_by_value(self):
        sorted_val = insertion_sort(self.items, key="value", reverse=True)
        values = [x.value for x in sorted_val]
        self.assertEqual(values, [50, 30, 20, 10])

    def test_selection_sort_by_weight(self):
        sorted_sel = selection_sort(self.items, key="weight", reverse=False)
        weights = [x.weight for x in sorted_sel]
        self.assertEqual(weights, [0.2, 1.0, 2.5, 5.5])


if __name__ == "__main__":
    unittest.main()

