from build123d import *
from enum import Enum
import sys

# All measurements in millimeters

# Ball diameter (pick one)
ball = 57.2    # pool billiards ball
#ball = 52.4   # snooker ball
#ball = 55     # Kensington ball

# Thickness of walls
wall = 2

base_width=110
base_height=(ball+10)/2

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

add_logo=False
add_text=''

class CableMountType(Enum):
    # Simple hole in the back to lead cable connected to RaspPi Pico to
    HOLE = 1

    # USB-C plug in back
    USBC_PLUG = 2

    # Use a RP2040 Super-Mini board instead of pi pico and place it in back so
    # the USB-C plug can be used directly
    RP2040_SUPERMINI = 3

cable_mount_type = CableMountType.RP2040_SUPERMINI

class SwitchPCBType(Enum):
    # Jacek Fedoryński's key switch PCB
    JFEDOR2 = 1

    # G304/G305 replacement key switch PCB
    G304 = 2

switch_pcb_type = SwitchPCBType.G304

# Parameters of trackball case arc
arc_radius=300/2
arc_location=(0,-20,-arc_radius)

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

eta = 0.1 # General tolerance

def mk_arc_shell(r1, r2):
    loc = Location(arc_location)

    v = Cylinder(r2, base_width, rotation=(0,90,0))

    if r1 > 0:
        v = v - Cylinder(r1, base_width+10, rotation=(0,90,0))
    return loc * v

trackball=Sphere(radius=ball/2)

def mk_button_sketch():
    inner = ball/2
    outer = ball/2 + 25

    line = CenterArc(center=(0,0), radius=inner, start_angle=0, arc_size=90)
    line += Polyline([line @ 1, (0,outer), (inner,outer)])
    #sketch += Line((inner,outer), (outer,inner))
    line += RadiusArc(line @ 1, (outer,inner), radius=outer-inner)
    line += Polyline([line @ 1, (outer,0), (inner,0)])

    face = make_face(line)
    face = offset(face, amount=-3)

    return face
button_sketch = mk_button_sketch()
button_mask = extrude(button_sketch, amount=-60)

bottom_hole_radius = 8

if suspension_type == SuspensionType.BEARING_BALL:
    bowl_radius = (ball+bearing)/2
elif suspension_type == SuspensionType.BALL_TRANSFER_UNIT:
    bowl_radius = ((ball/2 + btu_L1)**2 + (btu_D/2)**2)**0.5
else:
    assert(False)

def mk_top():
    part = Part()
    part += mk_arc_shell(0,arc_radius)
    part &= Pos(0,30,0) * Box(base_width, base_width+60, base_height*2)

    part -= Sphere(radius=bowl_radius)
    part -= Cylinder(bottom_hole_radius,100)

    if suspension_type == SuspensionType.BEARING_BALL:
        # Cut holes for bearing balls before offset
        locs = (Rotation(0,0,angle) * Rotation(70,0,0) * Pos(0,0,-(ball+bearing)/2)  for angle in range(60,360+60,120))
        part -= [loc * Cylinder(bearing/2, bearing + eta) for loc in locs]

    base_plate = part.faces().sort_by(Axis.Z)[0]
    part = offset(part.solids()[0], amount=-wall, openings=base_plate)

    fillet_edges = [
        part.edges().sort_by(Axis.Z)[-1],
        part.edges().sort_by(Axis.X)[-3:].sort_by(Axis.Z)[-1],
        part.edges().sort_by(Axis.X)[:3].sort_by(Axis.Z)[-1],
        part.edges().sort_by(Axis.Y)[:4].sort_by(Axis.Z)[-1],
        part.edges().sort_by(Axis.Y)[:4].sort_by(Axis.X)[0],
        part.edges().sort_by(Axis.Y)[:4].sort_by(Axis.X)[-1],
        part.edges().sort_by_distance(Vertex(-1,0,-ball/2))[0],
    ]
    part = chamfer(fillet_edges, wall )

    if suspension_type == SuspensionType.BALL_TRANSFER_UNIT:
        # Cut holes for BTUs at the end
        for angle in range(0,360+60,120):
            loc = Rotation(-8,0,0) * Rotation(0,0,angle) * Rotation(60,0,0) * Pos(0,0,-(ball/2+btu_L1))

            part += loc * Pos(0,0,-eta/2) * Cylinder(btu_D/2+wall, btu_H+wall, align=align('cc+'))
            part -= loc * Cylinder(btu_D/2 + eta, 2* (btu_H + eta), align=align('ccc'))
            part -= loc * Cylinder(btu_D1/2 + eta, 2* (btu_H + btu_L), align=align('ccc'))

    rots = [Rotation(0,0,angle) for angle in range(0,360,90)]
    part -= [r * button_mask for r in rots]

    if add_logo:
        logo = make_face(import_svg('ginkgoleaf.svg'))
        logo = logo.scale(0.1)
        logo = Pos(-logo.center()) * logo
        logo = Pos(12,-14) * Pos(-base_width/2,75,0) * Rotation(0,0,180+30) * logo
        part -= [extrude(f.project_to_shape_alt(part, direction=(0,0,-1)),-0.5, dir=(0,1,1)) for f in logo.faces()]

    if add_text:
        text = Text(add_text, font_size=8, font="Helvetica Neue", font_style=FontStyle.ITALIC, align=Align.MIN)
        text = Rotation(0,0,180) * Pos(-base_width/2+5,-71,0) * text
        part -= [extrude(f.project_to_shape(part, direction=(0,0,-1)),-0.5, dir=(0,1,1)) for f in text.faces()]

    return part
