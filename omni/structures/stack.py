"""
Custom Stack data structure implementation.
Used in O.M.N.I. to track player movement history and facilitate LIFO 'Flee' maneuvers.
"""

from typing import Any, List, Optional
from omni.core.exceptions import DataStructureUnderflowError


class StackNode:
    """Represents an individual node in the linked Stack."""

    def __init__(self, data: Any, next_node: Optional["StackNode"] = None):
        self.data = data
        self.next = next_node

    def __repr__(self) -> str:
        return f"StackNode({self.data!r})"


class Stack:
    """
    Class-based LIFO (Last-In, First-Out) Stack data structure.
    Used for breadcrumb tracking of player navigation and emergency retreats.
    """

    def __init__(self):
        self._top: Optional[StackNode] = None
        self._size: int = 0

    def push(self, item: Any) -> None:
        """Pushes an element onto the top of the stack."""
        new_node = StackNode(item, self._top)
        self._top = new_node
        self._size += 1

    def pop(self) -> Any:
        """
        Removes and returns the topmost element.
        Raises DataStructureUnderflowError if the stack is empty.
        """
        if self.is_empty():
            raise DataStructureUnderflowError("Movement History Stack")
        popped_node = self._top
        self._top = popped_node.next
        self._size -= 1
        return popped_node.data

    def peek(self) -> Optional[Any]:
        """Returns the topmost element without removing it, or None if empty."""
        if self.is_empty():
            return None
        return self._top.data

    def is_empty(self) -> bool:
        """Returns True if the stack contains no elements."""
        return self._top is None

    def size(self) -> int:
        """Returns total number of elements on the stack."""
        return self._size

    def clear(self) -> None:
        """Empties the stack."""
        self._top = None
        self._size = 0

    def to_list(self) -> List[Any]:
        """Returns elements from top to bottom as a standard Python list."""
        result = []
        current = self._top
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def __len__(self) -> int:
        return self._size

    def __iter__(self):
        current = self._top
        while current is not None:
            yield current.data
            current = current.next

    def __repr__(self) -> str:
        return f"Stack(size={self._size}, top={self.peek()!r})"

