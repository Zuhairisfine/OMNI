"""
Player entity module for O.M.N.I. Survival Engine.
Demonstrates strict encapsulation with private attributes, validated properties,
inventory weight enforcement, and movement history tracking via custom Stack.
"""

from typing import Any, Dict, List, Optional
from omni.core.exceptions import (
    InventoryCapacityExceededError,
    TemperatureCriticalError,
)
from omni.structures.stack import Stack
from omni.algorithms.search import find_item_in_inventory
from omni.algorithms.sort import bubble_sort, insertion_sort


class Player:
    """
    Encapsulated Player entity aboard Station O.M.N.I.
    Protects health, oxygen, body temperature, and inventory state.
    """

    def __init__(
        self,
        name: str = "Dr. Morgan Vance",
        starting_room_id: str = "cryo_bay",
        max_carry_weight: float = 15.0,
    ):
        self._name = name

        # Encapsulated private attributes
        self.__health: int = 100
        self.__oxygen: int = 100
        self.__temperature: float = 37.0  # Core body temp in °C
        self.__max_carry_weight: float = float(max_carry_weight)
        self.__current_room_id: str = starting_room_id

        # Inventory and Movement Stack
        self.inventory: List[Any] = []
        self.movement_history: Stack = Stack()

    # --- ENCAPSULATION: HEALTH ---
    @property
    def health(self) -> int:
        """Player vital health points (0 - 100)."""
        return self.__health

    @health.setter
    def health(self, value: int) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("Health value must be a numeric integer.")
        clamped = int(value)
        if clamped > 100:
            clamped = 100
        elif clamped < 0:
            clamped = 0
        self.__health = clamped

    # --- ENCAPSULATION: OXYGEN ---
    @property
    def oxygen(self) -> int:
        """Suit atmospheric oxygen reserve (0 - 100%)."""
        return self.__oxygen

    @oxygen.setter
    def oxygen(self, value: int) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("Oxygen value must be numeric.")
        clamped = max(0, min(100, int(value)))
        self.__oxygen = clamped

    # --- ENCAPSULATION: TEMPERATURE ---
    @property
    def temperature(self) -> float:
        """Internal suit / body core temperature in Celsius."""
        return self.__temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("Temperature must be a numeric float.")
        val = float(value)
        if val > 42.0:
            self.__temperature = val
            raise TemperatureCriticalError(
                f"Severe hyperthermia detected! Core body temp spiked to {val:.1f}°C!",
                current_temp=val,
                threshold=42.0,
            )
        elif val < 32.0:
            self.__temperature = val
            raise TemperatureCriticalError(
                f"Severe hypothermia detected! Core body temp plummeted to {val:.1f}°C!",
                current_temp=val,
                threshold=32.0,
            )
        self.__temperature = round(val, 2)

    # --- ENCAPSULATION: MAX WEIGHT ---
    @property
    def max_carry_weight(self) -> float:
        """Maximum carrying capacity in kilograms."""
        return self.__max_carry_weight

    @max_carry_weight.setter
    def max_carry_weight(self, value: float) -> None:
        val = float(value)
        if val <= 0:
            raise ValueError("Carry weight limit must be positive.")
        self.__max_carry_weight = round(val, 2)

    # --- ENCAPSULATION: CURRENT ROOM ---
    @property
    def current_room_id(self) -> str:
        """Identifier of the player's current sector."""
        return self.__current_room_id

    @current_room_id.setter
    def current_room_id(self, room_id: str) -> None:
        if not room_id or not isinstance(room_id, str):
            raise ValueError("Room ID must be a non-empty string.")
        self.__current_room_id = room_id.strip()

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_alive(self) -> bool:
        """Returns True if the player's life signs are stable."""
        return self.__health > 0 and self.__oxygen > 0

    # --- INVENTORY & WEIGHT LOGIC ---
    @property
    def current_carry_weight(self) -> float:
        """Calculates total weight of all carried items."""
        return round(sum(item.weight for item in self.inventory), 2)

    def can_carry(self, item_weight: float) -> bool:
        """Checks if adding item_weight exceeds maximum carry capacity."""
        return (self.current_carry_weight + item_weight) <= self.__max_carry_weight

    def add_to_inventory(self, item: Any) -> None:
        """
        Adds an item to the player's pack.
        Raises InventoryCapacityExceededError if over weight limit.
        """
        if not self.can_carry(item.weight):
            raise InventoryCapacityExceededError(
                f"Exceeds carrying capacity! Carrying {self.current_carry_weight}kg + {item.weight}kg > max {self.__max_carry_weight}kg.",
                current_weight=self.current_carry_weight,
                item_weight=item.weight,
                max_weight=self.__max_carry_weight,
            )
        self.inventory.append(item)

    def remove_from_inventory(self, item_name: str) -> Optional[Any]:
        """Removes an item by name using linear search."""
        target = item_name.strip().lower()
        for i, item in enumerate(self.inventory):
            if item.name.lower() == target or item.id.lower() == target:
                return self.inventory.pop(i)
        return None

    def find_item(self, item_name: str) -> Optional[Any]:
        """Locates an item in inventory via linear search algorithm."""
        return find_item_in_inventory(self.inventory, item_name)

    def sort_inventory(self, key: str = "weight", reverse: bool = False, algorithm: str = "bubble") -> None:
        """
        Sorts the player's inventory using custom sorting algorithms (Bubble Sort or Insertion Sort).
        """
        if algorithm == "insertion":
            self.inventory = insertion_sort(self.inventory, key=key, reverse=reverse)
        else:
            self.inventory = bubble_sort(self.inventory, key=key, reverse=reverse)

    # --- MOVEMENT HISTORY & LIFO FLEE ---
    def record_movement(self, room_id: str) -> None:
        """Pushes previous room location to movement history stack before entering new room."""
        self.movement_history.push(room_id)

    def flee(self) -> Optional[str]:
        """
        Pops the most recent room from the movement history stack (LIFO)
        to facilitate emergency retreat to previous sector.
        """
        if self.movement_history.is_empty():
            return None
        previous_room = self.movement_history.pop()
        self.__current_room_id = previous_room
        return previous_room

    # --- SERIALIZATION ---
    def to_dict(self) -> Dict[str, Any]:
        """Serializes player state to dictionary for Neural Upload checkpoint."""
        return {
            "name": self._name,
            "health": self.__health,
            "oxygen": self.__oxygen,
            "temperature": self.__temperature,
            "max_carry_weight": self.__max_carry_weight,
            "current_room_id": self.__current_room_id,
            "inventory": [item.to_dict() for item in self.inventory],
            "movement_history": self.movement_history.to_list(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        """Restores player state from serialized data."""
        from omni.entities.item import Item

        player = cls(
            name=data["name"],
            starting_room_id=data["current_room_id"],
            max_carry_weight=data.get("max_carry_weight", 15.0),
        )
        player.health = data.get("health", 100)
        player.oxygen = data.get("oxygen", 100)
        player.temperature = data.get("temperature", 37.0)

        # Reconstruct items
        for item_data in data.get("inventory", []):
            player.inventory.append(Item.from_dict(item_data))

        # Reconstruct history stack (restore bottom-up)
        history_list = data.get("movement_history", [])
        for room_id in reversed(history_list):
            player.movement_history.push(room_id)

        return player
