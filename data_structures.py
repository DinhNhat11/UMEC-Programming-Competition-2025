from collections import namedtuple
from dataclasses import dataclass
from typing import Optional, Tuple

# Emergency request data structure
Emergency = namedtuple('Emergency', [
    'id', 'timestamp', 'x', 'y', 'etype', 'priority_s', 'deadline'
])

# Unit state tracking
@dataclass
class UnitState:
    unit_id: int
    station_id: str
    unit_type: str  # 'fire', 'police', 'medical'
    home_x: float
    home_y: float
    speed: float
    current_x: float
    current_y: float
    available_at: float  # timestamp when unit becomes available
    assigned_to: Optional[int] = None  # emergency id if assigned
    
    def is_available(self, current_time: float) -> bool:
        """Check if unit is available at given time"""
        return current_time >= self.available_at and self.assigned_to is None
    
    def can_respond_to(self, emergency_type: str) -> bool:
        """Check if unit can respond to emergency type"""
        if emergency_type == 'fire':
            return self.unit_type == 'fire'
        elif emergency_type == 'medical':
            return self.unit_type in ['fire', 'medical']
        elif emergency_type == 'police':
            return self.unit_type in ['police', 'medical']
        return False
    
    def distance_to(self, x: float, y: float) -> float:
        """Calculate Euclidean distance to a point"""
        return ((self.current_x - x) ** 2 + (self.current_y - y) ** 2) ** 0.5
    
    def travel_time_to(self, x: float, y: float) -> float:
        """Calculate travel time to a point from current position"""
        return self.distance_to(x, y) / self.speed if self.speed > 0 else float('inf')

# Station data structure
@dataclass
class Station:
    station_id: str
    station_type: str  # 'fire', 'police', 'medical'
    x: float
    y: float
    num_units: int
    
    def create_units(self, start_id: int, speed: float = 1.0) -> list:
        """Create units for this station"""
        units = []
        for i in range(self.num_units):
            unit = UnitState(
                unit_id=start_id + i,
                station_id=self.station_id,
                unit_type=self.station_type,
                home_x=self.x,
                home_y=self.y,
                speed=speed,
                current_x=self.x,
                current_y=self.y,
                available_at=0.0
            )
            units.append(unit)
        return units

# Response result
@dataclass
class ResponseResult:
    emergency_id: int
    responded: bool
    response_time: float  # time when unit arrived
    travel_time: float
    time_remaining: float  # seconds remaining before deadline
    unit_id: Optional[int] = None
    score: float = 0.0  # points for this response

