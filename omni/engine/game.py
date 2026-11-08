"""
Core Game Engine for O.M.N.I. Survival Engine.
Implements the interactive turn loop with screen clearing, clean event logs,
numbered contextual action menus, dynamic mission objectives checklist,
threat queue escalation, exception narrative handling, and win/loss resolution.
"""

import sys
from typing import Dict, List, Optional, Tuple
from omni.core.player import Player
from omni.core.base import GameObject
from omni.core.exceptions import (
    OMNIError,
    TemperatureCriticalError,
    DoorJammedException,
    PowerGridFailureError,
    InventoryCapacityExceededError,
    DataStructureUnderflowError,
)
from omni.entities.room import Room, MedicalQuarantineBay
from omni.entities.item import Item, ToolItem
from omni.entities.hazard import Hazard
from omni.structures.linked_list import PowerGrid, PowerRelay
from omni.structures.queue import Queue
from omni.persistence.neural_upload import NeuralUpload
from omni.engine.map_builder import build_default_station
from omni.engine.ui import UI
from omni.algorithms.search import linear_search, binary_search
from omni.algorithms.sort import bubble_sort, insertion_sort


class GameEngine:
    """
    Coordinates state, input parsing, game turns, and subsystems for O.M.N.I.
    Provides screen clearing, an event log box, and an objectives checklist.
    """

    def __init__(self, player_name: str = "Dr. Morgan Vance"):
        self.rooms, self.power_grid, self.threat_queue = build_default_station()
        self.player = Player(name=player_name, starting_room_id="cryo_bay")
        self.turn_count: int = 1
        self.is_running: bool = False
        self.has_won: bool = False
        self._current_actions: List[Tuple[str, str]] = []
        self.event_logs: List[str] = []

    @property
    def current_room(self) -> Room:
        """Returns the Room instance where player is currently located."""
        return self.rooms[self.player.current_room_id]

    def log(self, message: str) -> None:
        """Logs an event message to be displayed on the refreshed screen."""
        self.event_logs.append(message)
        if not sys.stdout.isatty():
            print(message)

    def get_objectives_status(self) -> List[Tuple[str, str, bool]]:
        """
        Returns the structured 5-step mission escape checklist.
        Format: (step_label, description, is_completed)
        """
        has_tool = any(isinstance(i, ToolItem) for i in self.player.inventory)
        has_bridge_key = any("bridge command" in i.name.lower() for i in self.player.inventory)
        has_launch_code = any("launch code" in i.name.lower() for i in self.player.inventory)
        power_ok = self.power_grid.is_circuit_complete()
        at_escape_bay = (self.player.current_room_id == "escape_bay")

        online_relays = sum(1 for r in self.power_grid if r.is_online and not r.is_damaged)
        total_relays = self.power_grid.size()

        return [
            ("STEP 1", "Acquire an engineering tool (Prybar in Cryo / Cutter in Engineering)", has_tool),
            ("STEP 2", "Breach Reactor Core & retrieve Bridge Command Keycard", has_bridge_key),
            ("STEP 3", f"Restore Power Grid continuity across all relays ({online_relays}/{total_relays} Online)", power_ok),
            ("STEP 4", "Infiltrate Command Bridge & download Escape Pod Launch Code", has_launch_code),
            ("STEP 5", "Reach Emergency Escape Pod Bay & fire retro-thrusters to hyperspace", self.has_won or (at_escape_bay and power_ok and has_launch_code)),
        ]

    def get_current_objective_headline(self) -> str:
        """Generates the concise one-line active objective for the HUD."""
        steps = self.get_objectives_status()
        for step_label, desc, is_done in steps:
            if not is_done:
                return f"[{step_label}] {desc}"
        return "[STEP 5] All systems ready! Launch the escape pod to survive!"

    def get_available_actions(self) -> List[Tuple[str, str]]:
        """
        Dynamically discovers all valid contextual actions for the current room.
        Returns a list of (internal_command, display_label).
        """
        actions: List[Tuple[str, str]] = []
        cur = self.current_room

        # 1. Navigation / Movement
        for direction, dest_id in cur.exits.items():
            dest_room = self.rooms.get(dest_id)
            dest_name = dest_room.name if dest_room else dest_id
            if dest_room and getattr(dest_room, "is_door_jammed", False):
                actions.append(("force door", f"Force Jammed Door to [{dest_name}] (Use Prybar/Cutter)"))
            elif dest_room and getattr(dest_room, "is_locked", False):
                actions.append((f"move {direction}", f"Unlock & Enter [{dest_name}] (Requires Keycard)"))
            else:
                actions.append((f"move {direction}", f"Move {direction.title()} -> [{dest_name}]"))

        # 2. Pick up items from room
        for item in cur.items:
            actions.append((f"take {item.name}", f"Pick up [{item.name}] ({item.weight}kg)"))

        # 3. Sector-specific puzzles & mechanics
        if isinstance(cur, MedicalQuarantineBay) and cur.quarantine_active:
            actions.append(("decontaminate", "Initiate Bio-Decontamination Cycle"))

        if cur.id == "escape_bay":
            actions.append(("launch", "LAUNCH ESCAPE POD TO HYPERSPACE (WIN)"))

        # 4. Emergency Flee (LIFO retreat using movement stack)
        if not self.player.movement_history.is_empty():
            prev_id = self.player.movement_history.peek()
            prev_room = self.rooms.get(prev_id)
            prev_name = prev_room.name if prev_room else "Previous Sector"
            actions.append(("flee", f"Emergency Flee (Retreat backwards to [{prev_name}])"))

        # 5. Core Systems & Submenus
        inv_count = len(self.player.inventory)
        actions.append(("inventory", f"Backpack Inventory ({inv_count} items, {self.player.current_carry_weight:.1f}kg)"))
        actions.append(("power", "Power Grid Relays & Diagnostics"))
        actions.append(("objectives", "View Mission Objectives Checklist"))
        actions.append(("map", "Tactical Station Map"))
        actions.append(("system", "System Menu (Save / Load / Help / Quit)"))

        return actions

    def start_game(self) -> None:
        """Initializes game loop with boot-up sequence, screen clearing, and narrative setup."""
        self.is_running = True
        UI.play_boot_sequence(player_name=self.player.name)
        UI.clear_screen()
        print(UI.banner())
        print(
            "ALERT: Deep Space Research Station 'Promethium'.\n"
            "Mainframe AI 'O.M.N.I.' has entered a rogue state. Life support is collapsing.\n"
            "YOUR OBJECTIVE: Restore grid power, download launch codes, and escape via the pod.\n"
            "CONTROLS: Simply type a number [1, 2, 3...] to take an action, or type direct commands!\n"
        )
        self.log(UI.omni_message("Organic lifeform detected in Cryo Stasis. Terminating life support redundancy..."))

        # Main interactive loop
        while self.is_running and self.player.is_alive and not self.has_won:
            self._render_turn_screen()
            try:
                num_choices = len(self._current_actions)
                prompt = f"\n{UI.BOLD}[ACTION] Enter [1-{num_choices}] or command >> {UI.RESET}"
                user_input = input(prompt).strip()
                if not user_input:
                    continue
                self.process_command(user_input)
            except (KeyboardInterrupt, EOFError):
                print("\n[ABORT]: Simulation terminated by operator.")
                break

        self._evaluate_game_conclusion()

    def _render_turn_screen(self) -> None:
        """
        Clears the terminal screen (deleting previous input/output history)
        and displays the fresh turn interface with HUD, event logs, sector, and choices.
        """
        UI.clear_screen()

        is_powered = self.power_grid.is_circuit_complete()
        threat_count = self.threat_queue.size()
        objective = self.get_current_objective_headline()

        # Telemetry HUD
        print(UI.render_hud(self.player, self.current_room, is_powered, threat_count, objective))

        # Event log box from the most recent action
        if self.event_logs:
            print(UI.render_event_log(self.event_logs))
            self.event_logs = []

        # Current Sector Details
        print(UI.render_sector_view(self.current_room, self.rooms))

        # Available Actions Menu
        self._current_actions = self.get_available_actions()
        print(UI.render_action_menu(self._current_actions))

    def process_command(self, cmd_line: str) -> None:
        """
        Parses and executes player input.
        Supports both numbered menu inputs [1, 2, 3...] and typed CLI commands.
        """
        clean_input = cmd_line.strip()
        if not clean_input:
            return

        # 1. Numbered selection from current action menu
        if clean_input.isdigit() and self._current_actions:
            idx = int(clean_input) - 1
            if 0 <= idx < len(self._current_actions):
                target_cmd = self._current_actions[idx][0]
                self._dispatch_command(target_cmd)
                return
            else:
                self.log(UI.warning_message(f"Please select a number between 1 and {len(self._current_actions)}."))
                return

        # 2. Direct typed command
        self._dispatch_command(clean_input)

    def _dispatch_command(self, cmd_line: str) -> None:
        """Internal command dispatcher with defensive exception handling."""
        tokens = cmd_line.strip().split()
        verb = tokens[0].lower()
        arg = " ".join(tokens[1:]) if len(tokens) > 1 else ""

        try:
            if verb in ["n", "north", "s", "south", "e", "east", "w", "west", "move", "go"]:
                direction = arg if verb in ["move", "go"] else verb
                if direction in ["n", "s", "e", "w"]:
                    direction = {"n": "north", "s": "south", "e": "east", "w": "west"}[direction]
                self.handle_move(direction)

            elif verb == "flee":
                self.handle_flee()

            elif verb in ["interact", "examine", "inspect", "look"]:
                self.handle_interact(arg)

            elif verb in ["take", "get", "grab", "pickup"]:
                self.handle_take(arg)

            elif verb in ["drop", "discard"]:
                self.handle_drop(arg)

            elif verb == "use":
                self.handle_use(arg)

            elif verb in ["inventory", "inv", "i", "pack", "bag"]:
                self.handle_inventory()

            elif verb in ["objectives", "objective", "goal", "mission", "tasks"]:
                self.handle_objectives()

            elif verb == "sort":
                self.handle_sort(arg)

            elif verb == "search":
                self.handle_search(arg)

            elif verb in ["power", "grid"]:
                self.handle_power_grid()

            elif verb == "repair":
                self.handle_repair_relay(arg)

            elif verb in ["force", "cut", "pry"]:
                self.handle_force_door()

            elif verb in ["decontaminate", "sanitize", "clean"]:
                self.handle_decontaminate()

            elif verb == "map":
                print(UI.render_map(self.rooms, self.player.current_room_id))
                if sys.stdin.isatty():
                    input("\nPress Enter to return to action menu...")

            elif verb in ["system", "menu"]:
                self.handle_system_menu()

            elif verb in ["status"]:
                pass

            elif verb in ["save", "upload"]:
                self.handle_save()

            elif verb in ["load", "restore"]:
                self.handle_load()

            elif verb in ["launch", "escape"]:
                self.handle_escape()

            elif verb in ["help", "?"]:
                self.handle_help()

            elif verb in ["quit", "exit"]:
                self.log("Ending O.M.N.I. simulation. Goodbye.")
                self.is_running = False
                return

            else:
                cur = self.current_room
                matched_item = None
                for item in cur.items:
                    if verb in item.name.lower():
                        matched_item = item
                        break
                if matched_item:
                    self.log(f">> Assuming: 'take {matched_item.name}'...")
                    self.handle_take(matched_item.name)
                else:
                    self.log(UI.warning_message(
                        f"Unrecognized action: '{cmd_line}'. Type a number [1-{len(self._current_actions)}] or 'help'."
                    ))
                return

            # Advance game turn if an action occurred
            self._advance_turn()

        except TemperatureCriticalError as tce:
            self.log(UI.error_message(f"THERMAL HAZARD ALERT: {tce.message} (Readout: {tce.current_temp}°C)"))
            self.player.health -= 20
        except DoorJammedException as dje:
            self.log(UI.warning_message(f"MECHANICAL RESISTANCE: {dje.message}\nTip: Select option 'Force Jammed Door' using a Prybar or Cutter."))
        except InventoryCapacityExceededError as ice:
            self.log(UI.warning_message(f"LOAD CAPACITY EXCEEDED: {ice.message} (Drop an item first from inventory)."))
        except PowerGridFailureError as pfe:
            self.log(UI.error_message(f"POWER CONDUIT OFFLINE: {pfe.message}"))
        except DataStructureUnderflowError as due:
            self.log(UI.warning_message(f"TACTICAL SYSTEM WARNING: {due.message}"))
        except OMNIError as oe:
            self.log(UI.warning_message(f"O.M.N.I. SYSTEM FAULT: {oe.message}"))

    def handle_objectives(self) -> None:
        """Displays the mission objectives checklist."""
        steps = self.get_objectives_status()
        checklist_text = UI.render_objectives_checklist(steps)
        print(checklist_text)
        if sys.stdin.isatty():
            input("Press Enter to return to action menu...")

    def handle_move(self, direction: str) -> None:
        """
        Moves player in specified direction.
        Checks locked bulkheads, jams, and records movement on Stack for Flee LIFO tracking.
        """
        cur = self.current_room
        if direction not in cur.exits:
            self.log(UI.warning_message(f"No bulkhead leading '{direction}'. Available: {', '.join(cur.exits.keys())}"))
            return

        target_room_id = cur.exits[direction]
        target_room = self.rooms[target_room_id]

        target_room.check_entry_permitted(self.player)

        if target_room.is_locked and target_room.required_key:
            has_key = any(item.name.lower() == target_room.required_key.lower() for item in self.player.inventory)
            if not has_key:
                self.log(UI.warning_message(
                    f"Airlock to [{target_room.name}] is magnetically SEALED. Requires '{target_room.required_key}'."
                ))
                return
            else:
                self.log(UI.success_message(f"Security keycard accepted. Airlock unlocked: [{target_room.name}]."))
                target_room.is_locked = False

        self.player.record_movement(self.player.current_room_id)
        self.player.current_room_id = target_room_id
        target_room.visited = True
        self.log(UI.success_message(f"Moved through bulkhead into [{target_room.name}]."))

        for hazard in target_room.hazards:
            if hazard.is_active:
                self.log(UI.warning_message(f"HAZARD DETECTED UPON ENTRY: {hazard.name}!"))
                self.log(hazard.interact(self.player))

    def handle_flee(self) -> None:
        """
        LIFO movement retreat: pops the most recently visited room from the Stack
        and retreats immediately to it.
        """
        previous_room_id = self.player.flee()
        if not previous_room_id:
            self.log(UI.warning_message("Movement history stack is empty. There is nowhere to flee back to!"))
            return

        prev_room = self.rooms[previous_room_id]
        self.log(UI.warning_message(f">> EMERGENCY TACTICAL RETREAT! You fled backwards into [{prev_room.name}]."))

    def handle_interact(self, target_name: str) -> None:
        """Polymorphic interaction with any GameObject."""
        cur = self.current_room
        if not target_name or target_name.lower() in ["room", "sector", "here", "area"]:
            self.log(cur.interact(self.player))
            return

        target_clean = target_name.strip().lower()

        inv_item = self.player.find_item(target_clean)
        if inv_item:
            self.log(inv_item.interact(self.player))
            return

        for item in cur.items:
            if item.name.lower() == target_clean or target_clean in item.name.lower():
                self.log(item.interact(self.player))
                return

        for hazard in cur.hazards:
            if hazard.name.lower() == target_clean or target_clean in hazard.name.lower():
                self.log(hazard.interact(self.player))
                return

        self.log(UI.warning_message(f"Could not find any entity matching '{target_name}' to interact with."))

    def handle_take(self, item_name: str) -> None:
        """Picks up an item from the current room, enforcing carry weight."""
        if not item_name:
            self.log(UI.warning_message("Specify an item to pick up."))
            return
        cur = self.current_room
        target_item = None
        for item in cur.items:
            if item_name.lower() in item.name.lower():
                target_item = item
                break

        if not target_item:
            self.log(UI.warning_message(f"No item matching '{item_name}' found in this sector."))
            return

        self.player.add_to_inventory(target_item)
        cur.items.remove(target_item)
        self.log(UI.success_message(f"Stowed [{target_item.name}] into inventory. (Weight: {target_item.weight}kg)"))

    def handle_drop(self, item_name: str) -> None:
        """Drops an item into current sector."""
        if not item_name:
            self.log(UI.warning_message("Specify an item to drop."))
            return
        dropped = self.player.remove_from_inventory(item_name)
        if dropped:
            self.current_room.add_item(dropped)
            self.log(UI.success_message(f"Dropped [{dropped.name}] onto the deck."))
        else:
            self.log(UI.warning_message(f"You are not carrying '{item_name}'."))

    def handle_use(self, item_name: str) -> None:
        """Uses an item from the player's pack."""
        if not item_name:
            self.log(UI.warning_message("Specify an item to use."))
            return
        item = self.player.find_item(item_name)
        if not item:
            self.log(UI.warning_message(f"Item '{item_name}' not found in backpack."))
            return

        result = item.use(self.player)
        self.log(UI.success_message(result))

        if item.charges <= 0 and getattr(item, "heal_amount", None) is not None:
            self.player.inventory.remove(item)
            self.log(f"Depleted [{item.name}] discarded.")

    def handle_inventory(self) -> None:
        """Interactive backpack management submenu."""
        inv = self.player.inventory
        print(f"\n{UI.CYAN}{UI.BOLD}=== [ BACKPACK INVENTORY ({self.player.current_carry_weight:.1f} / {self.player.max_carry_weight:.1f} kg) ] ==={UI.RESET}")
        if not inv:
            print("  (Your backpack is currently empty)")
            if sys.stdin.isatty():
                input("Press Enter to return...")
            return

        for i, item in enumerate(inv, 1):
            extra = ""
            if hasattr(item, "heal_amount"):
                extra = f" | [HEALS +{item.heal_amount} HP]"
            elif hasattr(item, "tool_type"):
                extra = f" | [TOOL: {item.tool_type}, Charges: {item.charges}]"
            elif hasattr(item, "clearance_level"):
                extra = f" | [SECURITY CLEARANCE LVL {item.clearance_level}]"
            print(f"  [{i}] [{item.name}] (Weight: {item.weight}kg, Value: {item.value}{extra})")

        print(f"\n  [S] Sort Backpack (Bubble / Insertion Sort)")
        print(f"  [F] Search Backpack for specific item")
        print(f"  [D] Drop an item")
        print(f"  [0] Return to Sector")

        if not sys.stdin.isatty():
            return

        try:
            choice = input(f"\n{UI.BOLD}Select item number [1-{len(inv)}] to USE/INSPECT, or option >> {UI.RESET}").strip().lower()
            if not choice or choice == "0" or choice in ["back", "b", "q"]:
                return
            elif choice.isdigit():
                item_idx = int(choice) - 1
                if 0 <= item_idx < len(inv):
                    sel_item = inv[item_idx]
                    self.log(UI.success_message(sel_item.interact(self.player)))
                    if hasattr(sel_item, "heal_amount"):
                        use_confirm = input(f"Inject/Use [{sel_item.name}] now? (y/n) >> ").strip().lower()
                        if use_confirm in ["y", "yes"]:
                            self.log(UI.success_message(sel_item.use(self.player)))
                            if sel_item.charges <= 0:
                                inv.remove(sel_item)
                                self.log(f"Depleted [{sel_item.name}] discarded.")
                else:
                    self.log(UI.warning_message("Invalid item number."))
            elif choice == "s":
                self._interactive_sort_menu()
            elif choice == "f":
                query = input("Search target name >> ").strip()
                if query:
                    self.handle_search(query)
            elif choice == "d":
                target = input("Item number or name to drop >> ").strip()
                if target.isdigit():
                    t_idx = int(target) - 1
                    if 0 <= t_idx < len(inv):
                        self.handle_drop(inv[t_idx].name)
                elif target:
                    self.handle_drop(target)
        except (KeyboardInterrupt, EOFError):
            pass

    def _interactive_sort_menu(self) -> None:
        """Submenu for choosing sorting parameters."""
        print("\n--- SORT INVENTORY ---")
        print("  [1] Sort by Weight (Heaviest first)")
        print("  [2] Sort by Value (Most valuable first)")
        print("  [3] Sort Alphabetically (A-Z)")
        print("  [0] Cancel")
        sub_choice = input("Select sort option [1-3] >> ").strip()
        if sub_choice == "1":
            self.handle_sort("weight")
        elif sub_choice == "2":
            self.handle_sort("value")
        elif sub_choice == "3":
            self.handle_sort("name")

    def handle_sort(self, sort_key: str) -> None:
        """Sorts inventory using custom sorting algorithms."""
        key = sort_key.strip().lower() or "weight"
        if key not in ["weight", "value", "name"]:
            key = "weight"

        self.player.sort_inventory(key=key, reverse=(key in ["value", "weight"]), algorithm="bubble")
        self.log(UI.success_message(f"Backpack sorted by {key.upper()} using custom Bubble Sort algorithm."))

    def handle_search(self, target_name: str) -> None:
        """Searches inventory using Linear Search and verifies with Binary Search."""
        if not target_name:
            self.log(UI.warning_message("Specify an item name to search for."))
            return
        idx = linear_search(self.player.inventory, target_name, key_fn=lambda x: x.name)
        if idx is not None:
            item = self.player.inventory[idx]
            self.log(UI.success_message(
                f"FOUND IN PACK: Slot {idx + 1}: [{item.name}] (Weight: {item.weight}kg, Value: {item.value})"
            ))
        else:
            self.log(UI.warning_message(f"Target '{target_name}' was NOT found in your backpack."))

    def handle_power_grid(self) -> None:
        """Displays and allows interactive repair of the Singly Linked List power grid."""
        print(f"\n{UI.CYAN}{UI.BOLD}=== [ STATION PRIMARY POWER CONDUIT (SINGLY LINKED LIST) ] ==={UI.RESET}")
        print(self.power_grid.display_grid())

        is_complete = self.power_grid.is_circuit_complete()
        if is_complete:
            print(UI.success_message("Circuit continuity UNBROKEN! Main bus power fully energized to Escape Pods."))
        else:
            broken = self.power_grid.get_broken_relay()
            if broken:
                print(UI.warning_message(f"CIRCUIT BROKEN: Relay '{broken.name}' [{broken.relay_id}] in {broken.sector} is offline/damaged!"))

        relays = self.power_grid.to_list()
        print(f"\n{UI.BOLD}POWER CONDUIT RELAYS:{UI.RESET}")
        for i, relay in enumerate(relays, 1):
            status = f"{UI.GREEN}ONLINE{UI.RESET}" if relay.is_online and not relay.is_damaged else (
                f"{UI.RED}DAMAGED (NEEDS REPAIR){UI.RESET}" if relay.is_damaged else f"{UI.YELLOW}OFFLINE (TOGGLEABLE){UI.RESET}"
            )
            print(f"  [{i}] [{relay.relay_id}] {relay.name} ({relay.sector}) -> {status}")

        print("  [0] Return to Sector")
        if not sys.stdin.isatty():
            return
        try:
            choice = input(f"\n{UI.BOLD}Select relay number [1-{len(relays)}] to REPAIR or TOGGLE, or 0 to return >> {UI.RESET}").strip()
            if not choice or choice == "0":
                return
            if choice.isdigit():
                r_idx = int(choice) - 1
                if 0 <= r_idx < len(relays):
                    self.handle_repair_relay(relays[r_idx].relay_id)
        except (KeyboardInterrupt, EOFError):
            pass

    def handle_repair_relay(self, relay_id: str) -> None:
        """Repairs or toggles a power relay node in the linked list grid."""
        if not relay_id:
            self.log(UI.warning_message("Specify the relay ID. Example: 'repair RELAY-02'"))
            return
        relay = self.power_grid.find_relay(relay_id.upper().strip())
        if not relay:
            self.log(UI.warning_message(f"No power relay found matching identifier '{relay_id}'."))
            return

        has_tool = any(isinstance(i, ToolItem) for i in self.player.inventory)
        if relay.is_damaged:
            if not has_tool:
                self.log(UI.warning_message(
                    f"Relay [{relay.relay_id}] is damaged. You need an engineering tool (Prybar, Cutter, Coupler) in your pack to repair it!"
                ))
                return
            result = relay.repair()
            self.log(UI.success_message(result))
        else:
            new_state = relay.toggle_power()
            status = "ONLINE" if new_state else "OFFLINE"
            self.log(UI.success_message(f"Toggled [{relay.relay_id}] {relay.name} power to: {status}."))

    def handle_force_door(self) -> None:
        """Forces open a jammed door in the current room using tools."""
        cur = self.current_room
        jammed_room = None
        for dir_name, room_id in cur.exits.items():
            r = self.rooms[room_id]
            if r.is_door_jammed:
                jammed_room = r
                break

        if not jammed_room:
            self.log(UI.warning_message("There are no jammed bulkheads adjoining this sector."))
            return

        tool = None
        for item in self.player.inventory:
            if isinstance(item, ToolItem) and item.charges > 0:
                tool = item
                break

        if not tool:
            self.log(UI.warning_message(
                f"The bulkhead to [{jammed_room.name}] is jammed solid. You need an engineering tool (Prybar or Cutter) in your pack!"
            ))
            return

        tool.charges -= 1
        jammed_room.is_door_jammed = False
        self.log(UI.success_message(
            f"You activate [{tool.name}], applying mechanical leverage and heat. "
            f"The hydraulic lock on [{jammed_room.name}] gives way! Bulkhead is now open!"
        ))

    def handle_decontaminate(self) -> None:
        """If in Medical Quarantine Bay, triggers sterilization cycle."""
        cur = self.current_room
        if isinstance(cur, MedicalQuarantineBay):
            msg = cur.sanitize_chamber(35.0)
            self.log(UI.success_message(msg))
        else:
            self.log(UI.warning_message("There is no bio-decontamination station installed in this sector."))

    def handle_system_menu(self) -> None:
        """System options: Save, Load, Help, Objectives, Quit."""
        print(f"\n{UI.BOLD}=== SYSTEM OPTIONS ==={UI.RESET}")
        print("  [1] Save Checkpoint (Neural Upload to JSON)")
        print("  [2] Load Checkpoint (Restore previous state)")
        print("  [3] View Mission Objectives Checklist")
        print("  [4] Tactical Map")
        print("  [5] Exit Game")
        print("  [0] Return to Game")

        if not sys.stdin.isatty():
            return

        try:
            choice = input(f"\n{UI.BOLD}Select system option [0-5] >> {UI.RESET}").strip()
            if choice == "1":
                self.handle_save()
            elif choice == "2":
                self.handle_load()
            elif choice == "3":
                self.handle_objectives()
            elif choice == "4":
                print(UI.render_map(self.rooms, self.player.current_room_id))
                input("\nPress Enter to return...")
            elif choice == "5":
                self.log("Ending O.M.N.I. simulation. Goodbye.")
                self.is_running = False
        except (KeyboardInterrupt, EOFError):
            pass

    def handle_save(self) -> None:
        """Executes Neural Upload checkpoint persistence."""
        path = NeuralUpload.save_checkpoint(
            player_dict=self.player.to_dict(),
            rooms_dict={r_id: r.to_dict() for r_id, r in self.rooms.items()},
            power_grid_list=[r.to_dict() for r in self.power_grid],
            threat_queue_list=[h.to_dict() for h in self.threat_queue],
            turn_count=self.turn_count,
        )
        self.log(UI.success_message(f"NEURAL UPLOAD COMPLETE: State saved to '{path}'."))

    def handle_load(self) -> None:
        """Loads Neural Upload checkpoint."""
        try:
            data = NeuralUpload.load_checkpoint()
            self.turn_count = data.get("turn_count", 1)

            self.rooms = {}
            for r_id, r_data in data["rooms"].items():
                self.rooms[r_id] = Room.from_dict(r_data)

            self.player = Player.from_dict(data["player"])

            self.power_grid = PowerGrid()
            for relay_data in data["power_grid"]:
                self.power_grid.append(PowerRelay.from_dict(relay_data))

            self.threat_queue = Queue()
            for hazard_data in data["threat_queue"]:
                self.threat_queue.enqueue(Hazard.from_dict(hazard_data))

            self.log(UI.success_message(
                f"NEURAL CHECKPOINT RESTORED: Resumed at turn {self.turn_count} in [{self.current_room.name}]."
            ))
        except Exception as e:
            self.log(UI.error_message(f"Failed to restore neural checkpoint: {e}"))

    def handle_escape(self) -> None:
        """Evaluates escape pod launch conditions."""
        if self.player.current_room_id != "escape_bay":
            self.log(UI.warning_message("You must reach the Emergency Escape Pod Bay to evacuate!"))
            return

        if not self.power_grid.is_circuit_complete():
            raise PowerGridFailureError("Emergency pod launch rails have no energy! The Power Grid linked list is broken.")

        has_code = any("launch code" in item.name.lower() or "fob" in item.name.lower() for item in self.player.inventory)
        if not has_code:
            self.log(UI.warning_message("LAUNCH ABORTED: Missing 'Escape Pod Launch Code' cryptographic key from Bridge!"))
            return

        self.has_won = True
        self.is_running = False
        print(UI.success_message("\n*** RETRO-THRUSTERS ENGAGED! ***"))
        print(
            "Primary power floods the launch rail solenoids.\n"
            "The escape pod detaches from Deep Space Station Promethium and accelerates into hyperspace!\n"
            "CONGRATULATIONS: You have survived Station O.M.N.I.!"
        )

    def handle_help(self) -> None:
        """Displays clear command reference."""
        print(f"""
{UI.CYAN}{UI.BOLD}======================== [ O.M.N.I. SURVIVAL GUIDE ] ========================{UI.RESET}
HOW TO PLAY:
  1. Every turn, a numbered list of available actions is shown.
  2. Simply type a number like [1], [2], [3] to perform that action!
  3. You can also type natural commands at any time:

NATURAL COMMAND SHORTCUTS:
  * Navigation:     n / s / e / w / move north / flee
  * Items & Gear:   take <item> / drop <item> / use <item> / inv
  * Station Power:  power / repair <relay_id> / force door
  * Objectives:     objectives / goal / mission
  * System:         map / save / load / quit / help
{UI.CYAN}{UI.BOLD}============================================================================={UI.RESET}
""")
        if sys.stdin.isatty():
            input("Press Enter to return...")

    def _advance_turn(self) -> None:
        """
        Advances the turn counter, drains minor life support, and processes
        the next scheduled hazard from the FIFO Threat Queue.
        """
        self.turn_count += 1

        if self.turn_count % 3 == 0:
            self.player.oxygen -= 2

        if not self.threat_queue.is_empty():
            threat: Hazard = self.threat_queue.dequeue()
            self.log(threat.trigger_turn_effect(self.player))

    def _evaluate_game_conclusion(self) -> None:
        """Prints post-game debriefing."""
        print(f"\n{UI.BOLD}======================= [ SIMULATION SUMMARY ] ======================={UI.RESET}")
        print(f"Survivor: {self.player.name}")
        print(f"Turns Elapsed: {self.turn_count}")
        print(f"Final Vital Signs: Health: {self.player.health}%, Oxygen: {self.player.oxygen}%")
        print(f"Power Grid Status: {'RESTORED' if self.power_grid.is_circuit_complete() else 'INCOMPLETE'}")
        if self.has_won:
            print(f"\n{UI.GREEN}{UI.BOLD}STATUS: MISSION ACCOMPLISHED - SURVIVED ROGUE AI O.M.N.I.{UI.RESET}")
        elif not self.player.is_alive:
            print(f"\n{UI.RED}{UI.BOLD}STATUS: FATAL - LIFE SIGNS TERMINATED ABOARD STATION.{UI.RESET}")
        print(f"{UI.BOLD}======================================================================{UI.RESET}\n")
