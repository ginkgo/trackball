from build123d import *

ball = 57.2    # pool billiards ball
#ball = 52.4   # snooker ball
#ball = 55     # Kensington ball

bearing = 2.5
wall_thickness = 2

base_width=110
base_height=(ball+10)/2

arc_radius=300/2
arc_location=(0,-20,-arc_radius)

def align(xyz):
    d = {'c': Align.CENTER,
         '-': Align.MIN,
         '+': Align.MAX}
    return [d[c] for c in xyz]

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

def mk_top():
    part = Part()
    part += mk_arc_shell(0,arc_radius)
    part &= Pos(0,30,0) * Box(base_width, base_width+60, base_height*2)
    part -= Sphere(radius=(ball+bearing)/2)
    part -= Cylinder(8,100)
    
    locs = (Rotation(0,0,angle) * Rotation(70,0,0) * Pos(0,0,-ball/2-bearing/2)  for angle in range(60,360+60,120))
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
    
    # text = Text("Awesome...", font_size=8, font="Helvetica Neue", font_style=FontStyle.ITALIC, align=Align.MIN)
    # text = Rotation(0,0,180) * Pos(-base_width/2+5,-71,0) * text
    # # f = text.faces()[0]
    # part -= [extrude(f.project_to_shape(part, direction=(0,0,-1)),-0.5, dir=(0,1,1)) for f in text.faces()]
    
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
    
    part += extrude(outer, wall_thickness, dir=(0,0,-1))
    #part += extrude(inner, wall_thickness, dir=(0,0,1)) - top

    # Add front notch in top
    front_edge = top.edges().sort_by(Axis.Y)[-1]
    front_pos = front_edge.center()
    top += (Pos(front_pos) * Box(front_edge.length, 5, 20, align=align('c+-'))) & mk_arc_shell(0,arc_radius - wall_thickness/2)
    
    # Add front notch in bottom
    notch_loc = Pos(0,-5 - 0.5,0) * Pos(front_edge.center())
    notch_width = base_width - wall_thickness * 2.5
    part += notch_loc * Box(notch_width, wall_thickness, 5, align=align('c+-')) & mk_arc_shell(0, arc_radius - wall_thickness - 0.5)

    # Add back notch in bottom
    bottom_edge = top.faces().sort_by(Axis.Y)[0].edges().sort_by(Axis.Z)[0]
    bottom_pos = bottom_edge.center()
    part += Pos(0,wall_thickness+0.5,0) * Pos(bottom_pos) * Box(notch_width,
                                                                wall_thickness,
                                                                wall_thickness,
                                                                align=align('c--'))
    
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
                                 
        
    return part
bottom = mk_bottom()


def mk_sensor_pcb(loc):
    global bottom, top
    board = Pos(2.91,0,0) * Box(34,22,1.55, align=align('cc-')) - Box(18,9,5, align=align('cc-'))

    hole_locations = [Pos(x,y) for x in (-11.09, +13.41) for y in (-8, +8)]
    board -= [l * Cylinder(.8, 10) for l in hole_locations]


    strut=4
    sketch = Polyline([(-2,0,strut-5),
                       (+2,0,strut-5),
                       (+2,0,-5),
                       (-2,0,-5),
                       (-2,0,strut-5)])
    bottom += [extrude(loc * l * make_face(sketch), target=bottom, dir=(0,0,-1)) for l in hole_locations]
    
    sketch = Pos(0,0,-5) * Circle(radius=2)
    bottom += [extrude(loc * l * make_face(sketch), target=bottom, dir=(0,0,-1)) for l in hole_locations]
    
    bottom += [loc * l * Cylinder(2.1,5, align=align('cc+')) for l in hole_locations]
    bottom -= [loc * l * Cylinder(0.9,2, align=align('cc+')) for l in hole_locations]
             
    top -= loc * Cylinder(2,20) 
            
    return loc * board
        
sensor_pcb1 = mk_sensor_pcb(Rotation(0, 45,90) * Pos(0,0,-ball/2 - 3*wall_thickness))
sensor_pcb2 = mk_sensor_pcb(Rotation(0,-45,90) * Pos(0,0,-ball/2 - 3*wall_thickness))

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
pipico = mk_pipico(Pos(0,45, -30))

def mk_button(angle):
    rot = Rotation(0,0,angle)
    
    part = mk_arc_shell(arc_radius - wall_thickness,
                        arc_radius + wall_thickness/2)
    part &= Pos(0,0,10) * extrude(offset(rot * button_sketch,amount=-0.5), amount=-60)

    # part = bounding_box(part)
    # part &= mk_arc_shell(0,arc_radius+wall_thickness/2)
    # part &= Pos(0,0,10) * extrude(offset(rot * button_sketch,amount=-0.5), amount=-60)
        
    edges = part.edges()
    part = chamfer(edges, 0.5)

    rod_width = 5
    rod = Rotation(0,0,45+angle) * Pos(ball/2+rod_width/2+5,0,0) * Box(rod_width, rod_width, 200)
    rod &= mk_arc_shell(0, arc_radius)
    rod &= Box(300,300,40)
    part += rod

    return part
buttons = [mk_button(a) for a in range(0,360,90)]

def mk_button_pcb(pos=Pos(0,0,0), rot=Rotation(0,0,0)):
    global bottom
    
    part = Box(8,30,1.4, align=align('cc-'))
    part += Pos(0,2,1.4) * Box(5.8,12.8,6.5, align=align('cc-'))
    part += Pos(0,0,1.4+6.5) * Box(2.9,1.2,1, align=align('cc-'))

    part -= Pos(0,-12,0) * Cylinder(1,3)
    part -= Pos(0,+12,0) * Cylinder(1,3)
    
    top_loc = part.faces().sort_by(Axis.Z)[-1].center()
    
    loc = pos * Pos(-top_loc) * rot
    for p in [Pos(0,-12,-0.1),
              Pos(0,+12,-0.1)]:
        bottom += (loc * p * Cylinder(3, 30, align=align('cc+'))) & bounding_box(top)
        bottom -= (loc * p * Cylinder(0.9, 3.1, align=align('cc+')))
    
    return loc * part

button_pcbs = []
for i,b in enumerate(buttons):
    p = b.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0].center()
    rot = Rotation(0,0,90) if (i not in [1,2]) else Rotation(0,0,-90)
    button_pcbs.append(mk_button_pcb(pos=Pos(p), rot=rot))

result = {
    'ball': trackball,
    'top': top,
    'bottom': bottom,
    'sensor_pcb1': sensor_pcb1,
    'sensor_pcb2': sensor_pcb2,
    'pipico': pipico,
}

for i,b in enumerate(buttons):
    result[f'button{i}'] = b

for i,b in enumerate(button_pcbs):
    result[f'button_pcb{i}'] = b
    
if __name__ == "__main__":

    for k,v in result.items():
        print(k)
        exporter = Mesher()
        exporter.add_shape(v)
        exporter.write(f'{k}.stl')
