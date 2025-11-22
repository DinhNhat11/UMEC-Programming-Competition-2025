# UMEC Emergency Dispatch System - Solution Summary

## Overview

This solution implements a **Priority-Aware Dispatcher** combined with **K-Means Station Optimization** to efficiently handle emergency responses over a 3-day simulation period.

## Key Components

### 1. Priority-Aware Dispatcher (`dispatcher.py`)
- **Strategy**: Weighted scoring function considering:
  - **Urgency**: Time remaining before deadline
  - **Distance**: Travel time to emergency
  - **Time Remaining**: Bonus points potential
  
- **Scoring Formula**:
  ```
  score = (urgency_weight × urgency) + (time_remaining_weight × time_remaining) - (distance_weight × distance)
  ```

- **Advantages**:
  - Fast O(n log n) complexity
  - Balances multiple objectives
  - Handles 500+ emergencies efficiently

### 2. K-Means Station Optimizer (`station_optimizer.py`)
- **Method**: Weighted K-Means clustering
- **Weighting**: Emergencies weighted by inverse priority (urgent = higher weight)
- **Process**:
  1. Cluster emergency locations by type
  2. Place stations at weighted centroids
  3. Optimizes for both coverage and urgency

### 3. Simulation Engine (`simulation.py`)
- **Type**: Event-driven simulation
- **Features**:
  - Tracks unit availability and positions
  - Handles concurrent emergencies
  - Calculates travel times dynamically
  - Variable handling times based on emergency priority

## Results

### Initial Station Configuration
- **Success Rate**: 71.8% (359/500 emergencies)
- **Total Score**: 775.70 points
- **Average Response Time**: 45.34 seconds
- **Average Time Remaining**: 176.77 seconds

### Optimized Station Configuration (K-Means)
- **Success Rate**: 78.4% (392/500 emergencies)
- **Total Score**: 840.92 points
- **Average Response Time**: 49.68 seconds
- **Average Time Remaining**: 161.77 seconds

### Improvement
- **Score Improvement**: +65.23 points (+8.4%)
- **Success Rate Improvement**: +6.6%
- **Failed Emergencies Reduced**: 141 → 108 (23% reduction)

## File Structure

```
UMEC-Programming-Competition-2025/
├── UMEC_Programming_Competitor_Demo.py  # Main entry point
├── data_structures.py                   # Core data classes
├── csv_parser.py                        # CSV file parser
├── dispatcher.py                        # Priority-aware dispatcher
├── simulation.py                         # Simulation engine
├── station_optimizer.py                 # K-Means optimizer
├── utils.py                             # Utility functions
└── emergency_events.csv                 # Input data
```

## How to Run

```bash
python UMEC_Programming_Competitor_Demo.py
```

The script will:
1. Load emergencies from `emergency_events.csv`
2. Run simulation with initial station configuration
3. Optimize station locations using K-Means
4. Run simulation with optimized stations
5. Display comparison results

## Key Features

1. **Response Type Compatibility**:
   - Firefighters → fire + medical emergencies
   - Paramedics → medical + police emergencies
   - Police → police emergencies only

2. **Scoring System**:
   - Failed request: **-2 points**
   - Each extra minute (60 seconds): **+1 point**

3. **Dynamic Unit Tracking**:
   - Units dispatched from current location (not just home)
   - Variable handling times based on emergency priority
   - Automatic return to home station after response

## Future Enhancements

1. **Genetic Algorithm**: Further optimize station locations
2. **Hungarian Algorithm**: Optimal batch assignment for concurrent emergencies
3. **Visualization**: Plot city grid, emergencies, and unit paths
4. **Advanced Metrics**: Coverage analysis, response time distributions

## Performance Notes

- **Processing Time**: ~1-2 seconds for full 3-day simulation
- **Scalability**: Handles 500+ emergencies efficiently
- **Optimization Time**: K-Means clustering completes in <1 second

