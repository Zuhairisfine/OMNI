"""
Scripted playthrough test verifying end-to-end gameplay loop.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omni.engine.game import GameEngine


def test_gameplay():
    print("Initializing GameEngine for test scenario...")
    game = GameEngine(player_name="Test Pilot Vance")

    # Check initial room
    print(f"Initial Room: {game.current_room.name}")
    assert game.current_room.id == "cryo_bay"

    # Take prybar and medkit
    game.process_command("take Titanium Prybar")
    game.process_command("take Emergency Stimpack")
    print(f"Inventory: {[i.name for i in game.player.inventory]}")
    assert len(game.player.inventory) == 2

    # Test sorting
    game.process_command("sort weight")
    game.process_command("sort value")

    # Test search
    game.process_command("search Titanium Prybar")

    # Move north to corridor
    game.process_command("move north")
    assert game.current_room.id == "corridor"
    assert game.player.movement_history.peek() == "cryo_bay"

    # Test flee (should retreat to cryo_bay)
    game.process_command("flee")
    assert game.current_room.id == "cryo_bay"

    # Move back north to corridor
    game.process_command("move north")
    assert game.current_room.id == "corridor"

    # Move east to engineering
    game.process_command("move east")
    assert game.current_room.id == "engineering"

    # Take cutter and coupler
    game.process_command("take Plasma Torch Cutter")
    game.process_command("take Magnetic Relay Coupler")

    # Attempt to move south into jammed reactor core (triggers DoorJammedException handled as narrative event)
    print("Testing DoorJammedException...")
    game.process_command("move south")
    assert game.current_room.id == "engineering"  # Still in engineering

    # Force the door
    print("Forcing jammed bulkhead...")
    game.process_command("force door")
    # Now move south into reactor
    game.process_command("move south")
    assert game.current_room.id == "reactor_core"

    # Take command keycard
    game.process_command("take Bridge Command Keycard")

    # Check power grid
    game.process_command("power")
    # Repair relay 02
    game.process_command("repair RELAY-02")
    game.process_command("repair RELAY-03")
    game.process_command("repair RELAY-04")
    game.process_command("repair RELAY-05")

    # Test save checkpoint
    game.process_command("save")
    assert os.path.exists("saves/neural_checkpoint.json")

    # Move north back to engineering, then west to corridor, then north to quarantine
    game.process_command("move north")
    game.process_command("move west")
    game.process_command("move north")
    assert game.current_room.id == "quarantine"

    # Sanitize quarantine
    game.process_command("decontaminate")

    # Move north to bridge (requires Bridge Command Keycard which we have!)
    game.process_command("move north")
    assert game.current_room.id == "bridge"

    # Take escape pod launch code
    game.process_command("take Escape Pod Launch Code")

    # Move north to escape bay
    game.process_command("move north")
    assert game.current_room.id == "escape_bay"

    # Attempt launch
    print("Attempting escape launch...")
    game.process_command("launch")
    assert game.has_won is True
    print("\nSUCCESS: End-to-end game scenario completed with win condition achieved!")


if __name__ == "__main__":
    test_gameplay()
