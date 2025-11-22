"""
UMEC Programming Competition 2025 - Emergency Dispatch System

Main entry point for the emergency dispatch simulation.
Implements priority-aware dispatching and K-means station optimization.
"""

import os
from data_structures import Station
from csv_parser import load_emergencies
from simulation import Simulation
from station_optimizer import optimize_stations

def build_initial_stations():
    """Build initial station configuration"""
    stations = []
    stations.append(Station('F1', 'fire', 20, 20, 2))
    stations.append(Station('F2', 'fire', 180, 20, 2))
    stations.append(Station('P1', 'police', 50, 100, 2))
    stations.append(Station('P2', 'police', 150, 120, 2))
    stations.append(Station('H1', 'medical', 100, 30, 2))
    stations.append(Station('H2', 'medical', 100, 170, 2))
    return stations

def main():
    """Main simulation function"""
    print("=" * 60)
    print("UMEC Emergency Dispatch System")
    print("=" * 60)
    
    # Load emergencies
    csv_path = 'emergency_events.csv'
    if not os.path.exists(csv_path):
        csv_path = os.path.join('UMEC-Programming-Competition-2025', csv_path)
    
    print(f"\nLoading emergencies from {csv_path}...")
    emergencies = load_emergencies(csv_path)
    print(f"Loaded {len(emergencies)} emergencies")
    
    # Option 1: Use initial stations
    print("\n" + "=" * 60)
    print("SIMULATION 1: Initial Station Configuration")
    print("=" * 60)
    initial_stations = build_initial_stations()
    initial_units = []
    unit_id = 0
    for station in initial_stations:
        units = station.create_units(unit_id, speed=1.0)
        initial_units.extend(units)
        unit_id += len(units)
    
    sim1 = Simulation(initial_stations, initial_units)
    results1 = sim1.run(emergencies)
    stats1 = sim1.get_statistics()
    
    print(f"\nResults:")
    print(f"  Total Score: {stats1['total_score']:.2f}")
    print(f"  Responded: {stats1['responded']}/{stats1['total_emergencies']} ({stats1['success_rate']*100:.1f}%)")
    print(f"  Failed: {stats1['failed']}")
    print(f"  Average Response Time: {stats1['avg_response_time']:.2f} seconds")
    print(f"  Average Time Remaining: {stats1['avg_time_remaining']:.2f} seconds")
    
    # Option 2: Optimized stations using K-Means
    print("\n" + "=" * 60)
    print("SIMULATION 2: Optimized Station Configuration (K-Means)")
    print("=" * 60)
    print("Optimizing station locations...")
    
    optimized_stations = optimize_stations(
        emergencies,
        station_types=['fire', 'police', 'medical'],
        num_stations_per_type=[2, 2, 2]
    )
    
    print("\nOptimized Station Locations:")
    for station in optimized_stations:
        print(f"  {station.station_id}: {station.station_type} at ({station.x:.1f}, {station.y:.1f})")
    
    optimized_units = []
    unit_id = 0
    for station in optimized_stations:
        units = station.create_units(unit_id, speed=1.0)
        optimized_units.extend(units)
        unit_id += len(units)
    
    sim2 = Simulation(optimized_stations, optimized_units)
    results2 = sim2.run(emergencies)
    stats2 = sim2.get_statistics()
    
    print(f"\nResults:")
    print(f"  Total Score: {stats2['total_score']:.2f}")
    print(f"  Responded: {stats2['responded']}/{stats2['total_emergencies']} ({stats2['success_rate']*100:.1f}%)")
    print(f"  Failed: {stats2['failed']}")
    print(f"  Average Response Time: {stats2['avg_response_time']:.2f} seconds")
    print(f"  Average Time Remaining: {stats2['avg_time_remaining']:.2f} seconds")
    
    # Comparison
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    score_improvement = stats2['total_score'] - stats1['total_score']
    print(f"Score Improvement: {score_improvement:+.2f} points")
    print(f"Success Rate Improvement: {(stats2['success_rate'] - stats1['success_rate'])*100:+.1f}%")
    
    print("\n" + "=" * 60)
    print("Simulation Complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