top = mk_top()

def mk_bottom():
    global top
    part = Part()

    bottom_face = top.faces().filter_by(Axis.Z)[0]
    hole_face = top.faces().filter_by(Axis.Z)[1]

    outer = Face(bottom_face.outer_wire(), hole_face.inner_wires())
    inner = make_face(bottom_face.inner_wires()[0])

    #hole_face = offset(hole_face, 0.5)

    #outer = outer.faces()[0].make_holes([hole_face.outer_wire()])

    part += extrude(outer, wall, dir=(0,0,-1))
    #part += extrude(inner, wall, dir=(0,0,1)) - top

    # Add front notch in top
    front_edge = top.edges().sort_by(Axis.Y)[-1]
    front_pos = front_edge.center()
    top += (Pos(front_pos) * Box(front_edge.length, 5, 20, align=align('c+-'))) & mk_arc_shell(0,arc_radius - wall/2)

    # Add front notch in bottom
    notch_loc = Pos(0,-5 - 0.5,0) * Pos(front_edge.center())
    notch_width = base_width - wall * 2.5
    part += notch_loc * Box(notch_width*.8, wall, 5, align=align('c+-')) & mk_arc_shell(0, arc_radius - wall - 0.5)

    # Add back notch in bottom
    back_edge = top.faces().sort_by(Axis.Y)[0].edges().sort_by(Axis.Z)[0]
    bottom_pos = back_edge.center()
    part += Pos(0,wall+eta,0) * Pos(bottom_pos) * Box(base_width*0.66, wall, wall, align=align('c--'))

    # Add right notch
    right_edge = bottom_face.edges().sort_by(Axis.X)[0]
    right_pos = right_edge.center()
    part += Pos(wall+eta,0,0) * Pos(right_pos) * Box(wall, right_edge.length*0.4, wall, align=align('-c-'))

    # Add left notch
    left_edge = bottom_face.edges().sort_by(Axis.X)[-1]
    left_pos = left_edge.center()
    part += Pos(-wall-eta,0,0) * Pos(left_pos) * Box(wall, left_edge.length*0.4, wall, align=align('+c-'))

    # Add ring-shaped notch around cup hole on bottom
    ring_pos = Pos(hole_face.center())
    ring_height = wall
    ring =  Cylinder(bottom_hole_radius + 2*wall,       ring_height, align=align('cc-'))
    ring -= Cylinder(bottom_hole_radius + 1*wall + 0.1, ring_height, align=align('cc-'))
    ring -= Box(wall+0.2,30,wall, align=align('c--'))
    part += ring_pos * ring

    # Add hole alignment notch to top part
    top += ring_pos * Pos(0,bottom_hole_radius,0) * Box(wall*0.75,wall*2,wall, align=align('c--'))

    # Add screw holes
    bottom_corners = bounding_box(part).faces().sort_by(Axis.Z)[0].vertices()
    hole_positions = [
        Pos( 4.5, 4.5)  * Pos(bottom_corners.sort_by(Axis.Y)[:2].sort_by(Axis.X)[0]),
        Pos(-4.5, 4.5)  * Pos(bottom_corners.sort_by(Axis.Y)[:2].sort_by(Axis.X)[1]),
        Pos( 6,-6) * Pos(bottom_corners.sort_by(Axis.Y)[2:].sort_by(Axis.X)[0]),
        Pos(-6,-6) * Pos(bottom_corners.sort_by(Axis.Y)[2:].sort_by(Axis.X)[1]),
    ]

    for pos in hole_positions:
        top  += (pos  * Pos(0,0,wall) * Cylinder(radius=3, height=100, align=align('cc-'))) & mk_arc_shell(0,arc_radius-wall)
        part -= pos  * Rot(180,0,0) * M3x4
        top  -= pos  * Rot(180,0,0) * M3x4

    if cable_mount_type == CableMountType.HOLE:
        # Cut hole for USB cable in top
        hole_radius=3
        hole_sketch = [
            Polyline([(hole_radius,0,hole_radius),
                      (hole_radius,0,0),
                      (-hole_radius,0,0),
                      (-hole_radius,0,hole_radius)]),
            ThreePointArc([(-hole_radius,0,hole_radius),
                           (0,0,hole_radius*2),
                           (hole_radius,0,hole_radius)])
        ]

        top -= Pos(bottom_pos) * extrude(make_face(hole_sketch), amount=3, dir=(0,1,0))
        part -= Pos(bottom_pos) * extrude(make_face(hole_sketch), amount=10, dir=(0,1,0))
    elif cable_mount_type == CableMountType.USBC_PLUG:
        loc = Pos(bottom_pos) * Pos(0,wall,6)

        usbc_sketch = Plane.XZ * fillet(Rectangle(8.34,2.56).vertices(), radius=1.25)
        top -= loc * extrude(usbc_sketch, wall, dir=(0,-1,0), taper=-60)

        hole_dist = 16.15
        top -= loc * Rot(90,0,0) * Pos( hole_dist/2,0,0) * Cylinder(radius=0.95, height=1.5, align=align('cc-'))
        top -= loc * Rot(90,0,0) * Pos(-hole_dist/2,0,0) * Cylinder(radius=0.95, height=1.5, align=align('cc-'))
    elif cable_mount_type == CableMountType.RP2040_SUPERMINI:
        z_offset = 4

        # Super-mini RP2040 dimensions
        board_width = 18.0
        board_length = 23.9
        board_thickness = 1.0

        usbc_protrusion = 0.85
        usbc_width = 8.8
        usbc_thickness = 3.4

        loc = Pos(bottom_pos) * Pos(0,wall+eta,0)

        part += loc * Pos(-board_width/2, board_length, 0) * Box(3,3,z_offset + board_thickness*2, align=align('cc-'))
        part += loc * Pos( board_width/2, board_length, 0) * Box(3,3,z_offset + board_thickness*2, align=align('cc-'))
        part += loc * Pos(-7/2, 0, 0) * Box(2,3,z_offset-eta, align=align('+--'))
        part += loc * Pos( 7/2, 0, 0) * Box(2,3,z_offset-eta, align=align('---'))
        part += loc * Box(usbc_width - eta, usbc_protrusion-eta, z_offset + board_thickness - eta, align=align('c+-'))


        for xpos in [-(board_width/2 + 2), +(board_width/2 + 2)]:
            part += Pos(bottom_pos) * Pos(xpos,wall+eta,0) * Box(4,4,z_offset+board_thickness+usbc_thickness/2+3, align=align('c--'))
            screw = Pos(bottom_pos) * Pos(xpos,0,z_offset+board_thickness+usbc_thickness/2) * Rot(90,0,0) * M2x4
            top  -= screw
            part -= screw

        part -= loc * Pos(0,0,z_offset-eta) * Box(board_width+2*eta, board_length+eta, board_thickness+2*eta, align=align('c--'))

        #part += loc * Pos(0,0,z_offset) * Box(board_width, board_length, board_thickness, align=align('c--'))

        usbc_sketch = Plane.XZ * fillet(Rectangle(usbc_width+eta*2,usbc_thickness+eta*2, align=align('cc')).vertices(), radius=1.5)
        usbc_loc = loc * Pos(0,-usbc_protrusion,z_offset + board_thickness+usbc_thickness/2)

        top -= usbc_loc * extrude(usbc_sketch, wall, dir=(0,-1,0), taper=-60)
        top -= usbc_loc * extrude(usbc_sketch, wall, dir=(0,1,0))
        top -= usbc_loc * Box(usbc_width,10,10, align=align('c-+'))
        top += loc * Pos(0,-eta,z_offset+board_thickness+usbc_thickness+eta) * Box(3,1,1, align=align('c--'))

        #part += usbc_loc * extrude(usbc_sketch, amount=7.5, dir=(0,1,0))

        None
    else:
        assert(False)

    return part
