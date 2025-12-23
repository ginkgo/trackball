from build123d import *
from enum import Enum
import sys
import math
from trackball_common import *

# All measurements in millimeters

# Ball diameter (pick one)
ball = 57.2    # pool billiards ball
#ball = 52.4   # snooker ball
#ball = 55     # Kensington ball

suspension_type = SuspensionType.BALL_TRANSFER_UNIT

cable_mount_type = CableMountType.RP2040_SUPERMINI

# Thickness of walls
wall = 2

# Bearing diameter
bearing = 2.5

skip_buttons = False
skip_usb_plug = False
skip_pcbs = False

trackball = Sphere(radius=ball/2)

bottom_hole_radius = 8

if suspension_type == SuspensionType.BEARING_BALL:
    bowl_radius = (ball+bearing)/2
elif suspension_type == SuspensionType.BALL_TRANSFER_UNIT:
    bowl_radius = ((ball/2 + btu_L1)**2 + (btu_D/2)**2)**0.5
else:
    assert(False)


plate_angle = 13.5
angle_r = plate_angle*math.pi/180
profile = Polyline([(0,-60,-ball/2),
                    (0, 50,-ball/2),
                    (0, 48, math.tan(angle_r) * -48),
                    (0,-48, math.tan(angle_r) *  48),
                    (0,-60,-ball/2+10),
                    (0,-60,-ball/2),
                    ])

top = extrude(make_face(profile), amount=100/2, dir=(1,0,0), both=True)
top -= Rotation(0,0,math.pi) * Sphere(radius=bowl_radius)
top -= Cylinder(radius=15,height=100)

front_face = top.faces().sort_by(Axis.Y)[-1]

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
top_original = top

base_plate = top.faces().sort_by(Axis.Z)[0]
top = offset(top.solids()[0], amount=-wall, openings=base_plate)

front_face_front_edge = front_face.edges().sort_by(Axis.Z)[0]
front_face_center_pos = front_face_front_edge.center()
wrist_rest = loft([front_face, Pos(front_face_center_pos) * Pos(0,70,0) * Rot(90+50,0,0) * Rectangle(front_face_front_edge.length, 10, align=align('c-c'))])
wrist_rest = chamfer(wrist_rest.edges().sort_by(Axis.Z)[4:], wall)
wrist_rest += extrude(wrist_rest.faces().sort_by(Axis.Z)[0], amount=wall)
for loc in [front_face.location_at(*uv) for uv in [(0.5,0.2), (0.5,0.8)]]:
    wrist_rest -= loc * Cylinder(radius=5+eta/2, height=3+eta)
    top += loc * Pos(0,0,-wall) * Cone(top_radius=7, bottom_radius=5.5, height=0.5, align=align('cc+'))
    top -= loc * Pos(0,0,-wall) * Cylinder(radius=5.1, height=2, align=align('cc+'))

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

bottom = Compound()
bottom += extrude(base_plate,amount=wall)

top = Part() + top
bottom = Part() + bottom

shrunk_bottom_face = offset(bounding_box(bottom).faces().sort_by(Axis.Z)[-1], amount=-4)
bottom_points = shrunk_bottom_face.vertices() + \
    [Vertex(shrunk_bottom_face.edges().sort_by(Axis.X)[0].center()), \
     Vertex(shrunk_bottom_face.edges().sort_by(Axis.X)[-1].center())]

for p in bottom_points:
    pd = Vector(p).normalized()
    extrude_dir = pd.cross(Vector(0,0,1).cross(pd).normalized())
    top += extrude(Pos(p) * Pos(0,0,eta) * Circle(radius=4), until=Until.NEXT, target=top, dir=extrude_dir)
    top -= Pos(p) * Cone(bottom_radius=3.5, top_radius=2, height=1, align=align('cc-'))
    bottom += Pos(p) * Cone(bottom_radius=3.5-eta, top_radius=2-eta, height=1-eta, align=align('cc-'))

    top -= Pos(0,0,-wall) * Pos(p) * Rot(180,0,0) * M3x4
    bottom -= Pos(0,0,-wall) * Pos(p) * Rot(180,0,0) * M3x4

inner_radius = ball/2 + 3
button_width = 48
outer_radius = 15
button_sketch = make_face([TangentArc([(0,inner_radius,0),
                                                        (inner_radius,0,0)], tangent=(1,0,0)),
                                            Polyline([(inner_radius, 0,0),
                                                      (button_width, 0,0),
                                                      (button_width, button_width-outer_radius, 0)]),
                                            TangentArc([(button_width, button_width-outer_radius, 0),
                                                        (button_width-outer_radius, button_width, 0)], tangent=(0,1,0)),
                                            Polyline([(button_width-outer_radius, button_width, 0),
                                                      (0, button_width, 0),
                                                      (0, inner_radius, 0)])])

