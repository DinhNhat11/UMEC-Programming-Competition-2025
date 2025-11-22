"""CSV parser for emergency events"""

import csv
from typing import List
from data_structures import Emergency

def load_emergencies(csv_path: str) -> List[Emergency]:
    """
    Load emergency events from CSV file.
    
    CSV format: t,x,y,etype,priority_s,id
    - t: timestamp in seconds
    - x, y: coordinates (0-200)
    - etype: emergency type (fire, medical, police)
    - priority_s: deadline in seconds
    - id: unique identifier
    
    Returns:
        List of Emergency objects sorted by timestamp
    """
    emergencies = []
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamp = float(row['t'])
            x = float(row['x'])
            y = float(row['y'])
            etype = row['etype']
            priority_s = float(row['priority_s'])
            emergency_id = int(row['id'])
            
            # Calculate deadline
            deadline = timestamp + priority_s
            
            emergency = Emergency(
                id=emergency_id,
                timestamp=timestamp,
                x=x,
                y=y,
                etype=etype,
                priority_s=priority_s,
                deadline=deadline
            )
            emergencies.append(emergency)
    
    # Sort by timestamp
    emergencies.sort(key=lambda e: e.timestamp)
    
    return emergencies

