"""Utility functions for distance calculations and conversions"""

import math

def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def minutes_to_seconds(minutes: float) -> float:
    """Convert minutes to seconds"""
    return minutes * 60.0

def seconds_to_minutes(seconds: float) -> float:
    """Convert seconds to minutes"""
    return seconds / 60.0

def calculate_score(response_time: float, deadline: float, timestamp: float) -> float:
    """
    Calculate score for a response.
    - Failed request (response_time > deadline): -2 points
    - Each extra minute (60 seconds) when response arrives: +1 point
    
    Args:
        response_time: Time when unit arrived at emergency
        deadline: Deadline for the emergency (timestamp + priority_s)
        timestamp: When emergency occurred
    
    Returns:
        Score for this response
    """
    if response_time > deadline:
        # Failed request
        return -2.0
    
    # Calculate how early the response arrived
    time_remaining = deadline - response_time
    
    # Each extra minute (60 seconds) = +1 point
    extra_minutes = time_remaining / 60.0
    
    return extra_minutes

