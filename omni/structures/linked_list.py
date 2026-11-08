"""
Custom Singly Linked List data structure implementation.
Used in O.M.N.I. to model the station's primary power relay grid and narrative chapters.
Supports traversal, insertion, and deletion of relay nodes to restore circuit continuity.
"""

from typing import Any, Callable, Dict, Iterator, List, Optional


class LinkedListNode:
    """Represents a node within the singly linked list."""

    def __init__(self, data: Any, next_node: Optional["LinkedListNode"] = None):
        self.data = data
        self.next = next_node

    def __repr__(self) -> str:
        return f"LinkedListNode({self.data!r})"


class SinglyLinkedList:
    """
    Custom Singly Linked List data structure.
    Implements standard operations: append, prepend, insert_after, delete, search, traversal.
    """

    def __init__(self):
        self._head: Optional[LinkedListNode] = None
        self._size: int = 0

    @property
    def head(self) -> Optional[LinkedListNode]:
        """Returns the head node."""
        return self._head

    def is_empty(self) -> bool:
        """Returns True if the list has zero nodes."""
        return self._head is None

    def size(self) -> int:
        """Returns the number of elements in the list."""
        return self._size

    def append(self, data: Any) -> None:
        """Appends a new node to the end of the linked list."""
        new_node = LinkedListNode(data)
        if self._head is None:
            self._head = new_node
        else:
            current = self._head
            while current.next is not None:
                current = current.next
            current.next = new_node
        self._size += 1

    def prepend(self, data: Any) -> None:
        """Prepends a new node to the beginning of the list."""
        new_node = LinkedListNode(data, self._head)
        self._head = new_node
        self._size += 1

    def insert_after(self, target_key: Any, new_data: Any, key_fn: Optional[Callable[[Any], Any]] = None) -> bool:
        """
        Inserts new_data immediately after the node matching target_key.
        :param target_key: The value to match against node data or key_fn(node.data).
        :param new_data: The data to insert.
        :param key_fn: Optional accessor to extract comparison key from node data.
        :return: True if successfully inserted, False if target not found.
        """
        current = self._head
        while current is not None:
            extracted = key_fn(current.data) if key_fn else current.data
            if extracted == target_key:
                new_node = LinkedListNode(new_data, current.next)
                current.next = new_node
                self._size += 1
                return True
            current = current.next
        return False

    def delete(self, target_key: Any, key_fn: Optional[Callable[[Any], Any]] = None) -> Optional[Any]:
        """
        Deletes the first node matching target_key.
        :return: The deleted node's data, or None if not found.
        """
        if self._head is None:
            return None

        # Check if head node is the target
        head_key = key_fn(self._head.data) if key_fn else self._head.data
        if head_key == target_key:
            deleted_data = self._head.data
            self._head = self._head.next
            self._size -= 1
            return deleted_data

        current = self._head
        while current.next is not None:
            next_key = key_fn(current.next.data) if key_fn else current.next.data
            if next_key == target_key:
                deleted_data = current.next.data
                current.next = current.next.next
                self._size -= 1
                return deleted_data
            current = current.next

        return None

    def search(self, target_key: Any, key_fn: Optional[Callable[[Any], Any]] = None) -> Optional[Any]:
        """
        Searches for a node matching target_key and returns its data.
        """
        current = self._head
        while current is not None:
            node_key = key_fn(current.data) if key_fn else current.data
            if node_key == target_key:
                return current.data
            current = current.next
        return None

    def traverse(self) -> List[Any]:
        """Traverses the linked list and returns all data elements in order."""
        return self.to_list()

    def to_list(self) -> List[Any]:
        """Converts the linked list into a standard Python list."""
        elements = []
        current = self._head
        while current is not None:
            elements.append(current.data)
            current = current.next
        return elements

    def clear(self) -> None:
        """Clears all nodes from the linked list."""
        self._head = None
        self._size = 0

    def __iter__(self) -> Iterator[Any]:
        current = self._head
        while current is not None:
            yield current.data
            current = current.next

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        items = " -> ".join(str(d) for d in self.to_list())
        return f"SinglyLinkedList({items or 'EMPTY'})"


class PowerRelay:
    """
    Represents an individual power relay conduit node within the station power grid.
    """

    def __init__(self, relay_id: str, name: str, sector: str, is_online: bool = False, is_damaged: bool = False):
        self.relay_id = relay_id
        self.name = name
        self.sector = sector
        self.is_online = is_online
        self.is_damaged = is_damaged

    def repair(self) -> str:
        """Repairs a damaged relay node."""
        if not self.is_damaged:
            return f"Relay '{self.name}' [{self.relay_id}] is already structurally sound."
        self.is_damaged = False
        self.is_online = True
        return f"Relay '{self.name}' [{self.relay_id}] repaired and brought ONLINE."

    def toggle_power(self) -> bool:
        """Toggles online state if relay is not damaged."""
        if self.is_damaged:
            self.is_online = False
            return False
        self.is_online = not self.is_online
        return self.is_online

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relay_id": self.relay_id,
            "name": self.name,
            "sector": self.sector,
            "is_online": self.is_online,
            "is_damaged": self.is_damaged,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PowerRelay":
        return cls(
            relay_id=data["relay_id"],
            name=data["name"],
            sector=data["sector"],
            is_online=data.get("is_online", False),
            is_damaged=data.get("is_damaged", False),
        )

    def __repr__(self) -> str:
        status = "ONLINE" if self.is_online and not self.is_damaged else ("DAMAGED" if self.is_damaged else "OFFLINE")
        return f"[{self.relay_id}: {self.name} ({status})]"


class PowerGrid(SinglyLinkedList):
    """
    Singly linked list representing the station's main energy distribution conduits.
    Energy flows strictly from head (Primary Reactor) sequentially through relays to tail (Escape Pod Bay).
    """

    def is_circuit_complete(self) -> bool:
        """
        Verifies if uninterrupted power reaches all the way to the end of the conduit.
        Fails if any relay in the sequence is offline or damaged.
        """
        if self.is_empty():
            return False
        current = self._head
        while current is not None:
            relay: PowerRelay = current.data
            if not relay.is_online or relay.is_damaged:
                return False
            current = current.next
        return True

    def find_relay(self, relay_id: str) -> Optional[PowerRelay]:
        """Locates a relay by its unique identifier."""
        return self.search(relay_id, key_fn=lambda r: r.relay_id)

    def get_broken_relay(self) -> Optional[PowerRelay]:
        """Returns the first relay blocking circuit continuity."""
        current = self._head
        while current is not None:
            relay: PowerRelay = current.data
            if not relay.is_online or relay.is_damaged:
                return relay
            current = current.next
        return None

    def display_grid(self) -> str:
        """Returns an ASCII schematic representation of the power grid."""
        if self.is_empty():
            return "[GRID OFFLINE: NO RELAYS CONNECTED]"
        nodes_str = []
        current = self._head
        while current is not None:
            nodes_str.append(repr(current.data))
            current = current.next
        return " ====> ".join(nodes_str)

