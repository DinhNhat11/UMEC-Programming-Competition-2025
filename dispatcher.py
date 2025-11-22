"""Priority-aware dispatcher for emergency responses"""

from typing import List, Optional, Tuple
from data_structures import Emergency, UnitState

def priority_aware_dispatch(
    emergency: Emergency,
    available_units: List[UnitState],
    current_time: float
) -> Optional[Tuple[UnitState, float]]:
    """
    Priority-aware greedy dispatcher.
    
    Considers:
    1. Unit type compatibility
    2. Urgency (time remaining before deadline)
    3. Distance to emergency
    
    Args:
        emergency: The emergency to respond to
        available_units: List of available units
        current_time: Current simulation time
    
    Returns:
        Tuple of (best_unit, travel_time) or None if no unit available
    """
    if not available_units:
        return None
    
    # Filter units that can respond to this emergency type
    compatible_units = [
        unit for unit in available_units
        if unit.can_respond_to(emergency.etype)
    ]
    
    if not compatible_units:
        return None
    
    # Calculate urgency (how close to deadline)
    time_until_deadline = emergency.deadline - current_time
    urgency = time_until_deadline / emergency.priority_s if emergency.priority_s > 0 else 0
    
    # Score each compatible unit
    best_unit = None
    best_score = float('-inf')
    
    for unit in compatible_units:
        # Calculate travel time
        travel_time = unit.travel_time_to(emergency.x, emergency.y)
        arrival_time = current_time + travel_time
        
        # Check if we can make it in time
        if arrival_time > emergency.deadline:
            # Can't make deadline - skip this unit
            continue
        
        # Calculate time remaining after arrival
        time_remaining = emergency.deadline - arrival_time
        
        # Scoring function:
        # - Higher urgency = higher priority
        # - Shorter distance = better
        # - More time remaining = better (for bonus points)
        distance = unit.distance_to(emergency.x, emergency.y)
        
        # Weighted score
        urgency_weight = 100.0
        distance_weight = 2.0
        time_remaining_weight = 0.5
        
        score = (
            urgency_weight * urgency +
            time_remaining_weight * time_remaining -
            distance_weight * distance
        )
        
        if score > best_score:
            best_score = score
            best_unit = unit
    
    if best_unit is None:
        return None
    
    travel_time = best_unit.travel_time_to(emergency.x, emergency.y)
    return (best_unit, travel_time)

def simple_greedy_dispatch(
    emergency: Emergency,
    available_units: List[UnitState],
    current_time: float
) -> Optional[Tuple[UnitState, float]]:
    """
    Simple greedy dispatcher - assigns closest available unit.
    Used as baseline for comparison.
    """
    if not available_units:
        return None
    
    # Filter compatible units
    compatible_units = [
        unit for unit in available_units
        if unit.can_respond_to(emergency.etype)
    ]
    
    if not compatible_units:
        return None
    
    # Find closest unit
    best_unit = min(compatible_units, key=lambda u: u.distance_to(emergency.x, emergency.y))
    travel_time = best_unit.travel_time_to(emergency.x, emergency.y)
    
    return (best_unit, travel_time)

