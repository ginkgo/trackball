from build123d import *

ball = 57.2
bearing = 2.5
wall_thickness = 2

base_width=110

arc_radius=300/2
arc_location=(0,-20,-arc_radius)

def mk_arc_shell(r1, r2):
    loc = Location(arc_location)

    v = Cylinder(r2, base_width, rotation=(0,90,0))

    if r1 > 0:
        v = v - Cylinder(r1, base_width+10, rotation=(0,90,0))
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

pipico = Rotation(90,90,0) * Location((-10.5,0,25.5)) * import_step("Pico-R3.step")
pipico = Locations((0,-40, -35)) * pipico


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

def mk_top():
    part = Part()
    part += mk_arc_shell(0,arc_radius)
    part &= Location((0,30,0)) * Box(base_width, base_width+60, ball+15)
    part -= Sphere(radius=(ball+bearing)/2)
    part -= Cylinder(8,100)
    
    locs = (Rotation(0,0,angle) * Rotation(70,0,0) * Location((0,0,-ball/2-bearing/2))  for angle in range(60,360+60,120))
    part -= [loc * Cylinder(bearing/2, bearing) for loc in locs]

    base_plate = part.faces().sort_by(Axis.Z)[0]
    part = offset(part.solids()[0], amount=-wall_thickness, openings=base_plate)

    fillet_edges = [
        part.edges().sort_by(Axis.Z)[-1],
        part.edges().sort_by(Axis.X)[-3:].sort_by(Axis.Z)[-1],
        part.edges().sort_by(Axis.X)[:3].sort_by(Axis.Z)[-1],
        part.edges().sort_by(Axis.Y)[:4].sort_by(Axis.Z)[-1],
        part.edges().sort_by(Axis.Y)[:4].sort_by(Axis.X)[0],
        part.edges().sort_by(Axis.Y)[:4].sort_by(Axis.X)[-1],
        part.edges().sort_by_distance(Vertex(-1,0,-ball/2))[0],
    ]
    part = chamfer(fillet_edges, wall_thickness )   

    rots = [Rotation(0,0,angle) for angle in range(0,360,90)]
    part -= [r * button_mask for r in rots]

    part -= [l * Cylinder(2,20) for l in [loc1, loc2]]
    return part
top = mk_top()

def mk_button(angle):
    rot = Rotation(0,0,angle)
    
    part = mk_arc_shell(arc_radius - wall_thickness,
                        arc_radius + wall_thickness/2)
    part &= Location((0,0,10)) * extrude(offset(rot * button_sketch,amount=-0.5), amount=-60)

    # part = bounding_box(part)
    # part &= mk_arc_shell(0,arc_radius+wall_thickness/2)
    # part &= Location((0,0,10)) * extrude(offset(rot * button_sketch,amount=-0.5), amount=-60)
        
    edges = part.edges()
    part = chamfer(edges, 0.5)

    rod_width = 5
    rod = Rotation(0,0,45+angle) * Location((ball/2+rod_width/2+4,0,0)) * Box(rod_width, rod_width, 200)
    rod &= mk_arc_shell(0, arc_radius)
    rod &= Box(300,300,50)
    part += rod
    
    return part
buttons = [mk_button(a) for a in range(0,360,90)]

result = {
    'ball': trackball,
    'top': top,
   'board1': board1,
   'board2': board2,
   'pipico': pipico,
}

for i,b in enumerate(buttons):
    result[f'button{i}'] = b

if __name__ == "__main__":

    for k,v in result.items():
        print(k)
        exporter = Mesher()
        exporter.add_shape(v)
        exporter.write(f'{k}.stl')
