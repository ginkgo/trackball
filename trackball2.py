from build123d import *
from enum import Enum
import sys
import math

# All measurements in millimeters

# Ball diameter (pick one)
ball = 57.2    # pool billiards ball
#ball = 52.4   # snooker ball
#ball = 55     # Kensington ball

# Thickness of walls
wall = 2

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

print_resolution = 0.1

def align(xyz):
    d = {'c': Align.CENTER,
         '-': Align.MIN,
         '+': Align.MAX}
    return [d[c] for c in xyz]

def prusa_trick_borehole(radius, depth, counter_bore_radius, counter_bore_depth):
    loc = Pos(0,0,1)

    part = Cylinder(radius, counter_bore_depth + depth, align=align('cc+'))
    part += Cylinder(counter_bore_radius, counter_bore_depth + 1, align=align('cc+'))
    part += (Box(2*radius, 2*counter_bore_radius, counter_bore_depth + 1 + print_resolution, align=align('cc+')) &
             Cylinder(counter_bore_radius, counter_bore_depth + 1 + print_resolution, align=align('cc+')))
    part += Box(2*radius, 2*radius, counter_bore_depth + 1 + 2*print_resolution, align=align('cc+'))

    return loc * part

# Bore holes for screws
M3x4 = prusa_trick_borehole(radius=1.45, depth=5, counter_bore_radius=3.1, counter_bore_depth=1.2)
M2x3 = CounterBoreHole(radius=0.95, depth=4, counter_bore_radius=2.1, counter_bore_depth=0.7)
M2x4 = CounterBoreHole(radius=0.95, depth=5, counter_bore_radius=2.1, counter_bore_depth=0.7)
M2x6 = CounterBoreHole(radius=0.95, depth=7, counter_bore_radius=2.1, counter_bore_depth=0.7)

eta = 0.1 # General tolerance

trackball = Sphere(radius=ball/2)

bottom_hole_radius = 8

if suspension_type == SuspensionType.BEARING_BALL:
    bowl_radius = (ball+bearing)/2
elif suspension_type == SuspensionType.BALL_TRANSFER_UNIT:
    bowl_radius = ((ball/2 + btu_L1)**2 + (btu_D/2)**2)**0.5
else:
    assert(False)


angle = 18
profile1 = Rotation(-angle, 0,0) * Pos(0,0,0) * Rectangle(90, 100)
profile2 = Pos(0,0,-ball/2) * Pos(0,-5,0) * Rectangle(90,110)

top = loft([profile1, profile2])
top -= Rotation(0,0,math.pi) * Sphere(radius=bowl_radius)
top -= Cylinder(radius=15,height=100)

base_plate = top.faces().sort_by(Axis.Z)[0]
top = offset(top.solids()[0], amount=-wall, openings=base_plate)

if suspension_type == SuspensionType.BALL_TRANSFER_UNIT:
    # Cut holes for BTUs at the end
    for angle in range(0,360+60,120):
        loc = Rotation(-8,0,0) * Rotation(0,0,angle) * Rotation(60,0,0) * Pos(0,0,-(ball/2+btu_L1))

        top += loc * Pos(0,0,-eta/2) * Cylinder(btu_D/2+wall, btu_H+wall, align=align('cc+'))
        top -= loc * Cylinder(btu_D/2 + eta, 2* (btu_H + eta), align=align('ccc'))
        top -= loc * Cylinder(btu_D1/2 + eta, 2* (btu_H + btu_L), align=align('ccc'))

        # pull-out slots
        pullout_size = 2
        pullout_depth = 1
        top -= loc * Box(btu_D + pullout_size, pullout_size, 2* (btu_H + pullout_depth), align=align('ccc'))

bottom = extrude(base_plate,amount=wall)

def mk_sensor_pcb(loc):
    global bottom, top
    board = Pos(2.91,0,0) * Box(34,22,1.5, align=align('cc-')) - Box(18,9,5, align=align('cc-'))

    hole_locations = [Pos(x,y) for x in (-11.09, +13.41) for y in (-8, +8)]
    board -= [l * Cylinder(.8, 10) for l in hole_locations]

    strut=4
    sketch = Polyline([(-2,0,strut-4),
                       (+2,0,strut-4),
                       (+2,0,-4),
                       (-2,0,-4),
                       (-2,0,strut-4)])
    bottom += [extrude(loc * l * make_face(sketch), target=bottom, until=Until.NEXT, dir=(0,0,-1)) for l in hole_locations]

    sketch = Pos(0,0,-4) * Circle(radius=2)
    bottom += [extrude(loc * l * make_face(sketch), target=bottom, until=Until.NEXT, dir=(0,0,-1)) for l in hole_locations]

    bottom += [loc * l * Cylinder(2.1,4, align=align('cc+')) for l in hole_locations]
    bottom -= [loc * l * Cylinder(0.9,2, align=align('cc+')) for l in hole_locations]

    top -= (loc * Box(17,15,5, align=align('cc-')))
    top += (loc * Pos(0,0,5) * Box(17,15,10, align=align('cc-'))) - Sphere(bowl_radius)

    #opening
    face = Plane.XY * make_face([ThreePointArc([(0,2), (-2,0), (0,-2)]),
                                 Polyline([(0,-2), (4,-2), (4,2), (0,2)])])

    top -= loc * Pos(0,0,7.41) * extrude(face, amount=10, dir=(0,0,-1), taper=68.5-90)

    return loc * board

sensor_pcb1 = mk_sensor_pcb(Rotation(0, 60,-90) * Pos(0,0,-ball/2 - 7.41))
sensor_pcb2 = mk_sensor_pcb(Rotation(0,-60,-90) * Pos(0,0,-ball/2 - 7.41))

result = {
    'ball': trackball,
    'sensor_pcb1': sensor_pcb1,
    'sensor_pcb2': sensor_pcb2,
    'top': top,
    'bottom': bottom,
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
