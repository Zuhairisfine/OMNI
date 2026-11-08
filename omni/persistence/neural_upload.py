"""
Neural Upload Persistence System for O.M.N.I.
Serializes player consciousness and station telemetry to JSON checkpoints,
allowing progress recovery across engine restarts.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class NeuralUpload:
    """
    Handles JSON serialization and deserialization of the entire O.M.N.I. station state.
    """

    DEFAULT_SAVE_DIR = "saves"
    DEFAULT_FILENAME = "neural_checkpoint.json"

    @classmethod
    def get_save_path(cls, filename: Optional[str] = None, save_dir: Optional[str] = None) -> str:
        folder = save_dir or cls.DEFAULT_SAVE_DIR
        file = filename or cls.DEFAULT_FILENAME
        return os.path.join(folder, file)

    @classmethod
    def save_checkpoint(
        cls,
        player_dict: Dict[str, Any],
        rooms_dict: Dict[str, Any],
        power_grid_list: List[Dict[str, Any]],
        threat_queue_list: List[Dict[str, Any]],
        turn_count: int,
        filepath: Optional[str] = None,
    ) -> str:
        """
        Serializes all station systems and player status to disk as a JSON checkpoint.
        :return: Absolute path to the saved checkpoint.
        """
        path = filepath or cls.get_save_path()
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)

        payload = {
            "protocol": "O.M.N.I. NEURAL UPLOAD CHECKPOINT",
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "turn_count": turn_count,
            "player": player_dict,
            "rooms": rooms_dict,
            "power_grid": power_grid_list,
            "threat_queue": threat_queue_list,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)

        return path

    @classmethod
    def load_checkpoint(cls, filepath: Optional[str] = None) -> Dict[str, Any]:
        """
        Loads and validates a neural upload checkpoint file.
        :return: Decoded JSON dictionary.
        """
        path = filepath or cls.get_save_path()
        if not os.path.exists(path):
            raise FileNotFoundError(f"Neural checkpoint file '{path}' not found.")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "player" not in data or "rooms" not in data:
            raise ValueError(f"Corrupt checkpoint format in '{path}'.")

        return data

    @classmethod
    def checkpoint_exists(cls, filepath: Optional[str] = None) -> bool:
        path = filepath or cls.get_save_path()
        return os.path.exists(path)

