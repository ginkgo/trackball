from build123d import *

ball = 57.2
bearing = 2.5
wall_thickness = 2

base_width=110

arc_radius=300/2
arc_location=(0,-20,-arc_radius)

def make_arc_shell(r1, r2):
    loc = Location(arc_location)

    v = Cylinder(r2, base_width, rotation=(0,90,0))

    if r1 > 0:
        v = v - Cylinder(r2, base_width+10, rotation=(0,90,0))
    return loc * v

trackball=Sphere(radius=ball/2)

board = Location((2.91,0,0)) * Box(34,22,1.5) - Box(18,9,5)
for l in [(-11.09,-8),
          (-11.09,8),
          (+13.41,-8),
          (+13.41,8)]:
    board -= Location(l) * Cylinder(1.6, 10)

loc1 = Rotation(0, 45,-90) * Location((0,0,-ball/2 - 3*wall_thickness))
loc2 = Rotation(0,-45,-90) * Location((0,0,-ball/2 - 3*wall_thickness))
board1 = loc1 * board
board2 = loc2 * board

pizero = Rotation(90,90,0) * Location((-10.5,0,25.5)) * import_step("Pico-R3.step")
pizero = Locations((0,-40, -35)) * pizero


def mk_button_sketch():
    inner = ball/2
    outer = ball/2 + 25

    sketch = CenterArc(center=(0,0), radius=inner, start_angle=0, arc_size=90)
    sketch += Polyline([(0,inner), (0,outer), (inner,outer)])
    #sketch += Line((inner,outer), (outer,inner))
    sketch += RadiusArc((inner,outer,0), (outer,inner,0), radius=outer-inner)
    sketch += Polyline([(outer,inner), (outer,0), (inner,0),])

    face = make_face(sketch)
    face = offset(face, amount=-3)
    return face
button_sketch = mk_button_sketch()

# with BuildPart() as button_mask:
#     add(button_sketch)
#     ex
button_mask = extrude(button_sketch, amount=-60)
    
with BuildPart() as top:
    with Locations(arc_location):
        Cylinder(arc_radius, base_width, rotation=(0,90,0))
    # add(make_arc_shell(0, arc_radius))
    
    with Locations((0,30,0)):
        Box(base_width, base_width+60, ball+15, mode=Mode.INTERSECT)
    Sphere(radius=(ball+bearing)/2, mode=Mode.SUBTRACT)
    Cylinder(8,100,mode=Mode.SUBTRACT)

    with Locations([Rotation(0,0,angle) * Rotation(70,0,0) * Location((0,0,-ball/2-bearing/2))  for angle in range(60,360+60,120)]):
        Cylinder(bearing/2, bearing, mode=Mode.SUBTRACT)
    
    base_plate = top.faces().sort_by(Axis.Z)[0]
    offset(top.solids()[0], amount=-wall_thickness, openings=base_plate)

        
    top_edges = top.faces().sort_by(Axis.Z)[-1:].edges().sort_by(Axis.Y)[:-1]
    back_edges = top.faces().sort_by(Axis.Y)[:1].edges().sort_by(Axis.Z)[1:]
    
    fillet(top_edges + back_edges, radius=wall_thickness)

    with PolarLocations(radius=0, count=4):
        add(button_mask, mode=Mode.SUBTRACT)
        
    with Locations([loc1, loc2]):
        Cylinder(2, 20, mode=Mode.SUBTRACT)

    with Locations((0,0,-32)):
        Cone(bottom_radius=0, top_radius=12, height=12, mode=Mode.SUBTRACT)
    
result = {
    'ball': trackball,
    'top': top,
    'board1': board1,
    'board2': board2,
    'pizero': pizero,
}
