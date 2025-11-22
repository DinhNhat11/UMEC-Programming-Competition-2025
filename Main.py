import math
import random
import csv
import os
from collections import defaultdict

# ==========================================
# CONFIGURATION
# ==========================================
CSV_FILENAME = "emergency_events.csv" 

# Define station types and their capabilities
STATION_TYPES = {
    'fire': ['fire', 'medical'],
    'police': ['police'],
    'paramedic': ['medical', 'police']
}

# Station definitions
STATIONS = {
    -1: {'type': 'fire', 'x': 50, 'y': 60},
    -2: {'type': 'fire', 'x': 150, 'y': 140},
    -3: {'type': 'police', 'x': 100, 'y': 50},
    -4: {'type': 'police', 'x': 100, 'y': 150},
    -5: {'type': 'paramedic', 'x': 50, 'y': 160},
    -6: {'type': 'paramedic', 'x': 150, 'y': 40}
}

NUM_RESPONDERS = len(STATIONS)
RESPONDER_TO_STATION = {0: -1, 1: -2, 2: -3, 3: -4, 4: -5, 5: -6}

RETURN_TO_BASE = True
MAX_ROUTE_COST = 2000.0 
# LOWEST_PRIORITY_TO_IGNORE = 1 

# Severity Mapping
PRIORITY_MAP = {30: 10, 60: 8, 120: 5, 300: 3, 600: 1}
SEVERITY_WEIGHTS = {1: 1.0, 2: 1.2, 3: 1.5, 4: 2.0, 5: 2.5,
                    6: 3.0, 7: 4.0, 8: 5.0, 9: 7.5, 10: 10.0}

# ==========================================
# GLOBAL STATE
# ==========================================
ALL_NODES = {}
for sid, station in STATIONS.items():
    ALL_NODES[sid] = [sid, station['x'], station['y'], 0, 0, 'station']

UNVISITED_NODE_IDS = set()
PENDING_EMERGENCIES = []

RESPONDER_LOCATIONS = {0: -1, 1: -2, 2: -3, 3: -4, 4: -5, 5: -6}
RESPONDER_COSTS = {r: 0.0 for r in range(NUM_RESPONDERS)}
RESPONDER_POINTS = {r: 0 for r in range(NUM_RESPONDERS)}

# Track active routes - when responder will arrive at destination
RESPONDER_ROUTES = {}  # {responder_id: (destination_node, arrival_time)}

TOTAL_EMERGENCIES_HANDLED = 0
DIST_CACHE = {}  # Pre-compute distances between stations

# ==========================================
# DATA LOADING
# ==========================================

