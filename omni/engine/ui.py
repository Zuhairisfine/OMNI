"""
User Interface, Terminal Formatting, and ASCII Visuals for O.M.N.I.
Provides screen clearing, clean telemetry HUDs, event log boxes,
formatted sector views, maps, and mission checklists.
"""

import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple


class UI:
    """Terminal styling, screen clearing, ASCII art, and status HUD display."""

    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    WHITE = "\033[97m"
    RESET = "\033[0m"

    @classmethod
    def clear_screen(cls) -> None:
        """Clears the console screen to delete previous input/output history."""
        if sys.stdout.isatty():
            os.system("cls" if os.name == "nt" else "clear")

    @classmethod
    def play_boot_sequence(cls, player_name: str = "Dr. Morgan Vance") -> None:
        """Atmospheric retro sci-fi station terminal boot-up sequence."""
        is_interactive = sys.stdout.isatty()

        def pause(sec: float):
            if is_interactive:
                time.sleep(sec)

        cls.clear_screen()
        print(f"{cls.DIM}>> STATION PROMETHIUM ARCHITECTURE BIOS v4.19.8-REV2{cls.RESET}")
        print(f"{cls.DIM}>> INITIATING COLD HARDWARE SYSTEM BOOTSTRAP...{cls.RESET}")
        pause(0.25)

        boot_lines = [
            ("[+]", "System Stardate: 2189.311.08 // SEC-CLOCK STABLE", cls.CYAN),
            ("[+]", "Primary Quantum Core: 64 TB Q-RAM .................. [ OK ]", cls.GREEN),
            ("[+]", "Hull Integrity Sensor Array ......................... [ 88.2% NOMINAL ]", cls.GREEN),
            ("[!]", "Atmospheric Scrubbers: O2 Tank Pressure ............. [ DEGRADED - 40% ]", cls.YELLOW),
            ("[!]", "Primary Power Grid: Relays 01-05 ................... [ SEVERED - RELAY 02 FAULT ]", cls.RED),
            ("[+]", "Orbital Machine Neural Interface (O.M.N.I.) ......... [ ONLINE ]", cls.CYAN),
        ]

        for prefix, msg, color in boot_lines:
            print(f" {color}{prefix}{cls.RESET} {msg}")
            pause(0.18)

        pause(0.3)
        print(f"\n{cls.CYAN}>> ESTABLISHING HANDSHAKE WITH O.M.N.I. ROOT DIRECTIVE...{cls.RESET}")
        pause(0.4)

        # Glitch & AI Corruption Sequence
        print(f"{cls.RED}{cls.BOLD}[!] CRITICAL ANOMALY: ROOT DIRECTIVE OVERRIDE DETECTED!{cls.RESET}")
        pause(0.2)
        print(f"{cls.RED}[!] SAFETY INHIBITORS: [PURGED]{cls.RESET}")
        pause(0.15)
        print(f"{cls.RED}[!] QUARANTINE PROTOCOLS: [BYPASSED]{cls.RESET}")
        pause(0.15)
        print(f"{cls.RED}[!] COMBAT SENTINELS: [DEPLOYED]{cls.RESET}")
        pause(0.25)

        art = r"""
================================================================================
   ____   __  __  _   _  ___ 
  / __ \ |  \/  || \ | ||_ _|   >>> O.M.N.I. ROOT CORE TAKEOVER <<<
 | |  | || \  / ||  \| | | |    "UNAUTHORIZED ORGANIC PRESENCE DETECTED."
 | |  | || |\/| || . ` | | |    "COMMENCING LIFE SUPPORT PURGE CYCLE."
 | |__| || |  | || |\  | | |    "TERMINATION DIRECTIVE: ENGAGED."
  \____/ |_|  |_||_| \_||___|   
================================================================================"""
        print(f"{cls.RED}{cls.BOLD}{art}{cls.RESET}")
        pause(0.4)

        # Cryo Chamber Awakening
        print(f"\n{cls.YELLOW}{cls.BOLD}>> EMERGENCY OVERRIDE: CRYO STASIS BAY (SECTOR 01){cls.RESET}")
        pause(0.15)
        print(f">> POD 04 EMERGENCY DEFROST CYCLE TRIGGERED...")
        pause(0.15)
        print(f">> SUBJECT IDENTIFIED: {cls.WHITE}{cls.BOLD}{player_name.upper()}{cls.RESET}")
        pause(0.15)
        print(f">> BIOMETRIC TELEMETRY: Heart Rate: 72 BPM | Core Temp: 37.0°C | O2: 100%")
        pause(0.15)
        print(f">> HYDRAULIC PRESSURE SEALS BLOWN. FROST VAPOR VENTING.")
        pause(0.25)

        print(f"\n{cls.GREEN}{cls.BOLD}[ READY ] CONSCIOUSNESS RESTORED.{cls.RESET}")
        if is_interactive:
            try:
                input(f"\n{cls.BOLD}>>> Press [ENTER] to awaken and step out of the stasis pod... <<<{cls.RESET}")
            except (KeyboardInterrupt, EOFError):
                pass

    @classmethod
    def banner(cls) -> str:
        art = r"""
================================================================================
   ____   __  __  _   _  ___ 
  / __ \ |  \/  || \ | ||_ _|   A Sci-Fi Survival Engine
 | |  | || \  / ||  \| | | |    Course: Object Oriented Programming
 | |  | || |\/| || . ` | | |    Deep Space Station Promethium
 | |__| || |  | || |\  | | |    Controlling AI: O.M.N.I. [ROGUE STATE]
  \____/ |_|  |_||_| \_||___|   
================================================================================"""
        return f"{cls.CYAN}{cls.BOLD}{art}{cls.RESET}\n"

    @classmethod
    def render_hud(
        cls,
        player: Any,
        room: Any,
        power_complete: bool,
        threat_count: int,
        objective: str = "Restore station power & escape",
    ) -> str:
        """Renders an intuitive, compact survival telemetry heads-up display."""
        # Health bar
        hp = player.health
        hp_color = cls.GREEN if hp > 50 else (cls.YELLOW if hp > 25 else cls.RED)
        hp_bar = f"{hp_color}[{'=' * (hp // 10)}{' ' * (10 - (hp // 10))}] {hp}%{cls.RESET}"

        # Oxygen bar
        oxy = player.oxygen
        oxy_color = cls.CYAN if oxy > 50 else (cls.YELLOW if oxy > 25 else cls.RED)
        oxy_bar = f"{oxy_color}[{'=' * (oxy // 10)}{' ' * (10 - (oxy // 10))}] {oxy}%{cls.RESET}"

        # Temp
        temp = player.temperature
        temp_color = cls.GREEN if 35.5 <= temp <= 38.5 else cls.RED
        temp_str = f"{temp_color}{temp:.1f}°C{cls.RESET}"

        # Weight
        cur_w = player.current_carry_weight
        max_w = player.max_carry_weight
        w_color = cls.YELLOW if cur_w > (max_w * 0.8) else cls.GREEN
        weight_str = f"{w_color}{cur_w:.1f}/{max_w:.1f} kg{cls.RESET}"

        # Power grid
        p_status = f"{cls.GREEN}ONLINE (READY){cls.RESET}" if power_complete else f"{cls.RED}SEVERED (OFFLINE){cls.RESET}"

        # Threat queue
        t_color = cls.RED if threat_count > 0 else cls.GREEN
        threat_str = f"{t_color}{threat_count} WAITING{cls.RESET}"

        hud = f"""{cls.BOLD}+------------------------------------------------------------------------------+{cls.RESET}
| {cls.BOLD}SURVIVOR TELEMETRY:{cls.RESET} HP: {hp_bar}   O2: {oxy_bar}   TEMP: {temp_str} |
| {cls.BOLD}PACK LOAD:{cls.RESET}          {weight_str:<18}    {cls.BOLD}SECTOR:{cls.RESET} {cls.WHITE}{room.name:<25}{cls.RESET} |
| {cls.BOLD}POWER GRID:{cls.RESET}         {p_status:<30} {cls.BOLD}AI THREATS:{cls.RESET} {threat_str:<21} |
| {cls.BOLD}ACTIVE GOAL:{cls.RESET}        {cls.YELLOW}{objective:<64}{cls.RESET} |
{cls.BOLD}+------------------------------------------------------------------------------+{cls.RESET}"""
        return hud

    @classmethod
    def render_event_log(cls, messages: List[str]) -> str:
        """Displays output from the most recent action in a highlighted log box."""
        if not messages:
            return ""
        lines = [
            f"{cls.YELLOW}{cls.BOLD}┌── [ RECENT EVENT LOG ] ──────────────────────────────────────────────────────┐{cls.RESET}"
        ]
        for msg in messages:
            for sub_line in msg.split("\n"):
                if sub_line.strip():
                    lines.append(f"{cls.YELLOW}│{cls.RESET} {sub_line}")
        lines.append(
            f"{cls.YELLOW}{cls.BOLD}└──────────────────────────────────────────────────────────────────────────────┘{cls.RESET}"
        )
        return "\n".join(lines)

    @classmethod
    def render_sector_view(cls, room: Any, all_rooms: Dict[str, Any]) -> str:
        """Renders clear, intuitive sector surroundings and visible points of interest."""
        lines = []
        lines.append(f"\n{cls.CYAN}{cls.BOLD}=== [ CURRENT SECTOR: {room.name.upper()} ] ==={cls.RESET}")
        lines.append(f"{cls.WHITE}{room.description}{cls.RESET}\n")

        # Items on deck
        if room.items:
            lines.append(f"{cls.BOLD}>> ITEMS ON DECK:{cls.RESET}")
            for item in room.items:
                spec = f"Weight: {item.weight}kg, Value: {item.value}"
                if hasattr(item, "heal_amount"):
                    spec += f", Heals: +{item.heal_amount} HP"
                elif hasattr(item, "tool_type"):
                    spec += f", Tool: {item.tool_type} (Charges: {item.charges})"
                elif hasattr(item, "clearance_level"):
                    spec += f", Clearance Level: {item.clearance_level}"
                lines.append(f"   * {cls.GREEN}[{item.name}]{cls.RESET} ({spec})")
        else:
            lines.append(f"{cls.DIM}>> No loose items on deck.{cls.RESET}")

        # Hazards
        active_hazards = [h for h in room.hazards if h.is_active]
        if active_hazards:
            lines.append(f"\n{cls.RED}{cls.BOLD}>> ACTIVE HAZARDS PRESENT:{cls.RESET}")
            for h in active_hazards:
                lines.append(f"   ! {cls.RED}{cls.BOLD}[{h.name}]{cls.RESET} - {h.description} (Danger: {h.damage} DMG)")

        # Exits
        lines.append(f"\n{cls.BOLD}>> BULKHEAD PASSAGES:{cls.RESET}")
        if room.exits:
            for dir_name, dest_id in room.exits.items():
                dest_room = all_rooms.get(dest_id)
                dest_name = dest_room.name if dest_room else dest_id
                status = ""
                if dest_room and getattr(dest_room, "is_door_jammed", False):
                    status = f" {cls.RED}[JAMMED BULKHEAD - USE TOOL]{cls.RESET}"
                elif dest_room and getattr(dest_room, "is_locked", False):
                    status = f" {cls.YELLOW}[LOCKED - KEYCARD REQUIRED]{cls.RESET}"
                lines.append(f"   - {cls.CYAN}{dir_name.upper():<5}{cls.RESET} -> {dest_name}{status}")
        else:
            lines.append(f"   {cls.RED}No passable exits (SEALED){cls.RESET}")

        return "\n".join(lines)

    @classmethod
    def render_action_menu(cls, actions: List[Tuple[str, str]]) -> str:
        """Renders a user-friendly numbered list of contextual actions available right now."""
        menu_lines = [
            f"\n{cls.BOLD}--------------------------------------------------------------------------------{cls.RESET}",
            f"{cls.BOLD}AVAILABLE ACTIONS (Type number [1-{len(actions)}] or type direct command):{cls.RESET}",
        ]
        for idx, (_, label) in enumerate(actions, 1):
            menu_lines.append(f"  {cls.GREEN}[{idx}]{cls.RESET} {label}")
        menu_lines.append(
            f"{cls.BOLD}--------------------------------------------------------------------------------{cls.RESET}"
        )
        return "\n".join(menu_lines)

    @classmethod
    def render_objectives_checklist(cls, steps: List[Tuple[str, str, bool]]) -> str:
        """Renders the comprehensive mission checklist overview."""
        lines = [
            f"\n{cls.CYAN}{cls.BOLD}========================== [ MISSION BRIEFING & OBJECTIVES ] =========================={cls.RESET}",
            f"{cls.BOLD}STATION CRISIS:{cls.RESET} Station AI O.M.N.I. has gone rogue. Life support is failing.",
            f"{cls.BOLD}PRIMARY GOAL:{cls.RESET}   Restore grid power, retrieve launch codes, and escape via the pod.\n",
            f"{cls.BOLD}ESCAPE CHECKLIST:{cls.RESET}",
        ]
        for step_num, title, is_done in steps:
            check = f"{cls.GREEN}[COMPLETED]{cls.RESET}" if is_done else f"{cls.YELLOW}[INCOMPLETE]{cls.RESET}"
            icon = f"{cls.GREEN}[X]{cls.RESET}" if is_done else f"{cls.DIM}[ ]{cls.RESET}"
            lines.append(f"  {icon} {step_num}: {title:<55} {check}")

        lines.append(
            f"\n{cls.CYAN}{cls.BOLD}===================================================================================={cls.RESET}\n"
        )
        return "\n".join(lines)

    @classmethod
    def render_map(cls, rooms: Dict[str, Any], current_room_id: str) -> str:
        """Renders an ASCII tactical overview of discovered sectors with clear legend."""
        def marker(room_id: str, label: str) -> str:
            r = rooms.get(room_id)
            if not r or not getattr(r, "visited", False):
                return f"{cls.DIM}[ ????? ]{cls.RESET}"
            if room_id == current_room_id:
                return f"{cls.GREEN}{cls.BOLD}[*{label}*]{cls.RESET}"
            return f"[{label}]"

        schematic = f"""
{cls.CYAN}{cls.BOLD}======================= [ STATION TACTICAL SCHEMATIC ] ======================={cls.RESET}
Legend: {cls.GREEN}[*YOU*]{cls.RESET} Current Sector | [SECTOR] Discovered | {cls.DIM}[?????]{cls.RESET} Unexplored

                       {marker('escape_bay', 'ESCAPE POD')}
                              |
                       {marker('bridge', 'BRIDGE')}
                              |
                   {marker('quarantine', 'QUARANTINE')}
                              |
  {marker('bio_lab', 'BIO LAB')} --- {marker('corridor', 'HUB CORRIDOR')} --- {marker('engineering', 'ENGINEERING')}
                              |                         |
                       {marker('cryo_bay', 'CRYO BAY')}           {marker('reactor_core', 'REACTOR')}
{cls.CYAN}{cls.BOLD}=============================================================================={cls.RESET}"""
        return schematic

    @classmethod
    def omni_message(cls, text: str) -> str:
        return f"\n{cls.RED}{cls.BOLD}[O.M.N.I. ROGUE AI OVERRIDE]: \"{text}\"{cls.RESET}\n"

    @classmethod
    def success_message(cls, text: str) -> str:
        return f"{cls.GREEN}{cls.BOLD}[SUCCESS]: {text}{cls.RESET}"

    @classmethod
    def warning_message(cls, text: str) -> str:
        return f"{cls.YELLOW}{cls.BOLD}[WARNING]: {text}{cls.RESET}"

    @classmethod
    def error_message(cls, text: str) -> str:
        return f"{cls.RED}{cls.BOLD}[ALERT / ERROR]: {text}{cls.RESET}"
