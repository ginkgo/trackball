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

class CableMountType(Enum):
    # Simple hole in the back to lead cable connected to RaspPi Pico to
    HOLE = 1

    # USB-C plug in back
    USBC_PLUG = 2

    # Use a RP2040 Super-Mini board instead of pi pico and place it in back so
    # the USB-C plug can be used directly
    RP2040_SUPERMINI = 3

cable_mount_type = CableMountType.RP2040_SUPERMINI

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
angle_r = angle*math.pi/180
profile = Polyline([(0,-60,-ball/2),
                    (0, 50,-ball/2),
                    (0, 48, math.tan(angle_r) * -48),
                    (0,-48, math.tan(angle_r) *  48),
                    (0,-60,-ball/2+10),
                    (0,-60,-ball/2),
                    ])

top = extrude(make_face(profile), amount=95/2, dir=(1,0,0), both=True)
top -= Rotation(0,0,math.pi) * Sphere(radius=bowl_radius)
top -= Cylinder(radius=15,height=100)

chamfer_edges = [
    top.edges().sort_by(Axis.Z)[-1],
    top.edges().sort_by(Axis.X)[-4:].sort_by(Axis.Z)[-1],
    top.edges().sort_by(Axis.X)[-4:].sort_by(Axis.Y)[-1],
    top.edges().sort_by(Axis.X)[-4:].sort_by(Axis.Y)[0],
    top.edges().sort_by(Axis.X)[-4:].sort_by(Axis.Y)[1],
    top.edges().sort_by(Axis.X)[:3].sort_by(Axis.Z)[-1],
    top.edges().sort_by(Axis.X)[:3].sort_by(Axis.Y)[-1],
    top.edges().sort_by(Axis.X)[:5].sort_by(Axis.Y)[0],
    top.edges().sort_by(Axis.X)[:5].sort_by(Axis.Y)[1],
    top.edges().sort_by(Axis.Y)[-4:].sort_by(Axis.Z)[-1],
    top.edges().sort_by_distance(Vertex(-1,0,0))[0],
]
top = chamfer(chamfer_edges, wall)

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
else:
    assert(False)

bottom = extrude(base_plate,amount=wall)

if cable_mount_type == CableMountType.RP2040_SUPERMINI:

    back_edge = top.faces().sort_by(Axis.Y)[0].edges().sort_by(Axis.Z)[0]
    bottom_pos = back_edge.center()
    z_offset = 2

    # Super-mini RP2040 dimensions
    board_width = 18.0
    board_length = 23.9
    board_thickness = 1.0

    usbc_protrusion = 0.85
    usbc_width = 8.8
    usbc_thickness = 3.4

    loc = Pos(bottom_pos) * Pos(0,wall+eta,0)

    bottom += loc * Pos(-board_width/2, board_length, 0) * Box(3,3,z_offset + board_thickness*2, align=align('cc-'))
    bottom += loc * Pos( board_width/2, board_length, 0) * Box(3,3,z_offset + board_thickness*2, align=align('cc-'))
    bottom += loc * Pos(-7/2, 0, 0) * Box(2,3,z_offset-eta, align=align('+--'))
    bottom += loc * Pos( 7/2, 0, 0) * Box(2,3,z_offset-eta, align=align('---'))
    bottom += loc * Box(usbc_width - eta, usbc_protrusion-eta, z_offset + board_thickness - eta, align=align('c+-'))


    for xpos in [-(board_width/2 + 2), +(board_width/2 + 2)]:
        bottom += Pos(bottom_pos) * Pos(xpos,wall+eta,0) * Box(4,4,z_offset+board_thickness+usbc_thickness/2+3, align=align('c--'))
        screw = Pos(bottom_pos) * Pos(xpos,0,z_offset+board_thickness+usbc_thickness/2) * Rot(90,0,0) * M2x4
        top  -= screw
        bottom -= screw

    bottom -= loc * Pos(0,0,z_offset-eta) * Box(board_width+2*eta, board_length+eta, board_thickness+2*eta, align=align('c--'))

    #bottom += loc * Pos(0,0,z_offset) * Box(board_width, board_length, board_thickness, align=align('c--'))

    usbc_sketch = Plane.XZ * fillet(Rectangle(usbc_width+eta*2,usbc_thickness+eta*2, align=align('cc')).vertices(), radius=1.5)
    usbc_loc = loc * Pos(0,-usbc_protrusion,z_offset + board_thickness+usbc_thickness/2)

    top -= usbc_loc * extrude(usbc_sketch, wall, dir=(0,-1,0), taper=-60)
    top -= usbc_loc * extrude(usbc_sketch, wall, dir=(0,1,0))
    top -= usbc_loc * Box(usbc_width,10,10, align=align('c-+'))
    top += loc * Pos(0,-eta,z_offset+board_thickness+usbc_thickness+eta) * Box(3,1,1, align=align('c--'))
else:
    assert(False)

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
