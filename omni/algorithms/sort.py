"""
Algorithmic sorting routines for O.M.N.I.
Provides custom Bubble Sort, Insertion Sort, and Selection Sort implementations
for ordering inventory items by weight, value, or name.
"""

from typing import Any, Callable, List, Optional


def _extract_key(item: Any, key_name: str, key_fn: Optional[Callable[[Any], Any]] = None) -> Any:
    """Helper to extract comparison key from an item."""
    if key_fn is not None:
        return key_fn(item)
    if hasattr(item, key_name):
        return getattr(item, key_name)
    if isinstance(item, dict) and key_name in item:
        return item[key_name]
    return item


def bubble_sort(items: List[Any], key: str = "weight", reverse: bool = False, in_place: bool = False) -> List[Any]:
    """
    Performs Bubble Sort on a list of items with early termination flag.
    Time Complexity: O(n^2) worst/average, O(n) best.
    Space Complexity: O(1) in-place, O(n) if returning a copy.

    :param items: List of items to sort.
    :param key: Attribute name to sort by ('weight', 'value', 'name').
    :param reverse: If True, sorts descending; otherwise ascending.
    :param in_place: If True, modifies items in-place; otherwise returns sorted copy.
    :return: The sorted list.
    """
    arr = items if in_place else list(items)
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            val_a = _extract_key(arr[j], key)
            val_b = _extract_key(arr[j + 1], key)

            condition = (val_a < val_b) if reverse else (val_a > val_b)
            if condition:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr


def insertion_sort(items: List[Any], key: str = "weight", reverse: bool = False, in_place: bool = False) -> List[Any]:
    """
    Performs Insertion Sort on a list of items.
    Time Complexity: O(n^2) worst/average, O(n) best.
    Space Complexity: O(1) in-place.

    :param items: List of items to sort.
    :param key: Attribute name to sort by ('weight', 'value', 'name').
    :param reverse: If True, sorts descending; otherwise ascending.
    :param in_place: If True, modifies items in-place; otherwise returns sorted copy.
    :return: The sorted list.
    """
    arr = items if in_place else list(items)
    for i in range(1, len(arr)):
        current_item = arr[i]
        current_val = _extract_key(current_item, key)
        j = i - 1

        while j >= 0:
            compare_val = _extract_key(arr[j], key)
            condition = (compare_val < current_val) if reverse else (compare_val > current_val)
            if condition:
                arr[j + 1] = arr[j]
                j -= 1
            else:
                break
        arr[j + 1] = current_item
    return arr


def selection_sort(items: List[Any], key: str = "weight", reverse: bool = False, in_place: bool = False) -> List[Any]:
    """
    Performs Selection Sort on a list of items.
    Time Complexity: O(n^2).
    Space Complexity: O(1) in-place.
    """
    arr = items if in_place else list(items)
    n = len(arr)
    for i in range(n):
        target_idx = i
        for j in range(i + 1, n):
            val_j = _extract_key(arr[j], key)
            val_target = _extract_key(arr[target_idx], key)
            condition = (val_j > val_target) if reverse else (val_j < val_target)
            if condition:
                target_idx = j
        if target_idx != i:
            arr[i], arr[target_idx] = arr[target_idx], arr[i]
    return arr

