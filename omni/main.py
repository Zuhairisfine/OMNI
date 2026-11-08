"""
Main entry point for O.M.N.I. Survival Engine.
"""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omni.engine.game import GameEngine


def main():
    player_name = "Dr. Morgan Vance"
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        player_name = sys.argv[1]

    engine = GameEngine(player_name=player_name)
    engine.start_game()


if __name__ == "__main__":
    main()

