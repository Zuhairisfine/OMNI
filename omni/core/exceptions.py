"""
Custom domain-specific exceptions for O.M.N.I. Engine.
Provides error types that are caught and transformed into narrative in-game events.
"""


class OMNIError(Exception):
    """Base exception for all domain errors within the O.M.N.I. Engine."""

    def __init__(self, message: str, severity: str = "MODERATE"):
        super().__init__(message)
        self.severity = severity
        self.message = message


class TemperatureCriticalError(OMNIError):
    """
    Raised when environmental temperature in a chamber or quarantine bay
    breaches life-support thermal safety thresholds.
    """

    def __init__(self, message: str, current_temp: float, threshold: float):
        super().__init__(message, severity="CRITICAL")
        self.current_temp = current_temp
        self.threshold = threshold


class DoorJammedException(OMNIError):
    """
    Raised when a bulkhead or pressure seal door cannot open due to mechanical
    seizure, structural warping, or missing security override.
    """

    def __init__(self, message: str, door_id: str = "Unknown Door"):
        super().__init__(message, severity="HIGH")
        self.door_id = door_id


class PowerGridFailureError(OMNIError):
    """
    Raised when attempting to operate station subsystems that are disconnected
    from the power relay linked list network.
    """

    def __init__(self, message: str, relay_name: str = "Unknown Relay"):
        super().__init__(message, severity="HIGH")
        self.relay_name = relay_name


class InventoryCapacityExceededError(OMNIError):
    """
    Raised when an attempt is made to pick up an item exceeding the player's
    maximum carrying weight limit.
    """

    def __init__(self, message: str, current_weight: float, item_weight: float, max_weight: float):
        super().__init__(message, severity="LOW")
        self.current_weight = current_weight
        self.item_weight = item_weight
        self.max_weight = max_weight


class ItemNotFoundError(OMNIError):
    """Raised when an item search fails to locate an item in an inventory."""

    def __init__(self, item_name: str):
        super().__init__(f"Target item '{item_name}' was not detected in inventory.", severity="LOW")
        self.item_name = item_name


class DataStructureUnderflowError(OMNIError):
    """Raised when popping an empty stack or dequeuing an empty queue."""

    def __init__(self, structure_name: str):
        super().__init__(f"Operation failed: {structure_name} is empty.", severity="MODERATE")
        self.structure_name = structure_name

