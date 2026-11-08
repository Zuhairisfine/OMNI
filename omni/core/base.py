"""
Abstract base module for the O.M.N.I. Survival Engine.
Defines the GameObject abstract base class enforcing the polymorphic interact() interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class GameObject(ABC):
    """
    Abstract base class for all interactive entities on Station O.M.N.I.
    Enforces the polymorphic interact() method across Rooms, Hazards, and Items.
    """

    def __init__(self, obj_id: str, name: str, description: str):
        self._id = obj_id
        self._name = name
        self._description = description

    @property
    def id(self) -> str:
        """Unique identifier of the game object."""
        return self._id

    @property
    def name(self) -> str:
        """Human-readable name of the object."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("Object name must be a non-empty string.")
        self._name = value.strip()

    @property
    def description(self) -> str:
        """Detailed sensory description of the object."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        if not value or not isinstance(value, str):
            raise ValueError("Object description must be a non-empty string.")
        self._description = value.strip()

    @abstractmethod
    def interact(self, player: Any) -> str:
        """
        Polymorphic interaction method. Must be overridden by all concrete subclasses
        (Room, Hazard, Item, etc.) to define specific behavior upon player interaction.

        :param player: The Player instance initiating interaction.
        :return: A narrative result string describing the outcome.
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Base dictionary representation for serialization."""
        return {
            "type": self.__class__.__name__,
            "id": self._id,
            "name": self._name,
            "description": self._description,
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self._id!r} name={self._name!r}>"

    def __str__(self) -> str:
        return f"{self._name}: {self._description}"