button_sketch = offset(button_sketch, amount=-1.5)

def plot2d(start, offsets):
    points = [Vector(start)]
    for o in offsets:
        np = o + points[-1]
        points.append(np)

    points.append(points[0]) # Close

    return Polyline(points)

def mk_g304_keyswitch_pcb(loc, mirror_sketch):
    global bottom
    pcb_thickness = 0.75

    # Base board
    X = Vector(1,0)
    Y = Vector(0,1)
    start = (-5.65, -10.5)
    sketch = plot2d(start, [5.5*X, -5*Y, 5.4*X, 5*Y, -2.1*X, 21*Y, -8.8*X, -4.9*Y, 2.5*X, -11.2*Y, -2.5*X])

    if mirror_sketch:
        sketch = mirror(sketch, Plane.YZ)

    part = extrude(make_face(sketch), pcb_thickness, dir=(0,0,1))

    part += Pos(0,-4.2) * Cylinder(0.9, 2.75, align=align('cc+'))
    part += Pos(0,   0) * Cylinder(0.9, 2.75, align=align('cc+'))
    part += Pos(0, 4.2) * Cylinder(0.9, 2.75, align=align('cc+'))

    # Keyswitch
    switch_length=12.8
    switch_width=5.7
    switch_height=6.5
    part += Pos(0,0,pcb_thickness) * Box(switch_width,switch_length,switch_height, align=align('cc-'))
    part += Pos(0,2,pcb_thickness+switch_height) * Box(2.9,1.2,1, align=align('cc-'))

    # Find keyswitch contact position (it's the center of the top-most face)
    top_loc = part.faces().sort_by(Axis.Z)[-1].center()
    loc = loc * Pos(-top_loc)

    # Screw holes
    hole_positions = [Pos(0,-8.6), Pos(0,8.6)]
    for hp in hole_positions:
        part -= hp * Cylinder(1.6/2,3)

        leg1 = extrude(loc * hp * Rotation(180,0,0) * Circle(2.5), until=Until.LAST, target=bottom)
        leg2 = extrude(loc * hp * Pos(0,0,-1) * Rotation(180,0,0) * Circle(2.5), dir=(0,0,-1), until=Until.NEXT, target=bottom)

        bottom = leg1 + leg2 + bottom
        bottom -= (loc * hp * Cylinder(1.6/2, 4.1, align=align('cc+')))

    return loc * part

keyswitch_pcbs = []
def add_button(loc, flip_pcb):
    global button_sketch
    global top
    global keyswitch_pcbs

    top = loc.inverse() * top
    top = Compound([top])

    extra = wall/2
    D1 = 1
    D2 = 0.25

    top += loft([Pos(0,0,-wall)       * offset(button_sketch, amount=0.5),
                 Pos(0,0,-wall-extra) * offset(button_sketch, amount=0.5)], ruled=True)

    top -= loft([Pos(0,0,0)           * offset(button_sketch, amount=0),
#                Pos(0,0,-wall)       * offset(button_sketch, amount=-wall-(D1-D2)/3),
                  Pos(0,0,-wall-(D1-D2)/2)       * offset(button_sketch, amount=-wall-(D1-D2)/2),
                 Pos(0,0,-wall-extra) * offset(button_sketch, amount=-wall+extra-D1+D2)], ruled=True)

    top += loft([Pos(0,0,0)           * offset(button_sketch, amount=-D1),
                 Pos(0,0,-wall)       * offset(button_sketch, amount=-wall-D1),
                 Pos(0,0,-wall-extra) * offset(button_sketch, amount=-wall+extra-D1)], ruled=True)

    # top += Rotation(0,0,-45) * Box(wall,50,wall, align=align('c-+'))
    top = Part() + top

    height = 4
    width = 4

    bridge_face = make_face([Polyline([(-width/2, 0, 0),
                                       (-width/2, 0, -2*print_resolution),
                                       (-width/4, 0, -3*print_resolution),
                                       ( width/4, 0, -3*print_resolution),
                                       ( width/2, 0, -2*print_resolution),
                                       ( width/2, 0, 0),
                                       (-width/2, 0, 0)])])

    for pos, angle in [(Pos(inner_radius + 7, 8, 0), -45),
                       (Pos(8, inner_radius + 7, 0), -45),
                       (Pos(button_width-19, inner_radius + 8, 0), 135),
                       (Pos(inner_radius + 8, button_width-19, 0), 135),
#                       (Pos(inner_radius + 6.5, inner_radius + 6.5, 0), -45),
                       ]:
        extrude_dir = Vector(0,1,0).rotate(Axis.Z, angle)
        face = pos * Pos(0,0,-height) * Rotation(0,0,angle) * Pos(0,-width/2,0) * bridge_face
        top += extrude(face, dir=extrude_dir, until=Until.NEXT, target=top)
        top += pos * Rotation(0,0,angle) * Box(width,width,height, align=align('cc+'))

    pusher_width = 5
    pusher_depth = 5
    tension = 0.25 # Move keyswitch 0.5mm in for tension
    pusher_pos = Pos(button_sketch.center()) * Pos(0,0,-pusher_depth)
    top += pusher_pos * Box(pusher_width,pusher_width,pusher_depth, align=align('cc-'))
    keyswitch_pcbs.append(mk_g304_keyswitch_pcb(loc * pusher_pos * Pos(0,0,tension) * Rotation(0,0,135), flip_pcb))

    top = loc * top.solid()
    #top = ShapeList([loc * s for s in top.solids()])

