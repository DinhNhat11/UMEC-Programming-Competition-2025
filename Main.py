import math
import random
import csv
import os

# ==========================================
# CONFIGURATION
# ==========================================
# File path for the emergency data
CSV_FILENAME = "emergency_events.csv" 
# Number of agents/vehicles available
NUM_RESPONDERS = 2
# Determines if the cost of returning to base (Node 0) must be included in the route calculation
RETURN_TO_BASE = True
# Maximum distance (cost) a responder can travel for a single assignment (including return trip)
MAX_ROUTE_COST = 2000.0 
# Severity Level 1 and below will be ignored by the selection logic
LOWEST_PRIORITY_TO_IGNORE = 1 
# The number of time steps the simulation will run for
SIMULATION_STEPS = 50 

# Severity Mapping: Lower seconds = Higher Severity
# This maps the time-based priority (from CSV) to a Severity score (1-10)
# 30s -> Sev 10 (Disaster), 600s -> Sev 1 (Ignore)
PRIORITY_MAP = {
    30: 10,
    60: 8,
    120: 5,
    300: 3,
    600: 1 
}

# Weights used in the scoring heuristic. Higher weight means higher priority for dispatch.
# Severity 10 is 50x more important than Severity 1.
SEVERITY_WEIGHTS = {
    1: 1.0, 2: 1.2, 3: 1.5, 4: 2.0, 5: 3.0,
    6: 5.0, 7: 8.0, 8: 15.0, 9: 30.0, 10: 50.0 
}

# ==========================================
# GLOBAL STATE
# ==========================================
# Dictionary storing all locations: {ID: [ID, X, Y, Points, Severity]}
# Initialize with just the Home Base (Node ID 0) at (100, 100)
ALL_NODES = {0: [0, 100, 100, 0, 0]} 
# Set of Node IDs that have spawned but not yet been visited/cleared
UNVISITED_NODE_IDS = set()
# List of events loaded from the CSV, waiting to be spawned into the simulation
PENDING_EMERGENCIES = []

# Tracks the current location (Node ID) of each responder
RESPONDER_LOCATIONS = {r: 0 for r in range(NUM_RESPONDERS)}
# Tracks the total distance traveled by each responder
RESPONDER_COSTS = {r: 0.0 for r in range(NUM_RESPONDERS)}
# Tracks the total points earned by each responder
RESPONDER_POINTS = {r: 0 for r in range(NUM_RESPONDERS)}

# Global counter for reporting
TOTAL_EMERGENCIES_HANDLED = 0
# Pre-calculated distance matrix: {(Node A, Node B): distance}
DIST_MATRIX = {} 
# Stores all simulation print output
SIMULATION_LOG = "" 

# ==========================================
# DATA LOADING
# ==========================================

