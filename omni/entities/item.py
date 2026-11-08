"""
Item entities for O.M.N.I. Engine.
Inherits from GameObject and overrides interact() polymorphically.
"""

from typing import Any, Dict
from omni.core.base import GameObject


class Item(GameObject):
    """
    Base class for interactive tools, keys, and supplies found aboard Station O.M.N.I.
    """

    def __init__(
        self,
        obj_id: str,
        name: str,
        description: str,
        weight: float = 1.0,
        value: int = 10,
        charges: int = 1,
    ):
        super().__init__(obj_id, name, description)
        self._weight = max(0.1, float(weight))
        self._value = max(0, int(value))
        self._charges = max(0, int(charges))

    @property
    def weight(self) -> float:
        """Weight of the item in kilograms."""
        return self._weight

    @weight.setter
    def weight(self, val: float) -> None:
        if val < 0:
            raise ValueError("Item weight cannot be negative.")
        self._weight = round(float(val), 2)

    @property
    def value(self) -> int:
        """Utility / resource value rating."""
        return self._value

    @value.setter
    def value(self, val: int) -> None:
        if val < 0:
            raise ValueError("Item value cannot be negative.")
        self._value = int(val)

    @property
    def charges(self) -> int:
        """Remaining uses or charges."""
        return self._charges

    @charges.setter
    def charges(self, val: int) -> None:
        self._charges = max(0, int(val))

    def interact(self, player: Any) -> str:
        """
        Polymorphic interaction: player inspects or examines the item.
        """
        return (
            f"You examine the [{self.name}]: {self.description} "
            f"(Weight: {self.weight}kg, Value: {self.value}, Charges: {self.charges})"
        )

    def use(self, player: Any) -> str:
        """
        Default use logic for generic items.
        """
        if self._charges <= 0:
            return f"The [{self.name}] is depleted and cannot be used."
        self._charges -= 1
        return f"You activate the [{self.name}]. Nothing notable happens."

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "weight": self._weight,
            "value": self._value,
            "charges": self._charges,
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        item_type = data.get("type", "Item")
        if item_type == "MedicalItem":
            return MedicalItem(
                obj_id=data["id"],
                name=data["name"],
                description=data["description"],
                weight=data["weight"],
                value=data["value"],
                heal_amount=data.get("heal_amount", 30),
                charges=data.get("charges", 1),
            )
        elif item_type == "ToolItem":
            return ToolItem(
                obj_id=data["id"],
                name=data["name"],
                description=data["description"],
                weight=data["weight"],
                value=data["value"],
                tool_type=data.get("tool_type", "GENERAL"),
                charges=data.get("charges", 5),
            )
        elif item_type == "KeycardItem":
            return KeycardItem(
                obj_id=data["id"],
                name=data["name"],
                description=data["description"],
                weight=data["weight"],
                value=data["value"],
                clearance_level=data.get("clearance_level", 1),
            )
        elif item_type == "EnergyCellItem":
            return EnergyCellItem(
                obj_id=data["id"],
                name=data["name"],
                description=data["description"],
                weight=data["weight"],
                value=data["value"],
                energy_output=data.get("energy_output", 50),
            )
        return cls(
            obj_id=data["id"],
            name=data["name"],
            description=data["description"],
            weight=data.get("weight", 1.0),
            value=data.get("value", 10),
            charges=data.get("charges", 1),
        )


class MedicalItem(Item):
    """Restores player vital signs and stabilizes biological integrity."""

    def __init__(
        self,
        obj_id: str,
        name: str,
        description: str,
        weight: float = 0.5,
        value: int = 25,
        heal_amount: int = 35,
        charges: int = 1,
    ):
        super().__init__(obj_id, name, description, weight, value, charges)
        self.heal_amount = heal_amount

    def interact(self, player: Any) -> str:
        return (
            f"[{self.name}] - Medical Stimpack. "
            f"Provides +{self.heal_amount} HP upon biological injection."
        )

    def use(self, player: Any) -> str:
        if self._charges <= 0:
            return f"The [{self.name}] has no doses left."
        old_health = player.health
        player.health += self.heal_amount
        actual_healed = player.health - old_health
        self._charges -= 1
        return (
            f"You inject [{self.name}]. Nanite serum surges through your veins! "
            f"+{actual_healed} HP restored. Current Health: {player.health}%"
        )


class ToolItem(Item):
    """Specialized engineering instrument used to repair conduits and bypass bulkheads."""

    def __init__(
        self,
        obj_id: str,
        name: str,
        description: str,
        weight: float = 2.5,
        value: int = 50,
        tool_type: str = "TORCH",
        charges: int = 5,
    ):
        super().__init__(obj_id, name, description, weight, value, charges)
        self.tool_type = tool_type.upper()

    def interact(self, player: Any) -> str:
        return (
            f"[{self.name}] - Heavy Engineering Tool ({self.tool_type}). "
            f"Can force jammed doors and repair damaged power relays. Charges: {self.charges}."
        )

    def use(self, player: Any) -> str:
        if self._charges <= 0:
            return f"The [{self.name}] battery is completely dead."
        return f"You ready the [{self.name}]. Use this to force jammed bulkheads or repair power relays."


class KeycardItem(Item):
    """Cryptographic authorization token granting passage through security gates."""

    def __init__(
        self,
        obj_id: str,
        name: str,
        description: str,
        weight: float = 0.1,
        value: int = 40,
        clearance_level: int = 1,
    ):
        super().__init__(obj_id, name, description, weight, value, charges=999)
        self.clearance_level = clearance_level

    def interact(self, player: Any) -> str:
        return (
            f"[{self.name}] - Security Keycard. "
            f"Embedded with Level-{self.clearance_level} station authorization credentials."
        )

    def use(self, player: Any) -> str:
        return f"You hold up [{self.name}]. Swipe it at a locked terminal or bulkhead reader."


class EnergyCellItem(Item):
    """High-density plasma power cell used to energize offline station conduits."""

    def __init__(
        self,
        obj_id: str,
        name: str,
        description: str,
        weight: float = 3.0,
        value: int = 60,
        energy_output: int = 100,
    ):
        super().__init__(obj_id, name, description, weight, value, charges=1)
        self.energy_output = energy_output

    def interact(self, player: Any) -> str:
        return (
            f"[{self.name}] - Plasma Energy Cell. "
            f"Emits a steady blue glow. Rated at {self.energy_output} MW for relay reactivation."
        )

    def use(self, player: Any) -> str:
        return f"Insert the [{self.name}] into a station power relay or terminal to restore energy flow."