if not skip_buttons:
    for i,angle in enumerate([0,90,180,270]):
        add_button(Rotation(-plate_angle, 0, angle), i%2 == 0)

if skip_usb_plug:
    None
elif cable_mount_type == CableMountType.RP2040_SUPERMINI:

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

    bottom_notch_face = make_face([Polyline([(0,-wall-eta,0),
                                             (0, wall,0),
                                             (0, wall,z_offset+board_thickness-eta),
                                             (0,-wall+usbc_protrusion,z_offset+board_thickness-eta),
                                             (0,-wall,1),
                                             (0,-wall-eta,0)])])
    bottom += loc * extrude(bottom_notch_face, (usbc_width-eta)/2, both=True)
    #bottom += loc * Box(usbc_width - eta, usbc_protrusion-eta + 1, z_offset + board_thickness - eta, align=align('c+-'))


    for xpos in [-(board_width/2 + 2), +(board_width/2 + 2)]:
        bottom += Pos(bottom_pos) * Pos(xpos,wall+eta,0) * Box(4,4,z_offset+board_thickness+usbc_thickness/2+3, align=align('c--'))
        screw = Pos(bottom_pos) * Pos(xpos,0,z_offset+board_thickness+usbc_thickness/2) * Rot(90,0,0) * M2x4
        top  -= screw
        bottom -= screw

    bottom -= loc * Pos(0,0,z_offset-eta) * Box(board_width+2*eta, board_length+eta, board_thickness+2*eta, align=align('c--'))

    top -= Pos(bottom_pos) * Box(usbc_width,wall*2,z_offset+board_thickness+usbc_thickness/2, align=align('c--'))

    #bottom += loc * Pos(0,0,z_offset) * Box(board_width, board_length, board_thickness, align=align('c--'))

    usbc_sketch = Plane.XZ * fillet(Rectangle(usbc_width+eta*2,usbc_thickness+eta*2, align=align('cc')).vertices(), radius=1.5)
    usbc_loc = loc * Pos(0,-usbc_protrusion,z_offset + board_thickness+usbc_thickness/2)

    top -= usbc_loc * extrude(usbc_sketch, wall, dir=(0,-1,0), taper=-60)
    top -= usbc_loc * extrude(usbc_sketch, wall, dir=(0,1,0))
    top -= usbc_loc * Box(usbc_width,10,10, align=align('c-+'))

    notch_face = make_face([Polyline([(0,0,0),
                                      (0,0,3),
                                      (0,1,0),
                                      (0,0,0),])])
    top += loc * Pos(0,-eta,z_offset+board_thickness+usbc_thickness+eta) * extrude(notch_face, amount=3, both=True)
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

result = {}
if not skip_pcbs:
    result['sensor_pcb1'] = mk_sensor_pcb(Rotation(0, 60,-90) * Pos(0,0,-ball/2 - 7.41))
    result['sensor_pcb2'] = mk_sensor_pcb(Rotation(0,-60,-90) * Pos(0,0,-ball/2 - 7.41))

result['ball'] = trackball
result['top'] = top
result['bottom'] = bottom
result['wrist_rest'] = wrist_rest

for i,keyswitch in enumerate(keyswitch_pcbs):
    result[f'keyswitch_pcb{i}'] = keyswitch

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
