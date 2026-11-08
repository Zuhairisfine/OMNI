"""
Algorithmic searching routines for O.M.N.I.
Provides linear and binary search implementations for item and entity lookups.
"""

from typing import Any, Callable, List, Optional


def linear_search(items: List[Any], target: str, key_fn: Optional[Callable[[Any], str]] = None) -> Optional[int]:
    """
    Performs Linear Search across a list of items.
    Time Complexity: O(n)
    Space Complexity: O(1)

    :param items: List of items to search.
    :param target: Target identifier or name string (case-insensitive).
    :param key_fn: Optional function to extract comparison key from item.
    :return: Index of target if found, else None.
    """
    target_clean = target.strip().lower()
    for idx, item in enumerate(items):
        item_val = key_fn(item) if key_fn else (getattr(item, "name", str(item)))
        if str(item_val).strip().lower() == target_clean:
            return idx
    return None


def binary_search(sorted_items: List[Any], target: str, key_fn: Optional[Callable[[Any], str]] = None) -> Optional[int]:
    """
    Performs Binary Search across an alphabetically sorted list of items.
    Time Complexity: O(log n)
    Space Complexity: O(1)

    :param sorted_items: Alphabetically sorted list of items.
    :param target: Target identifier or name string (case-insensitive).
    :param key_fn: Optional function to extract comparison key from item.
    :return: Index of target if found, else None.
    """
    low = 0
    high = len(sorted_items) - 1
    target_clean = target.strip().lower()

    while low <= high:
        mid = (low + high) // 2
        item_val = key_fn(sorted_items[mid]) if key_fn else getattr(sorted_items[mid], "name", str(sorted_items[mid]))
        mid_val = str(item_val).strip().lower()

        if mid_val == target_clean:
            return mid
        elif mid_val < target_clean:
            low = mid + 1
        else:
            high = mid - 1

    return None


def find_item_in_inventory(inventory: List[Any], target_name: str) -> Optional[Any]:
    """
    Helper function to locate an item in the player inventory using linear search.
    :return: The item instance if present, else None.
    """
    idx = linear_search(inventory, target_name, key_fn=lambda x: x.name)
    if idx is not None:
        return inventory[idx]
    return None

