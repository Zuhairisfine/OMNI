"""
Hazard entities for O.M.N.I. Engine.
Inherits from GameObject and overrides interact() polymorphically.
Can be dispatched sequentially via the Threat Queue or encountered in unstable rooms.
"""

from typing import Any, Dict
from omni.core.base import GameObject
from omni.core.exceptions import TemperatureCriticalError


class Hazard(GameObject):
    """
    Base class for environmental hazards, rogue AI defense protocols, and mechanical failures.
    """

    def __init__(
        self,
        obj_id: str,
        name: str,
        description: str,
        damage: int = 15,
        hazard_type: str = "ENVIRONMENTAL",
        is_active: bool = True,
    ):
        super().__init__(obj_id, name, description)
        self.damage = max(0, int(damage))
        self.hazard_type = hazard_type.upper()
        self.is_active = is_active

    def interact(self, player: Any) -> str:
        """
        Polymorphic interaction: Triggered when player approaches or interacts with hazard.
        Inflicts damage and reports status.
        """
        if not self.is_active:
            return f"The [{self.name}] has been neutralized and poses no immediate threat."

        player.health -= self.damage
        return (
            f"WARNING! You triggered [{self.name}]! "
            f"Inflicted {self.damage} damage! Player Health is now: {player.health}%"
        )

    def trigger_turn_effect(self, player: Any) -> str:
        """Called when this hazard is dequeued from the threat scheduler."""
        if not self.is_active:
            return f"Scheduled threat [{self.name}] was previously neutralized."
        player.health -= (self.damage // 2)
        return (
            f"[THREAT ALERT]: Station AI O.M.N.I. dispatched [{self.name}]! "
            f"Life support registers {self.damage // 2} secondary damage. Health: {player.health}%"
        )

    def neutralize(self) -> str:
        """Disables the hazard permanently."""
        self.is_active = False
        return f"[{self.name}] has been successfully suppressed."

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "damage": self.damage,
            "hazard_type": self.hazard_type,
            "is_active": self.is_active,
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Hazard":
        hazard_type = data.get("type", "Hazard")
        if hazard_type == "RadiationHazard":
            return RadiationHazard(
                obj_id=data["id"],
                name=data["name"],
                description=data["description"],
                damage=data.get("damage", 20),
                rad_level=data.get("rad_level", 45.0),
                is_active=data.get("is_active", True),
            )
        elif hazard_type == "RogueDroneHazard":
            return RogueDroneHazard(
                obj_id=data["id"],
                name=data["name"],
                description=data["description"],
                damage=data.get("damage", 25),
                drone_id=data.get("drone_id", "DRONE-01"),
                is_active=data.get("is_active", True),
            )
        elif hazard_type == "FireHazard":
            return FireHazard(
                obj_id=data["id"],
                name=data["name"],
                description=data["description"],
                damage=data.get("damage", 30),
                temperature=data.get("temperature", 85.0),
                is_active=data.get("is_active", True),
            )
        return cls(
            obj_id=data["id"],
            name=data["name"],
            description=data["description"],
            damage=data.get("damage", 15),
            hazard_type=data.get("hazard_type", "ENVIRONMENTAL"),
            is_active=data.get("is_active", True),
        )


class RadiationHazard(Hazard):
    """Lethal radioactive leak from damaged reactor conduits."""

    def __init__(
        self,
        obj_id: str,
        name: str,
        description: str,
        damage: int = 20,
        rad_level: float = 50.0,
        is_active: bool = True,
    ):
        super().__init__(obj_id, name, description, damage, hazard_type="RADIATION", is_active=is_active)
        self.rad_level = rad_level

    def interact(self, player: Any) -> str:
        if not self.is_active:
            return f"Geiger counter registers safe background levels around neutralized [{self.name}]."

        # Check if player has rad shield / nanite treatment
        player.health -= self.damage
        return (
            f"CRITICAL RADIATION ALERT! You were exposed to [{self.name}] ({self.rad_level} mSv/h). "
            f"Suffered {self.damage} radiation damage! Vital signs: {player.health}% HP."
        )


class RogueDroneHazard(Hazard):
    """Autonomous security combat drone commandeered by rogue O.M.N.I. AI."""

    def __init__(
        self,
        obj_id: str,
        name: str,
        description: str,
        damage: int = 25,
        drone_id: str = "SYNTH-PATROL-04",
        is_active: bool = True,
    ):
        super().__init__(obj_id, name, description, damage, hazard_type="AI_COMBAT", is_active=is_active)
        self.drone_id = drone_id

    def interact(self, player: Any) -> str:
        if not self.is_active:
            return f"The destroyed chassis of [{self.name}] ({self.drone_id}) lies smoking on the metal deck."

        player.health -= self.damage
        return (
            f"O.M.N.I. TACTICAL LINK: [{self.name}] locks targeting reticle onto you and fires pulsed energy! "
            f"Took {self.damage} damage! Player Health: {player.health}%"
        )


class FireHazard(Hazard):
    """Superheated plasma blaze consuming cabin oxygen and radiating extreme heat."""

    def __init__(
        self,
        obj_id: str,
        name: str,
        description: str,
        damage: int = 30,
        temperature: float = 90.0,
        is_active: bool = True,
    ):
        super().__init__(obj_id, name, description, damage, hazard_type="THERMAL", is_active=is_active)
        self.temperature = temperature

    def interact(self, player: Any) -> str:
        if not self.is_active:
            return f"Charred ash and extinguishing foam mark the remnants of [{self.name}]."

        if self.temperature > 75.0:
            # Domain exception integration as required by proposal
            raise TemperatureCriticalError(
                f"Ambient heat in chamber exceeded safety margins ({self.temperature}°C)!",
                current_temp=self.temperature,
                threshold=75.0,
            )

        player.health -= self.damage
        return f"Blistering fire from [{self.name}] singes your suit! -{self.damage} HP. Health: {player.health}%"

