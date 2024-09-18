from build123d import *

ball = 57.2
bearing = 2.5
wall_thickness = 2

base_width=110

arc_location=(0,-20,-base_radius)
arc_radius=300/2

def make_arc_shell(r1, r2):
    loc = Location(arc_location)

    v = Cylinder(r2, base_width, rotation=(0,90,0))

    if r1 > 0:
        v = v - Cylinder(r2, base_width+10, rotation=(0,90,0))
    return loc * v

trackball=Sphere(radius=ball/2)

# with BuildPart() as board:
#     with Locations((10,0,0)):
#         Box(44,44,1.5)
#         with Locations([(+18,+18,0),
#                         (+18,-18,0),
#                         (-18,+18,0),
#                         (-18,-18,0),]):
#             Cylinder(1.6, 10, mode=Mode.SUBTRACT)
                        
#     Box(18,9,5, mode=Mode.SUBTRACT)
#     # with Locations((0,0,5)):
#     #     add(import_step("rp2040-pmw3360.step"))
#     #board = import_step("/home/tom/Development/trackball/rp2040-pmw3360/kicad/Trackball.step")

with BuildPart() as board:
    with Locations((2.91,0,0)):
        Box(34,22,1.5)
    Box(18,9,5, mode=Mode.SUBTRACT)

    with Locations([(-11.09,-8),
                    (-11.09,8),
                    (+13.41,-8),
                    (+13.41,8)]):
        Cylinder(1.6, 10, mode=Mode.SUBTRACT)

with BuildPart() as board_location:
    loc1 = Rotation(0, 45,-90) * Location((0,0,-ball/2 - 3*wall_thickness))
    loc2 = Rotation(0,-45,-90) * Location((0,0,-ball/2 - 3*wall_thickness))
    
    with Locations([loc1, loc2]):        
        add(board)


with BuildPart() as pizero:
    with Locations((0,-40, -35)):
        add(Rotation(90,90,0) * Location((-10.5,0,25.5)) * import_step("Pico-R3.step"))
        
with BuildPart() as button_mask:
    with BuildSketch(Plane.XY) as button_sketch:
        with BuildLine(Plane.XY) as line:
            inner = ball/2
            outer = ball/2 + 25
            CenterArc(center=(0,0), radius=inner, start_angle=0, arc_size=90)
            Polyline([(0,inner), (0,outer), (inner,outer)])
            Line((inner,outer), (outer,inner))
            #RadiusArc((inner,outer,0), (outer,inner,0), radius=outer-inner)
            Polyline([(outer,inner), (outer,0), (inner,0),])
        make_face()
        offset(button_sketch.faces()[0], amount=-3)
        fillet(button_sketch.vertices(), radius=3)
        #offset(button_sketch.faces()[0], amount=+0.5)
    extrude(amount=-60)
    
with BuildPart() as top:
    with Locations(arc_location):
        Cylinder(base_radius, base_width, rotation=(0,90,0))
    # add(make_arc_shell(0, base_radius))
    
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

with BuildPart() as base:
    
    offset(base_plate, amount=-3)
    extrude(amount=wall_thickness)
        
with BuildPart() as button:
    for angle in range(0,360,90):
        with Locations((0,0,1.5)):
            with Locations((0,-20,-base_radius)):
                Cylinder(base_radius, base_width, rotation=(0,90,0))
            with Locations((0,30,0)):
                Box(base_width, base_width+60, ball+10, mode=Mode.INTERSECT)

            add(button_mask, rotation=(0,0,angle), mode=Mode.INTERSECT)
    
result = {
    'ball': trackball,
    'top': top,
    'base': base,
    #'button':button,
    #'button_mask': button_mask,
    #'button_sketch': button_sketch,
    'board': board_location,
    'pizero': pizero,
}