def load_csv_data():
    """Reads the external CSV file and parses it into memory."""
    global PENDING_EMERGENCIES
    
    if not os.path.exists(CSV_FILENAME):
        print(f"ERROR: Could not find '{CSV_FILENAME}' in this folder.")
        return False

    try:
        with open(CSV_FILENAME, 'r') as f:
            reader = csv.DictReader(f)
            events = []
            
            for row in reader:
                try:
                    p_seconds = int(float(row['priority_s']))
                except ValueError:
                    p_seconds = 600
                
                severity = PRIORITY_MAP.get(p_seconds, 3)
                base_points = 100 - (p_seconds // 10)
                if base_points < 10: base_points = 10

                emergency_type = row.get('etype', 'medical').lower()
                spawn_time = float(row.get('t', 0))
                
                event = [
                    spawn_time,
                    int(row['id']),
                    float(row['x']),
                    float(row['y']),
                    base_points,
                    severity,
                    emergency_type
                ]
                events.append(event)
            
            events.sort(key=lambda e: e[0])
            
            for event in events:
                spawn_time = event[0]
                node = event[1:]
                PENDING_EMERGENCIES.append((spawn_time, node))
        
        print(f"SUCCESS: Loaded {len(PENDING_EMERGENCIES)} emergencies from {CSV_FILENAME}.")
        return True
        
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return False

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_dist(node1, node2):
    """Calculate Euclidean distance between two nodes."""
    if node1 == node2:
        return 0.0
    
    key = (min(node1, node2), max(node1, node2))
    if key in DIST_CACHE:
        return DIST_CACHE[key]
    
    n1, n2 = ALL_NODES[node1], ALL_NODES[node2]
    dist = math.sqrt((n1[1]-n2[1])**2 + (n1[2]-n2[2])**2)
    DIST_CACHE[key] = dist
    return dist

def can_respond_to(responder_id, emergency_type):
    """Check if a responder can handle a specific emergency type."""
    station_id = RESPONDER_TO_STATION[responder_id]
    station_type = STATIONS[station_id]['type']
    capabilities = STATION_TYPES[station_type]
    return emergency_type in capabilities

def spawn_emergencies_until(target_time):
    """Spawns all emergencies up to target_time."""
    global PENDING_EMERGENCIES
    spawned_any = False
    
    while PENDING_EMERGENCIES and PENDING_EMERGENCIES[0][0] <= target_time:
        spawn_time, new_node = PENDING_EMERGENCIES.pop(0)
        nid = new_node[0]
        ALL_NODES[nid] = new_node
        UNVISITED_NODE_IDS.add(nid)
        spawned_any = True
    
    return spawned_any

# ==========================================
# THE AGENT (RHC PRIORITY LOGIC)
# ==========================================

def select_moves(current_time):
    """
    Assigns the highest-scoring unvisited node to each available responder.
    Only considers responders that are currently idle (not in transit).
    """
    moves = {}
    available_nodes = UNVISITED_NODE_IDS.copy()
    
    # Get idle responders (not currently traveling)
    idle_responders = [r for r in range(NUM_RESPONDERS) if r not in RESPONDER_ROUTES]
    
    # Prioritize those at their home station
    idle_responders.sort(
        key=lambda r: RESPONDER_LOCATIONS[r] == RESPONDER_TO_STATION[r], 
        reverse=True
    )

    for r in idle_responders:
        current_loc = RESPONDER_LOCATIONS[r]
        home_station = RESPONDER_TO_STATION[r]
        best_node = -1
        best_score = -1
        
        for node_id in available_nodes:
            node_data = ALL_NODES[node_id]
            points = node_data[3]
            severity = node_data[4]
            emergency_type = node_data[5]

            if not can_respond_to(r, emergency_type):
                continue

            # if severity <= LOWEST_PRIORITY_TO_IGNORE:
            #     continue

            dist = get_dist(current_loc, node_id)
            return_cost = get_dist(node_id, home_station) if RETURN_TO_BASE else 0
            
            if RESPONDER_COSTS[r] + dist + return_cost > MAX_ROUTE_COST:
                continue

            priority_multiplier = SEVERITY_WEIGHTS.get(severity, 1.0)
            score = (points * priority_multiplier) / (dist if dist > 0 else 0.1)

            if score > best_score:
                best_score = score
                best_node = node_id
        
        if best_node != -1:
            moves[r] = best_node
            available_nodes.remove(best_node)
            
            # Calculate arrival time and set route
            dist = get_dist(current_loc, best_node)
            arrival_time = current_time + dist
            RESPONDER_ROUTES[r] = (best_node, arrival_time)
        elif current_loc != home_station:
            # Return home if not already there
            moves[r] = home_station
            dist = get_dist(current_loc, home_station)
            arrival_time = current_time + dist
            RESPONDER_ROUTES[r] = (home_station, arrival_time)
    
    return moves

# ==========================================
# MAIN LOOP - EVENT-DRIVEN
# ==========================================

def run():
    global TOTAL_EMERGENCIES_HANDLED
    random.seed(42)
    
    print("--- STARTING MULTI-STATION EMERGENCY RESPONSE SIMULATION ---")
    print("\nSTATION SETUP:")
    for sid, station in STATIONS.items():
        capabilities = ', '.join(STATION_TYPES[station['type']])
        print(f"  Station {sid} ({station['type'].upper()}) at ({station['x']}, {station['y']}) - Handles: {capabilities}")
    print("")
    
    if not load_csv_data():
        return

    current_time = 0.0
    spawn_emergencies_until(current_time)
    select_moves(current_time)

    # Event-driven simulation: jump to next significant time
    while PENDING_EMERGENCIES or RESPONDER_ROUTES or UNVISITED_NODE_IDS:
        # Determine next event time
        next_times = []
        
        # Next emergency spawn
        if PENDING_EMERGENCIES:
            next_times.append(PENDING_EMERGENCIES[0][0])
        
        # Next responder arrival
        if RESPONDER_ROUTES:
            next_times.append(min(arrival for _, arrival in RESPONDER_ROUTES.values()))
        
        if not next_times:
            break
        
        current_time = min(next_times)
        
        # Process all responder arrivals at this time
        arrived_responders = [r for r, (dest, arr_time) in RESPONDER_ROUTES.items() 
                             if arr_time <= current_time]
        
        for r in arrived_responders:
            dest, _ = RESPONDER_ROUTES[r]
            home_station = RESPONDER_TO_STATION[r]
            
            # Update location and cost
            dist = get_dist(RESPONDER_LOCATIONS[r], dest)
            RESPONDER_COSTS[r] += dist
            RESPONDER_LOCATIONS[r] = dest
            
            # Handle emergency completion
            if dest != home_station and dest in ALL_NODES:
                node_data = ALL_NODES[dest]
                pts = node_data[3]
                RESPONDER_POINTS[r] += pts
                TOTAL_EMERGENCIES_HANDLED += 1
                
                if dest in UNVISITED_NODE_IDS:
                    UNVISITED_NODE_IDS.remove(dest)
            
            # Remove from active routes
            del RESPONDER_ROUTES[r]
        
        # Spawn new emergencies
        spawn_emergencies_until(current_time)
        
        # Replan for idle responders
        if arrived_responders or UNVISITED_NODE_IDS:
            select_moves(current_time)
        
        # Progress indicator
        if int(current_time) % 10000 == 0 and current_time > 0:
            print(f"Progress: t={current_time:.0f}s ({current_time/3600:.1f}h), "
                  f"Handled: {TOTAL_EMERGENCIES_HANDLED}, Pending: {len(UNVISITED_NODE_IDS)}")

    # Final Report
    total_points = sum(RESPONDER_POINTS.values())
    total_cost = sum(RESPONDER_COSTS.values())
    
    print("\n====================================")
    print("      FINAL REPORT")
    print("====================================")
    print(f"Total Emergencies Handled: {TOTAL_EMERGENCIES_HANDLED}")
    print(f"Total Points:  {total_points}")
    print(f"Total Cost:    {total_cost:.2f}")
    print(f"Net Score:     {total_points - total_cost:.2f}")
    print(f"Final Time: {current_time:.1f} seconds ({current_time/3600:.2f} hours)")
    print("\nPer-Responder Breakdown:")
    for r in range(NUM_RESPONDERS):
        station_id = RESPONDER_TO_STATION[r]
        station_type = STATIONS[station_id]['type']
        print(f"  Responder {r} ({station_type.upper()}, Station {station_id}): "
              f"{RESPONDER_POINTS[r]} pts, {RESPONDER_COSTS[r]:.2f} dist")
    print("====================================")

if __name__ == "__main__":
    run()