def load_csv_data():
    """Reads the external CSV file and parses it into memory."""
    global PENDING_EMERGENCIES
    
    # Check if the input file exists
    if not os.path.exists(CSV_FILENAME):
        print(f"ERROR: Could not find '{CSV_FILENAME}' in this folder.")
        return False

    try:
        with open(CSV_FILENAME, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse priority_s to an integer time value
                try:
                    p_seconds = int(float(row['priority_s']))
                except ValueError:
                    p_seconds = 600 # Default to low priority if parsing fails
                
                # Look up the Severity based on the time in seconds
                severity = PRIORITY_MAP.get(p_seconds, 3) # Default to Sev 3 if unknown time
                
                # Calculate Base Points (Urgent events get more points)
                # Formula ensures lower time (p_seconds) results in higher points
                base_points = 100 - (p_seconds // 10)
                if base_points < 10: base_points = 10

                # Create the node data structure [ID, X, Y, Points, Severity]
                node = [
                    int(row['id']),
                    float(row['x']),
                    float(row['y']),
                    base_points,
                    severity
                ]
                # Add to the queue of events waiting to be spawned
                PENDING_EMERGENCIES.append(node)
        
        log(f"SUCCESS: Loaded {len(PENDING_EMERGENCIES)} emergencies from {CSV_FILENAME}.")
        return True
        
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return False

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def log(message):
    global SIMULATION_LOG
    SIMULATION_LOG += message + "\n"
    # Print to console immediately
    print(message, flush=True)

def update_distance_matrix():
    """Calculates Euclidean distance between all active nodes and stores them."""
    global DIST_MATRIX
    DIST_MATRIX = {}
    ids = list(ALL_NODES.keys())
    for i in ids:
        for j in ids:
            n1, n2 = ALL_NODES[i], ALL_NODES[j]
            # Euclidean distance calculation: sqrt((x2-x1)^2 + (y2-y1)^2)
            dist = math.sqrt((n1[1]-n2[1])**2 + (n1[2]-n2[2])**2)
            DIST_MATRIX[(i,j)] = dist
            DIST_MATRIX[(j,i)] = dist # Matrix is symmetric
# Initial call to calculate distance from Base to itself
update_distance_matrix()

def get_dist(i, j):
    """Safely retrieves distance, returning infinity if not found."""
    return DIST_MATRIX.get((i, j), float('inf'))

def spawn_next_emergencies(count=1):
    """Pulls the next N emergencies from the loaded CSV list into the simulation."""
    spawned = False
    for _ in range(count):
        if not PENDING_EMERGENCIES:
            break
        
        new_node = PENDING_EMERGENCIES.pop(0) # Get the next event from the queue
        nid = new_node[0]
        
        ALL_NODES[nid] = new_node        # Add to the dictionary of active nodes
        UNVISITED_NODE_IDS.add(nid)      # Mark as an unvisited target
        log(f"  -> NEW ALERT: Node {nid} (Sev: {new_node[4]})")
        spawned = True
    
    if spawned:
        # Re-calculate distances to include the newly spawned nodes
        update_distance_matrix()
    return spawned

# ==========================================
# THE AGENT (RHC PRIORITY LOGIC)
# ==========================================

def select_moves(locations, unvisited):
    """
    Implements the Reactive Heuristic Control (RHC) logic.
    Assigns the highest-scoring unvisited node to each available responder.
    """
    moves = {}
    available_nodes = unvisited.copy()
    
    # Sort responders: Prioritize those at Base (0) for immediate dispatch
    # key=lambda r: locations[r] == 0 ensures responders at 0 are placed first
    sorted_responders = sorted(locations.keys(), key=lambda r: locations[r] == 0, reverse=True)

    for r in sorted_responders:
        current_loc = locations[r]
        best_node = -1
        best_score = -1
        
        for node_id in list(available_nodes):
            node_data = ALL_NODES[node_id]
            points = node_data[3]
            severity = node_data[4]

            # RULE: IGNORE SEVERITY BELOW OR EQUAL TO THE THRESHOLD
            if severity <= LOWEST_PRIORITY_TO_IGNORE:
                continue

            dist = get_dist(current_loc, node_id)
            # Calculate cost to return to base, if required by configuration
            return_cost = get_dist(node_id, 0) if RETURN_TO_BASE else 0
            
            # RULE: CHECK MAX ROUTE COST
            # If current total cost plus this trip exceeds the limit, skip this node
            if RESPONDER_COSTS[r] + dist + return_cost > MAX_ROUTE_COST:
                continue

            # Heuristic Score: (Points * PriorityMultiplier) / Distance
            # This is a Benefit-Per-Cost ratio (maximize reward, minimize cost/distance)
            priority_multiplier = SEVERITY_WEIGHTS.get(severity, 1.0)
            score = (points * priority_multiplier) / (dist if dist > 0 else 0.1) # Avoid division by zero

            if score > best_score:
                best_score = score
                best_node = node_id
        
        if best_node != -1:
            moves[r] = best_node
            # Critical: Remove the assigned node so no other responder takes it
            available_nodes.remove(best_node)
        else:
            # If no good node is found, assign the responder to return to Base (0)
            moves[r] = 0 
    
    return moves

# ==========================================
# MAIN LOOP
# ==========================================

def run():
    global TOTAL_EMERGENCIES_HANDLED
    random.seed(42) # Set seed for reproducibility
    
    log("--- STARTING SIMULATION ---")
    
    # 1. Load Data
    if not load_csv_data():
        return # Stop if CSV fails

    # 2. Initial Spawn (Get first 5 events from CSV to start the map)
    spawn_next_emergencies(5)
    
    # Get the initial plan
    moves = select_moves(RESPONDER_LOCATIONS, UNVISITED_NODE_IDS)
    log(f"Initial Plan: {moves}\n")

    for t in range(1, SIMULATION_STEPS + 1):
        log(f"--- TIME STEP {t} ---")
        replan = False # Flag to decide if a new plan is needed
        
        # Move Phase
        for r in range(NUM_RESPONDERS):
            cur = RESPONDER_LOCATIONS[r]
            tgt = moves.get(r, 0)
            
            if cur != tgt:
                dist = get_dist(cur, tgt)
                RESPONDER_COSTS[r] += dist         # Accumulate cost
                RESPONDER_LOCATIONS[r] = tgt       # Update location
                
                if tgt != 0:
                    # Responder arrived at and CLEARED an emergency node
                    pts = ALL_NODES[tgt][3]
                    sev = ALL_NODES[tgt][4]
                    RESPONDER_POINTS[r] += pts
                    TOTAL_EMERGENCIES_HANDLED += 1
                    
                    if tgt in UNVISITED_NODE_IDS:
                        UNVISITED_NODE_IDS.remove(tgt) # Remove from targets list
                        replan = True # A node was cleared, need to re-plan
                    log(f"Responder {r} CLEARED Node {tgt} (Sev {sev}).")
                else:
                    # Responder arrived back at the Base
                    log(f"Responder {r} returned to Base.")
            else:
                 # Responder is idle, waiting at current location. If at base (0), re-plan to find a new task.
                 if cur == 0: replan = True

        # New Events Phase (Pull 1 new event from CSV per step)
        if spawn_next_emergencies(1):
            replan = True # A new event occurred, need to re-plan
            
        # Re-Plan Phase
        if replan:
            # Recalculate the optimal moves based on the updated state
            moves = select_moves(RESPONDER_LOCATIONS, UNVISITED_NODE_IDS)
            log(f"New Plan: {moves}")

    # Final Report
    total_points = sum(RESPONDER_POINTS.values())
    total_cost = sum(RESPONDER_COSTS.values())
    
    log("\n====================================")
    log("      FINAL REPORT")
    log("====================================")
    log(f"Total Points:  {total_points}")
    log(f"Total Cost:    {total_cost:.2f}")
    # Net Score = Points - Cost (Standard metric for optimizing routing)
    log(f"Net Score:     {total_points - total_cost:.2f}")
    log("====================================")

if __name__ == "__main__":
    run() # Start the simulation when the script is executed