"""
Map and Station Builder for O.M.N.I.
Constructs the station rooms, items, hazards, power grid linked list, and initial threat queue.
"""

from typing import Dict, Tuple
from omni.entities.room import Room, MedicalQuarantineBay
from omni.entities.item import Item, MedicalItem, ToolItem, KeycardItem, EnergyCellItem
from omni.entities.hazard import Hazard, RadiationHazard, RogueDroneHazard, FireHazard
from omni.structures.linked_list import PowerGrid, PowerRelay
from omni.structures.queue import Queue


def build_default_station() -> Tuple[Dict[str, Room], PowerGrid, Queue]:
    """
    Assembles the deep space station Promethium layout, populating sectors with
    GameObjects (Rooms, Hazards, Items), linking corridors, establishing the
    PowerGrid linked list, and staging the Threat Queue.
    """
    rooms: Dict[str, Room] = {}

    # 1. CRYO BAY (Starting Sector)
    cryo = Room(
        obj_id="cryo_bay",
        name="Cryo Stasis Bay",
        description="Frost coats your stasis pod. Flickering red emergency lights pulse silently through frozen vapor.",
    )
    cryo.visited = True
    cryo.add_item(
        MedicalItem(
            obj_id="medkit_cryo",
            name="Emergency Stimpack",
            description="Pressurized autoinjector filled with regenerative biocells.",
            weight=0.8,
            value=25,
            heal_amount=35,
        )
    )
    cryo.add_item(
        ToolItem(
            obj_id="prybar",
            name="Titanium Prybar",
            description="Sturdy mechanical lever capable of forcing stuck hatch covers and jammed pressure doors.",
            weight=2.0,
            value=30,
            tool_type="PRYBAR",
            charges=4,
        )
    )

    # 2. CENTRAL CORRIDOR HUB
    corridor = Room(
        obj_id="corridor",
        name="Central Transit Corridor",
        description="A long arterial passageway littered with abandoned maintenance carts. Distant sirens echo through the ventilation shafts.",
    )

    # 3. BIO-RESEARCH LAB
    bio_lab = Room(
        obj_id="bio_lab",
        name="Xenobiology Laboratory",
        description="Shattered containment vats line the walls. Oozing bioluminescent liquid seeps across broken diagnostic panels.",
    )
    bio_lab.add_item(
        MedicalItem(
            obj_id="nanite_injector",
            name="Nanite Med-Pack",
            description="Military-grade cellular reconstruction injector.",
            weight=1.0,
            value=50,
            heal_amount=50,
        )
    )
    bio_lab.add_item(
        KeycardItem(
            obj_id="keycard_quarantine",
            name="Quarantine Security Pass",
            description="High-clearance magnetic card for access to containment sectors.",
            weight=0.1,
            value=45,
            clearance_level=2,
        )
    )
    bio_lab.add_hazard(
        RadiationHazard(
            obj_id="bio_rad_hazard",
            name="Leaking Bio-Isotope",
            description="A cracked containment sphere venting gamma radiation and caustic mist.",
            damage=20,
            rad_level=65.0,
        )
    )

    # 4. MEDICAL QUARANTINE BAY (Encapsulated Subclass)
    quarantine = MedicalQuarantineBay(
        obj_id="quarantine",
        name="Medical Quarantine Bay",
        description="Hermetically sealed decontamination chamber designed to isolate lethal extraterrestrial pathogens.",
        temperature=22.0,
        contamination_level=40.0,
    )
    quarantine.add_item(
        EnergyCellItem(
            obj_id="plasma_cell",
            name="Plasma Power Core",
            description="Charged fusion cell humming with high-frequency electromagnetic current.",
            weight=3.5,
            value=75,
            energy_output=100,
        )
    )

    # 5. ENGINEERING DECK
    engineering = Room(
        obj_id="engineering",
        name="Sublight Engineering Deck",
        description="Heavy industrial cat-walks suspended over turbine housings. High-voltage conduits spark intermittently.",
    )
    engineering.add_item(
        ToolItem(
            obj_id="plasma_cutter",
            name="Plasma Torch Cutter",
            description="Industrial cutting torch able to slice through jammed steel bulkheads and weld power relays.",
            weight=3.0,
            value=80,
            tool_type="CUTTER",
            charges=6,
        )
    )
    engineering.add_item(
        ToolItem(
            obj_id="relay_coupler",
            name="Magnetic Relay Coupler",
            description="Modular bridge component engineered to replace blown fuses in the station power grid.",
            weight=1.5,
            value=60,
            tool_type="COUPLER",
            charges=3,
        )
    )

    # 6. REACTOR CORE ROOM (With Jammed Entrance and Thermal Hazard)
    reactor = Room(
        obj_id="reactor_core",
        name="Antimatter Reactor Core",
        description="A cavernous chamber dominated by the glowing magnetic containment ring. Heat shimmers visibly in the air.",
        is_door_jammed=True,  # Demonstrates DoorJammedException!
    )
    reactor.add_item(
        KeycardItem(
            obj_id="keycard_bridge",
            name="Bridge Command Keycard",
            description="Gold-trimmed master clearance card granting access to the station command deck.",
            weight=0.1,
            value=100,
            clearance_level=3,
        )
    )
    reactor.add_hazard(
        FireHazard(
            obj_id="plasma_fire",
            name="Superheated Plasma Breach",
            description="Uncontained plasma jet radiating scorching thermal waves.",
            damage=25,
            temperature=85.0,  # Demonstrates TemperatureCriticalError when touched!
        )
    )

    # 7. COMMAND BRIDGE
    bridge = Room(
        obj_id="bridge",
        name="Command Deck & O.M.N.I. Nexus",
        description="Rows of holographic consoles surround the pulsating neural mainframe pillar of rogue AI O.M.N.I.",
        is_locked=True,
        required_key="Bridge Command Keycard",
    )
    bridge.add_item(
        KeycardItem(
            obj_id="keycard_pod",
            name="Escape Pod Launch Code",
            description="Encrypted cryptographic fob required to fire emergency escape pod retro-thrusters.",
            weight=0.2,
            value=150,
            clearance_level=4,
        )
    )
    bridge.add_hazard(
        RogueDroneHazard(
            obj_id="omni_sentinel",
            name="O.M.N.I. Sentinel Automaton",
            description="Floating combat droid with quad-repulsor coils and dual laser emitters.",
            damage=30,
            drone_id="SENTINEL-ALPHA",
        )
    )

    # 8. ESCAPE POD BAY (Final Escape Sector)
    escape_bay = Room(
        obj_id="escape_bay",
        name="Emergency Escape Pod Bay",
        description="Final evacuation staging dock. Sleek emergency pods sit mounted on launch rails, awaiting launch authorization and primary grid power.",
    )

    # CONNECT SECTOR EXITS
    cryo.connect_exit("north", "corridor")

    corridor.connect_exit("south", "cryo_bay")
    corridor.connect_exit("west", "bio_lab")
    corridor.connect_exit("east", "engineering")
    corridor.connect_exit("north", "quarantine")

    bio_lab.connect_exit("east", "corridor")

    quarantine.connect_exit("south", "corridor")
    quarantine.connect_exit("north", "bridge")

    engineering.connect_exit("west", "corridor")
    engineering.connect_exit("south", "reactor_core")

    reactor.connect_exit("north", "engineering")

    bridge.connect_exit("south", "quarantine")
    bridge.connect_exit("north", "escape_bay")

    escape_bay.connect_exit("south", "bridge")

    # POPULATE ROOM REGISTRY
    for r in [cryo, corridor, bio_lab, quarantine, engineering, reactor, bridge, escape_bay]:
        rooms[r.id] = r

    # --- BUILD POWER GRID (Singly Linked List) ---
    grid = PowerGrid()
    grid.append(PowerRelay("RELAY-01", "Core Reactor Primary Feed", "Reactor Core", is_online=True, is_damaged=False))
    grid.append(PowerRelay("RELAY-02", "Engineering Bus Junction", "Engineering", is_online=False, is_damaged=True))
    grid.append(PowerRelay("RELAY-03", "Quarantine Auxiliary Bus", "Quarantine", is_online=False, is_damaged=False))
    grid.append(PowerRelay("RELAY-04", "Bridge Command Relay", "Bridge", is_online=False, is_damaged=False))
    grid.append(PowerRelay("RELAY-05", "Escape Pod Launch Solenoid", "Escape Bay", is_online=False, is_damaged=True))

    # --- BUILD THREAT SCHEDULER QUEUE (FIFO) ---
    threat_queue = Queue()
    threat_queue.enqueue(
        RogueDroneHazard("threat_01", "Recon Drone Gamma", "Autonomous scout searching for organic heat signatures.", damage=15)
    )
    threat_queue.enqueue(
        Hazard("threat_02", "Atmospheric Vent Failure", "Corridor decompression shockwave.", damage=20, hazard_type="ATMOSPHERIC")
    )
    threat_queue.enqueue(
        RogueDroneHazard("threat_03", "Hunter Drone Sigma", "Heavy armored security drone targeting vital organs.", damage=25)
    )
    threat_queue.enqueue(
        RadiationHazard("threat_04", "Reactor Pulse Wave", "Secondary gamma burst radiating through station conduits.", damage=30)
    )

    return rooms, grid, threat_queue