bottom = mk_bottom()


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

    top -= loc * Pos(0,0,7.41) * extrude(face, amount=20, dir=(0,0,-1), taper=68.5-90)

    return loc * board

sensor_pcb1 = mk_sensor_pcb(Rotation(0, 45,90) * Pos(0,0,-ball/2 - 7.41))
sensor_pcb2 = mk_sensor_pcb(Rotation(0,-45,90) * Pos(0,0,-ball/2 - 7.41))

def mk_pipico(pos):
    global top
    global bottom

    part = Box(51,21,1, align=align('cc-'))
    part += Pos(51/2 + 1.3, 0, 1) * Box(5,8,2, align=align('+c-'))

    hole_positions = [Pos(x,y,0) for x in [-23.5, 23.5] for y in [-5.7, 5.7]]
    part -= [p * Cylinder(2.1/2, 4) for p in hole_positions]

    bbox = bounding_box(top)
    bottom += [bbox & pos * p * Cylinder(2,10, align=align('cc+')) for p in hole_positions]
    bottom -= [pos * p * Cylinder(0.9,3, align=align('cc+')) for p in hole_positions]

    return pos * part
if cable_mount_type != CableMountType.RP2040_SUPERMINI:
    pipico = mk_pipico(Pos(0,45, -30))


def mk_button(angle):
    global bottom
    rot = Rotation(0,0,angle)

    button = mk_arc_shell(arc_radius - wall - 1, arc_radius + wall/2)
    button &= Pos(0,0,10) * extrude(offset(rot * button_sketch,amount=-0.75), amount=-60)

    edges = button.edges()
    button = chamfer(edges, 0.5)

    notch = mk_arc_shell(arc_radius - wall - 1.5, arc_radius - wall - 0.5)
    notch &= Pos(0,0,10) * extrude(offset(rot * button_sketch,amount=1), amount=-60)
    notch -= Pos(0,0,10) * extrude(offset(rot * button_sketch,amount=-3), amount=-60)
    notch -= Cylinder(ball/2 + 4, 100)

    button += notch

    rod_width = 5

    strip_axis = (-Axis.Z).located(Rotation(0,0,angle-45) * Pos(0,ball/2+9,0))
    strip_pos = mk_arc_shell(0,arc_radius).find_intersection_points(strip_axis)[0][0]
    strip_loc = Pos(0,0,-8) * Pos(*strip_pos) * Rotation(0,0,angle-45)

    dy = 17
    dz = -10
    strip_thickness=wall/4
    strip_width=2*rod_width
    strip_path  = Line(  [(           0,  0), (     rod_width,  0)])
    strip_path += Spline([(   rod_width,  0), (  rod_width+dy, dz)], tangents=[(1,0), (1,-0.25)])
    strip_path += Line(  [(rod_width+dy, dz), (1.5*rod_width+dy, dz)])
    strip_cross_section = Rectangle(strip_width, strip_thickness, align=align('c--'))

    strip = sweep(sections=Plane.XZ * strip_cross_section, path=Plane.YZ * strip_path)
    strip += Box(strip_width, rod_width, 3, align=align('c--'))
    strip += Box(strip_width, rod_width, 1, align=align('c-+'))
    strip += Pos(0,rod_width+dy, dz) * Box(strip_width, rod_width, 50, align=align('c-+'))
    strip += Pos(0,rod_width+dy+rod_width/2, dz) * Rotation(0,90,0) * Cylinder(rod_width/2, strip_width)
    strip -= Pos(0,rod_width+dy+rod_width/2, dz) * Rotation(0,90,0) * Cylinder(rod_width/4, strip_width)

    # Fillet strip attachment point
    fillet_edge_positions = [
        Vertex(0,rod_width+dy,dz + strip_thickness),
        Vertex(0,rod_width+dy,dz ),
        Vertex(0,rod_width, +strip_thickness),
    ]
    fillet_edges = [strip.edges().sort_by_distance(pos)[0] for pos in fillet_edge_positions]
    strip = fillet(fillet_edges, wall)

    button += (strip_loc * Pos(0,-wall,-1) * Box(strip_width+2*wall, rod_width+wall, 100, align=align('c--'))) & mk_arc_shell(0,arc_radius)
    button -= strip_loc * Pos(0,0,-1) * Box(strip_width+0.2, rod_width+0.1, 4+0.1, align=align('c--'))

    strip = (strip_loc * strip) & mk_arc_shell(0,arc_radius) & bounding_box(top)

    # screw holes attaching buttons to strip
    for l in [strip_loc * Pos(-3,-wall,1),
              strip_loc * Pos( 3,-wall,1)]:
        strip  -= l * Rot(90,0,0) * M2x3
        button -= l * Rot(90,0,0) * M2x3

    bottom_face = strip.faces().sort_by(Axis.Z)[0]
    bottom += extrude(offset(bottom_face, amount=wall), amount=-6)
    bottom -= extrude(offset(bottom_face, amount=0.1), amount=-6)

    return button, strip
