"""
Core module for O.M.N.I. Engine.
"""

from omni.core.base import GameObject
from omni.core.exceptions import (
    OMNIError,
    TemperatureCriticalError,
    DoorJammedException,
    PowerGridFailureError,
    InventoryCapacityExceededError,
    ItemNotFoundError,
    DataStructureUnderflowError,
)
from omni.core.player import Player

__all__ = [
    "GameObject",
    "OMNIError",
    "TemperatureCriticalError",
    "DoorJammedException",
    "PowerGridFailureError",
    "InventoryCapacityExceededError",
    "ItemNotFoundError",
    "DataStructureUnderflowError",
    "Player",
]

