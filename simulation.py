"""Simulation engine for emergency dispatch"""

from typing import List, Dict
from data_structures import Emergency, UnitState, ResponseResult, Station
from dispatcher import priority_aware_dispatch
from utils import calculate_score

class Simulation:
    """Event-driven simulation engine"""
    
    def __init__(self, stations: List[Station], units: List[UnitState]):
        self.stations = stations
        self.units = units
        self.current_time = 0.0
        self.results: List[ResponseResult] = []
        
    def get_available_units(self, current_time: float) -> List[UnitState]:
        """Get all units available at the given time"""
        available = []
        for unit in self.units:
            # Update unit position if it has returned to home
            if unit.available_at <= current_time and unit.assigned_to is not None:
                # Unit has finished and returned
                unit.current_x = unit.home_x
                unit.current_y = unit.home_y
                unit.assigned_to = None
            
            if unit.is_available(current_time):
                available.append(unit)
        
        return available
    
    def process_emergency(self, emergency: Emergency) -> ResponseResult:
        """
        Process a single emergency.
        
        Returns:
            ResponseResult with outcome
        """
        # Update current time to emergency timestamp
        self.current_time = emergency.timestamp
        
        # Get available units
        available_units = self.get_available_units(self.current_time)
        
        # Try to dispatch
        dispatch_result = priority_aware_dispatch(emergency, available_units, self.current_time)
        
        if dispatch_result is None:
            # No unit available - emergency fails
            return ResponseResult(
                emergency_id=emergency.id,
                responded=False,
                response_time=emergency.deadline,  # Failed at deadline
                travel_time=0.0,
                time_remaining=0.0,
                score=-2.0
            )
        
        unit, travel_time = dispatch_result
        arrival_time = self.current_time + travel_time
        
        # Check if we made it in time
        if arrival_time > emergency.deadline:
            # Too late - emergency fails
            unit.assigned_to = None  # Don't assign if we can't make it
            return ResponseResult(
                emergency_id=emergency.id,
                responded=False,
                response_time=arrival_time,
                travel_time=travel_time,
                time_remaining=0.0,
                unit_id=unit.unit_id,
                score=-2.0
            )
        
        # Successfully responded
        # Assign unit and update its state
        unit.assigned_to = emergency.id
        
        # Unit travels to emergency location
        unit.current_x = emergency.x
        unit.current_y = emergency.y
        
        # Assume unit is busy for some time handling the emergency
        # Handling time depends on emergency type and priority
        # Shorter handling time for urgent emergencies
        base_handling_time = 30.0  # Base 30 seconds
        if emergency.priority_s <= 30:
            handling_time = base_handling_time  # Urgent: 30 seconds
        elif emergency.priority_s <= 60:
            handling_time = base_handling_time * 1.5  # 45 seconds
        else:
            handling_time = base_handling_time * 2.0  # 60 seconds
        
        # Unit returns to home station after handling
        return_travel_time = unit.travel_time_to(unit.home_x, unit.home_y)
        unit.available_at = arrival_time + handling_time + return_travel_time
        
        # Note: Unit position stays at emergency location until it returns
        # This allows tracking, but we'll update it when unit becomes available
        
        # Calculate score
        time_remaining = emergency.deadline - arrival_time
        score = calculate_score(arrival_time, emergency.deadline, emergency.timestamp)
        
        return ResponseResult(
            emergency_id=emergency.id,
            responded=True,
            response_time=arrival_time,
            travel_time=travel_time,
            time_remaining=time_remaining,
            unit_id=unit.unit_id,
            score=score
        )
    
    def run(self, emergencies: List[Emergency]) -> List[ResponseResult]:
        """
        Run simulation for all emergencies.
        
        Args:
            emergencies: List of emergencies sorted by timestamp
        
        Returns:
            List of response results
        """
        self.results = []
        
        for emergency in emergencies:
            result = self.process_emergency(emergency)
            self.results.append(result)
        
        return self.results
    
    def get_total_score(self) -> float:
        """Calculate total score from all responses"""
        return sum(result.score for result in self.results)
    
    def get_statistics(self) -> Dict:
        """Get simulation statistics"""
        total = len(self.results)
        responded = sum(1 for r in self.results if r.responded)
        failed = total - responded
        
        avg_response_time = sum(r.travel_time for r in self.results if r.responded) / responded if responded > 0 else 0
        avg_time_remaining = sum(r.time_remaining for r in self.results if r.responded) / responded if responded > 0 else 0
        
        return {
            'total_emergencies': total,
            'responded': responded,
            'failed': failed,
            'success_rate': responded / total if total > 0 else 0,
            'total_score': self.get_total_score(),
            'avg_response_time': avg_response_time,
            'avg_time_remaining': avg_time_remaining
        }