buttons, strips = zip(*[mk_button(a) for a in range(0,360,90)])

def mk_jfedor2_keyswitch_pcb(pos, rot):
    global bottom

    # Base board
    part = Box(8,30,1.4, align=align('cc-'))

    # Keyswitch
    part += Pos(0,2,1.4) * Box(5.8,12.8,6.5, align=align('cc-'))
    part += Pos(0,0,1.4+6.5) * Box(2.9,1.2,1, align=align('cc-'))

    # Screw holes
    part -= Pos(0,-12,0) * Cylinder(1,3)
    part -= Pos(0,+12,0) * Cylinder(1,3)

    # Find keyswitch contact position (it's the center of the top-most face)
    top_loc = part.faces().sort_by(Axis.Z)[-1].center()
    loc = pos * Pos(-top_loc) * rot

    # Add screw posts to bottom part
    for p in [Pos(0,-12,-eta), Pos(0,+12,-eta)]:
        bottom += (loc * p * Cylinder(3, 30, align=align('cc+'))) & bounding_box(top)
        bottom -= (loc * p * Cylinder(0.9, 3.1, align=align('cc+')))

    return loc * part

def plot2d(start, offsets):
    points = [Vector(start)]
    for o in offsets:
        np = o + points[-1]
        points.append(np)

    points.append(points[0]) # Close

    return Polyline(points)

