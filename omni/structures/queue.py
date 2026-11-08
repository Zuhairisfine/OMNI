"""
Custom Queue data structure implementation.
Used in O.M.N.I. to schedule AI threats, environmental incidents, and rogue events in FIFO order.
"""

from typing import Any, List, Optional
from omni.core.exceptions import DataStructureUnderflowError


class QueueNode:
    """Represents an individual node in the linked Queue."""

    def __init__(self, data: Any, next_node: Optional["QueueNode"] = None):
        self.data = data
        self.next = next_node

    def __repr__(self) -> str:
        return f"QueueNode({self.data!r})"


class Queue:
    """
    Class-based FIFO (First-In, First-Out) Queue data structure.
    Used for dispatching rogue AI threats and environmental hazards sequentially.
    """

    def __init__(self):
        self._head: Optional[QueueNode] = None
        self._tail: Optional[QueueNode] = None
        self._size: int = 0

    def enqueue(self, item: Any) -> None:
        """Adds an item to the rear of the queue."""
        new_node = QueueNode(item)
        if self.is_empty():
            self._head = new_node
            self._tail = new_node
        else:
            self._tail.next = new_node
            self._tail = new_node
        self._size += 1

    def dequeue(self) -> Any:
        """
        Removes and returns the front item of the queue.
        Raises DataStructureUnderflowError if the queue is empty.
        """
        if self.is_empty():
            raise DataStructureUnderflowError("Threat Scheduler Queue")
        front_node = self._head
        self._head = front_node.next
        if self._head is None:
            self._tail = None
        self._size -= 1
        return front_node.data

    def peek(self) -> Optional[Any]:
        """Returns the item at the front of the queue without removing it, or None if empty."""
        if self.is_empty():
            return None
        return self._head.data

    def is_empty(self) -> bool:
        """Returns True if the queue is empty."""
        return self._head is None

    def size(self) -> int:
        """Returns the count of elements currently queued."""
        return self._size

    def clear(self) -> None:
        """Empties the queue."""
        self._head = None
        self._tail = None
        self._size = 0

    def to_list(self) -> List[Any]:
        """Returns all elements from front to rear as a Python list."""
        result = []
        current = self._head
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def __len__(self) -> int:
        return self._size

    def __iter__(self):
        current = self._head
        while current is not None:
            yield current.data
            current = current.next

    def __repr__(self) -> str:
        return f"Queue(size={self._size}, front={self.peek()!r})"

