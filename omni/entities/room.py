"""
Room entities for O.M.N.I. Engine.
Inherits from GameObject and overrides interact() polymorphically.
Includes specialized MedicalQuarantineBay with encapsulated private attributes.
"""

from typing import Any, Dict, List, Optional
from omni.core.base import GameObject
from omni.core.exceptions import DoorJammedException, TemperatureCriticalError
from omni.entities.item import Item
from omni.entities.hazard import Hazard


class Room(GameObject):
    """
    Represents an architectural sector aboard Deep Space Station O.M.N.I.
    Contains items, environmental hazards, and directional bulkhead doors.
    """

    def __init__(
        self,
        obj_id: str,
        name: str,
        description: str,
        is_locked: bool = False,
        required_key: Optional[str] = None,
        is_door_jammed: bool = False,
    ):
        super().__init__(obj_id, name, description)
        self.exits: Dict[str, str] = {}  # e.g., {'north': 'room_02', 'east': 'room_03'}
        self.items: List[Item] = []
        self.hazards: List[Hazard] = []
        self.is_locked = is_locked
        self.required_key = required_key
        self.is_door_jammed = is_door_jammed
        self.visited = False

    def connect_exit(self, direction: str, destination_room_id: str) -> None:
        """Connects a directional corridor exit."""
        self.exits[direction.lower().strip()] = destination_room_id

    def add_item(self, item: Item) -> None:
        """Places an item in this room."""
        self.items.append(item)

    def remove_item(self, item_name: str) -> Optional[Item]:
        """Removes an item by name from the room."""
        target = item_name.strip().lower()
        for i, item in enumerate(self.items):
            if item.name.lower() == target or item.id.lower() == target:
                return self.items.pop(i)
        return None

    def add_hazard(self, hazard: Hazard) -> None:
        """Adds a threat or environmental hazard to this room."""
        self.hazards.append(hazard)

    def interact(self, player: Any) -> str:
        """
        Polymorphic interaction: Scans the room, reporting surroundings,
        visible items, active threats, and available directional airlocks.
        """
        self.visited = True
        status_lines = [
            f"=== [ SECTOR: {self.name} ] ===",
            self.description,
        ]

        if self.items:
            item_list = ", ".join(f"[{item.name}]" for item in self.items)
            status_lines.append(f"Detected Items on deck: {item_list}")
        else:
            status_lines.append("No loose equipment detected in this sector.")

        active_hazards = [h for h in self.hazards if h.is_active]
        if active_hazards:
            hazard_list = ", ".join(f"[{h.name}]" for h in active_hazards)
            status_lines.append(f"CRITICAL WARNING! Active Hazards present: {hazard_list}")

        exit_list = ", ".join(self.exits.keys()) if self.exits else "NONE (SEALED)"
        status_lines.append(f"Available Bulkhead Exits: {exit_list}")

        return "\n".join(status_lines)

    def check_entry_permitted(self, player: Any) -> None:
        """
        Validates whether player can enter.
        Raises DoorJammedException if door is mechanically stuck.
        """
        if self.is_door_jammed:
            raise DoorJammedException(
                f"Airlock to [{self.name}] is mechanically warped and jammed! Hydraulic pressure failure.",
                door_id=self.id,
            )

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "exits": self.exits,
            "items": [item.to_dict() for item in self.items],
            "hazards": [hazard.to_dict() for hazard in self.hazards],
            "is_locked": self.is_locked,
            "required_key": self.required_key,
            "is_door_jammed": self.is_door_jammed,
            "visited": self.visited,
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Room":
        room_type = data.get("type", "Room")
        if room_type == "MedicalQuarantineBay":
            room = MedicalQuarantineBay(
                obj_id=data["id"],
                name=data["name"],
                description=data["description"],
                temperature=data.get("temperature", 21.0),
                contamination_level=data.get("contamination_level", 12.0),
            )
        else:
            room = cls(
                obj_id=data["id"],
                name=data["name"],
                description=data["description"],
                is_locked=data.get("is_locked", False),
                required_key=data.get("required_key"),
                is_door_jammed=data.get("is_door_jammed", False),
            )
        room.exits = data.get("exits", {})
        room.visited = data.get("visited", False)
        room.items = [Item.from_dict(i_data) for i_data in data.get("items", [])]
        room.hazards = [Hazard.from_dict(h_data) for h_data in data.get("hazards", [])]
        return room