def mk_g304_keyswitch_pcb(pos, rot, mirror_sketch):
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
    loc = pos * rot * Pos(-top_loc)

    # Screw holes
    hole_positions = [Pos(0,-8.6), Pos(0,8.6)]
    for hp in hole_positions:
        part -= hp * Cylinder(1.6/2,3)

        bottom += (loc * hp * Cylinder(  2.5,  30, align=align('cc+'))) & bounding_box(top)
        bottom -= (loc * hp * Cylinder(1.6/2, 4.1, align=align('cc+')))

    return loc * part

button_pcbs = []
for i,b in enumerate(strips):
    p = b.faces().filter_by(Axis.Z).sort_by_distance((0,0,-ball/2))[0].center()
    rot = Rotation(0,0,90) if (i not in [1,2]) else Rotation(0,0,-90)

    if switch_pcb_type == SwitchPCBType.JFEDOR2:
        pcb = mk_jfedor2_keyswitch_pcb(Pos(p), rot)
    elif switch_pcb_type == SwitchPCBType.G304:
        pcb = mk_g304_keyswitch_pcb(Pos(p), rot, mirror_sketch=(i in [2,3]))
    button_pcbs.append(pcb)

result = {
    'ball': trackball,
    'top': top,
    'bottom': bottom,
    'sensor_pcb1': sensor_pcb1,
    'sensor_pcb2': sensor_pcb2,
}

if cable_mount_type != CableMountType.RP2040_SUPERMINI:
    result['pipico'] = pipico

for i,b in enumerate(buttons):
    result[f'button{i}'] = b

for i,s in enumerate(strips):
    result[f'strip{i}'] = s

for i,b in enumerate(button_pcbs):
    result[f'button_pcb{i}'] = b

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
