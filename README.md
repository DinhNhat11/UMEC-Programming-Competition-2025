# UMEC Programming Competition 2025
## Emergency Response Optimization System

### Overview
An intelligent emergency dispatch system that optimizes fleet deployment and station placement across a 200×200 pixel city grid. Processes 500+ emergencies over a 3-day simulation using event-driven architecture and priority-based scoring.

### Problem
After a major arson attack overwhelmed Manitoba's emergency services, we were tasked to:
- Efficiently dispatch emergency units to minimize response times
- Optimize station placement across the city
- Handle 500 emergencies over 72 hours with limited resources

### Solution Highlights
- **Event-Driven Simulation**: Jumps between significant events (250× faster than time-step simulation)
- **Priority-Based Dispatch**: Heuristic scoring that prioritizes urgent emergencies (disasters weighted 10× higher)
- **Multi-Capability Stations**: Fire and paramedic stations handle multiple emergency types for better coverage
- **Net Score**: 38,678 points (total points earned - travel distance)

### Key Features
- 6 strategically placed stations (2 fire, 2 police, 2 paramedic)
- Budget-constrained routing (2000-pixel max per responder)
- Real-time capability matching (responders assigned based on emergency type)
- Distance caching for performance optimization

### Technologies
- **Language**: Python 3.12
- **Libraries**: pandas, scikit-learn, matplotlib, NumPy
- **AI Assistance**: Development aided by Gemini and Claude AI

  ### Acknowledgments
This project was developed with assistance from:
- **Claude AI** by Anthropic -
- **Google Gemini** - Problem analysis 

### Team
UMEC Programming Competition 2025 - Team [Your Team Name]

### License
MIT License - Created for educational purposes
