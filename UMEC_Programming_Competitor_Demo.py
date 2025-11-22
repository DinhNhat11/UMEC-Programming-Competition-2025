from collections import defaultdict, namedtuple

Unit  = namedtuple('Unit', ['station_id','stype','unit_id','home_x','home_y','speed'])

def build_initial_stations():
    stations = []
    #(id, type, x, y, num_units)
    stations.append(('F1','fire', 20,20, 2))
    stations.append(('F2','fire',180,20, 2))
    stations.append(('P1','police', 50,100, 2))
    stations.append(('P2','police',150,120, 2))
    stations.append(('H1','medical', 100,30, 2))
    stations.append(('H2','medical', 100,170,2))
    return stations

def create_units_from_stations(stations, default_speed=1.0):
    units = []
    uid = 0
    for sid, stype, sx, sy, num in stations:
        for k in range(num):
            units.append(Unit(sid, stype, uid, sx, sy, default_speed))
            uid += 1
    return units

def main():
    stations = build_initial_stations()
    units = create_units_from_stations(stations, default_speed=1.0)  # 1 unit/sec