class MedicalQuarantineBay(Room):
    """
    Subclass demonstrating strict Encapsulation with private attributes.
    Protects __temperature, __contamination_level, and __quarantine_status
    via validated @property decorators as specifically requested in proposal.
    """

    def __init__(
        self,
        obj_id: str,
        name: str,
        description: str,
        temperature: float = 22.0,
        contamination_level: float = 15.0,
    ):
        super().__init__(obj_id, name, description)
        # Private encapsulated attributes
        self.__temperature: float = 22.0
        self.__contamination_level: float = 0.0
        self.__quarantine_active: bool = True
        self.__max_temp_safe: float = 65.0
        self.__min_temp_safe: float = -10.0

        # Setters with validation
        self.temperature = temperature
        self.contamination_level = contamination_level

    @property
    def temperature(self) -> float:
        """Internal chamber temperature in Celsius."""
        return self.__temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """
        Validates temperature. Raises TemperatureCriticalError if
        ambient environmental controls fail dangerously.
        """
        val = float(value)
        if val > self.__max_temp_safe:
            self.__temperature = val
            raise TemperatureCriticalError(
                f"Quarantine thermal regulator runaway! Chamber at {val:.1f}°C exceeds threshold {self.__max_temp_safe}°C!",
                current_temp=val,
                threshold=self.__max_temp_safe,
            )
        elif val < self.__min_temp_safe:
            self.__temperature = val
            raise TemperatureCriticalError(
                f"Quarantine cryo-coolant rupture! Chamber frozen at {val:.1f}°C drops below threshold {self.__min_temp_safe}°C!",
                current_temp=val,
                threshold=self.__min_temp_safe,
            )
        self.__temperature = round(val, 2)

    @property
    def contamination_level(self) -> float:
        """Biohazard / pathogen saturation percentage (0.0% to 100.0%)."""
        return self.__contamination_level

    @contamination_level.setter
    def contamination_level(self, value: float) -> None:
        val = float(value)
        if val < 0.0 or val > 100.0:
            raise ValueError("Contamination level must be bounded between 0.0% and 100.0%.")
        self.__contamination_level = round(val, 2)
        if self.__contamination_level <= 0.0:
            self.__quarantine_active = False

    @property
    def quarantine_active(self) -> bool:
        """Whether bio-containment seal is actively engaged."""
        return self.__quarantine_active

    def sanitize_chamber(self, reduction_pct: float = 30.0) -> str:
        """Engages ultraviolet decontamination spray to reduce biological hazard."""
        new_val = max(0.0, self.__contamination_level - reduction_pct)
        self.contamination_level = new_val
        if not self.__quarantine_active:
            return "DECONTAMINATION COMPLETE: Quarantine seal DISENGAGED. Atmosphere sterilized."
        return f"Decontamination pulse complete. Contamination down to {self.__contamination_level}%."

    def interact(self, player: Any) -> str:
        base_desc = super().interact(player)
        quarantine_hud = (
            f"\n[QUARANTINE TELEMETRY]:\n"
            f"  - Chamber Temp: {self.temperature:.1f}°C\n"
            f"  - Bio-Contamination: {self.contamination_level:.1f}%\n"
            f"  - Quarantine Seal: {'ENGAGED' if self.quarantine_active else 'DISENGAGED'}"
        )
        return base_desc + quarantine_hud

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "temperature": self.__temperature,
            "contamination_level": self.__contamination_level,
            "quarantine_active": self.__quarantine_active,
        })
        return data

