from build123d import *
from enum import Enum
import sys

# All measurements in millimeters

# Ball diameter (pick one)
ball = 57.2    # pool billiards ball
#ball = 52.4   # snooker ball
#ball = 55     # Kensington ball

# Type of ball suspension used
class SuspensionType(Enum):
    BEARING_BALL = 1
    BALL_TRANSFER_UNIT = 2

suspension_type = SuspensionType.BALL_TRANSFER_UNIT

# Bearing diameter
bearing = 2.5

# Measurements for 7.5mm YK310 ball transfer unit (from datasheet)
btu_D  = 9
btu_D1 = 7.5
btu_L  = 4
btu_L1 = 1.1
btu_H  = 1

# Thickness of walls
wall = 2

base_width=110
base_height=(ball+10)/2

# Parameters of trackball case arc
arc_radius=300/2
arc_location=(0,-20,-arc_radius)

# Bore holes for screws
M3x4 = CounterBoreHole(radius=1.45, depth=5, counter_bore_radius=3.1, counter_bore_depth=1.2)
M2x3 = CounterBoreHole(radius=0.95, depth=4, counter_bore_radius=2.1, counter_bore_depth=0.7)


def align(xyz):
    d = {'c': Align.CENTER,
         '-': Align.MIN,
         '+': Align.MAX}
    return [d[c] for c in xyz]

part = Box(30,10,wall, align=align('cc-'))

usbc_width=8.34
usbc_height=2.56

usbc_sketch = fillet(Rectangle(8.34,2.56).vertices(), radius=1.25)
part -= extrude(usbc_sketch, wall, dir=(0,0,1), taper=-45)

hole_dist = 16.15
part -= Pos( hole_dist/2,0,0) * Cylinder(radius=0.95, height=1.5, align=align('cc-'))
part -= Pos(-hole_dist/2,0,0) * Cylinder(radius=0.95, height=1.5, align=align('cc-'))

result = {
    'part': part,
}

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} STL|STEP')
        exit(0)

    if sys.argv[1] == 'STL':
        for k,v in result.items():
            print(k)
            exporter = Mesher()
            exporter.add_shape(v)
            exporter.write(f'stl/{k}.stl')
    elif sys.argv[1] == 'STEP':

        for k,v in result.items():
            print(k)
            export_step(v, f'step/{k}.step')
    else:
        print(f'Usage: {sys.argv[0]} STL|STEP')
        exit(0)
